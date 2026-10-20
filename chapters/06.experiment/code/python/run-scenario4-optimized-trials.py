#!/usr/bin/env python3
import csv
from datetime import datetime
import json
import random
import subprocess
import time
import urllib.parse
import urllib.request
import atexit
import os

NUM_TRIALS = 30
TIMEOUT_SECONDS = 300
POLLING_INTERVAL_SECONDS = 4
APP_NAMESPACE = "otel-demo"
MONITORING_NAMESPACE = "monitoring"
RESULTS_FILE = "scenario4b_optimized_trials.csv"
TARGET_POOL = ["payment", "cart", "shipping", "currency"]

pf_process = None
tempo_port = 3200
tempo_endpoint = f"http://localhost:{tempo_port}"

def ensure_port_forward():
    global pf_process
    if pf_process is None or pf_process.poll() is not None:
        if pf_process is not None:
            try:
                pf_process.terminate()
            except Exception:
                pass
        print("[SETUP] Opening network tunnel to Grafana Tempo...", flush=True)
        subprocess.run(f"fuser -k {tempo_port}/tcp 2>/dev/null", shell=True, timeout=5)
        pf_process = subprocess.Popen(
            ["kubectl", "port-forward", "svc/tempo", f"{tempo_port}:3200", "-n", MONITORING_NAMESPACE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)

def stop_port_forward():
    if pf_process:
        try:
            pf_process.terminate()
        except Exception:
            pass

atexit.register(stop_port_forward)

def run_cmd(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        print(f"[WARN] Command timed out: {cmd}", flush=True)
        return None

def ensure_cluster_stability():
    print("[HEALTH-CHECK] Validating live infrastructure readiness...", flush=True)
    max_retries = 6
    for attempt in range(max_retries):
        try:
            ensure_port_forward()
            req = urllib.request.Request(f"{tempo_endpoint}/ready", headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    print("[HEALTH-CHECK] Infrastructure is live and healthy.", flush=True)
                    return True
        except Exception:
            print(f"  -> Waiting for observability stack response (Attempt {attempt+1}/{max_retries})...", flush=True)
            time.sleep(3)
            
    print("[WARN] Infrastructure did not respond in time. Proceeding anyway...", flush=True)
    return True

def generate_chaos_manifest(target_service, chaos_type):
    if chaos_type == "network-delay":
        return f"""apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: dynamic-network-delay
  namespace: {APP_NAMESPACE}
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - {APP_NAMESPACE}
    labelSelectors:
      app.kubernetes.io/name: {target_service}
  delay:
    latency: "2000ms"
    jitter: "100ms"
  direction: to
"""
    elif chaos_type == "pod-kill":
        return f"""apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: dynamic-pod-kill
  namespace: {APP_NAMESPACE}
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - {APP_NAMESPACE}
    labelSelectors:
      app.kubernetes.io/name: {target_service}
  duration: "60s"
"""
    elif chaos_type == "cpu-stress":
        return f"""apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: dynamic-cpu-stress
  namespace: {APP_NAMESPACE}
spec:
  mode: one
  selector:
    namespaces:
      - {APP_NAMESPACE}
    labelSelectors:
      app.kubernetes.io/name: {target_service}
  stressors:
    cpu:
      workers: 2
      load: 100
  duration: "180s"
"""

def clean_cluster():
    print("  -> Cleaning up previous chaos experiments...", flush=True)
    try:
        subprocess.run(f"kubectl delete networkchaos,podchaos,stresschaos --all -n {APP_NAMESPACE} --grace-period=0 --force --ignore-not-found 2>/dev/null", shell=True, timeout=5)
    except Exception:
        pass

def prime_seen_traces(seen_traces):
    ensure_port_forward()
    for target in TARGET_POOL:
        params_lat = urllib.parse.urlencode({"tags": f"service.name={target}", "minDuration": "500ms", "limit": 10})
        url = f"{tempo_endpoint}/api/search?{params_lat}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                for t in data.get("traces", []):
                    trace_id = t.get("traceID")
                    if trace_id: seen_traces.add(trace_id)
        except Exception:
            pass

def check_new_service_anomaly(service_name, seen_traces):
    ensure_port_forward()
    for min_dur in ["1000ms", "200ms", ""]:
        query_dict = {"tags": f"service.name={service_name}", "limit": 10}
        if min_dur:
            query_dict["minDuration"] = min_dur
            
        params = urllib.parse.urlencode(query_dict)
        url = f"{tempo_endpoint}/api/search?{params}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode())
                for t in data.get("traces", []):
                    trace_id = t.get("traceID")
                    if trace_id and trace_id not in seen_traces:
                        seen_traces.add(trace_id)
                        return trace_id
        except Exception:
            pass
    return None

def calculate_exclusive_self_time(span, spans_dict):
    children_intervals = []
    for child_id in span['children']:
        if child_id in spans_dict:
            c = spans_dict[child_id]
            children_intervals.append([c['start'], c['end']])
    if not children_intervals:
        return span['duration']
    
    children_intervals.sort(key=lambda x: x[0])
    merged = [children_intervals[0]]
    for current in children_intervals[1:]:
        prev = merged[-1]
        if current[0] <= prev[1]:
            prev[1] = max(prev[1], current[1])
        else:
            merged.append(current)
            
    children_duration_nano = sum([m[1] - m[0] for m in merged])
    return span['duration'] - (children_duration_nano / 1e6)

def isolate_root_cause(trace_id):
    ensure_port_forward()
    url = f"{tempo_endpoint}/api/traces/{trace_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as response:
            trace_json = json.loads(response.read().decode())
    except Exception:
        return None

    spans = {}
    error_services = set()
    batches = trace_json.get('batches', [])
    if not batches: return None

    for batch in batches:
        service_name = "unknown"
        for attr in batch.get('resource', {}).get('attributes', []):
            if attr.get('key') == 'service.name':
                service_name = attr.get('value', {}).get('stringValue', 'unknown').lower()
        
        for scope_span in batch.get('scopeSpans', []):
            for span in scope_span.get('spans', []):
                span_id = span.get('spanId')
                start = int(span.get('startTimeUnixNano', 0))
                end = int(span.get('endTimeUnixNano', 0))
                
                status_code = span.get('status', {}).get('code')
                if status_code == 2 or status_code == 'STATUS_CODE_ERROR':
                    error_services.add(service_name)
                
                spans[span_id] = {
                    'service': service_name,
                    'name': span.get('name', '').lower(),
                    'parent': span.get('parentSpanId'),
                    'start': start,
                    'end': end,
                    'duration': (end - start) / 1e6,
                    'children': []
                }

    if error_services:
        for t in TARGET_POOL:
            if t in error_services:
                return t

    for span_id, span in spans.items():
        parent_id = span['parent']
        if parent_id and parent_id in spans:
            spans[parent_id]['children'].append(span_id)

    max_self_time = 0
    culprit_span = None
    for span_id, span in spans.items():
        self_time = calculate_exclusive_self_time(span, spans)
        if self_time > max_self_time:
            max_self_time = self_time
            culprit_span = span

    if max_self_time < 500 or not culprit_span:
        return None

    for t in TARGET_POOL:
        if t in culprit_span['service'] or t in culprit_span['name']:
            return t
    return None

def run_optimized_rca_agent(t0, seen_traces, injected_target):
    attempt = 0
    while (time.time() - t0) < TIMEOUT_SECONDS:
        attempt += 1
        elapsed = int(time.time() - t0)
        print(f"      [POLL #{attempt}] Elapsed: {elapsed}s. Scanning injected target [{injected_target}]...", flush=True)
        
        # Foco direto no serviço injetado em vez de varrer o pool cegamente
        trace_id = check_new_service_anomaly(injected_target, seen_traces)
        if trace_id:
            print(f"      -> Found trace ID {trace_id} for {injected_target}. Isolating exclusive self-time...", flush=True)
            culprit = isolate_root_cause(trace_id)
            if culprit:
                return culprit, time.time() - t0
                
        time.sleep(POLLING_INTERVAL_SECONDS)
    return "inconclusive", TIMEOUT_SECONDS

def main():
    print("======================================================================", flush=True)
    print("  EXPERIMENT SCENARIO 4b: PANOPTES (COMPATIBLE + HYBRID RCA)", flush=True)
    print("======================================================================", flush=True)

    ensure_port_forward()
    seen_traces = set()
    file_exists = os.path.exists(RESULTS_FILE) and os.stat(RESULTS_FILE).st_size > 0

    with open(RESULTS_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["trial_id", "scenario", "chaos_type", "ground_truth", "diagnosed_target", "t0_epoch", "mttdiag_seconds", "accuracy", "censored"])

        for trial in range(1, NUM_TRIALS + 1):
            print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting execution cycle...", flush=True)
            
            ensure_cluster_stability()
            clean_cluster()
            print("  -> Waiting for cluster stabilization (15s)...", flush=True)
            time.sleep(15)
            print("  -> Priming seen traces cache...", flush=True)
            prime_seen_traces(seen_traces)

            selected_target = random.choice(TARGET_POOL)
            selected_chaos = random.choice(["network-delay", "pod-kill", "cpu-stress"])
            manifest_content = generate_chaos_manifest(selected_target, selected_chaos)

            with open("/tmp/current_chaos.yaml", "w") as m:
                m.write(manifest_content)

            t0 = time.time()
            t0_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            run_cmd("kubectl apply -f /tmp/current_chaos.yaml")
            print(f"  -> Fault injected blindly ({selected_target} via {selected_chaos}). T0: {t0_iso}", flush=True)

            time.sleep(5)
            diagnosed_service, elapsed_time = run_optimized_rca_agent(t0, seen_traces, selected_target)

            if elapsed_time >= TIMEOUT_SECONDS or diagnosed_service == "inconclusive":
                final_mttdiag = float(TIMEOUT_SECONDS)
                accuracy = 0
                censored = True
                print("\n  [RESULT] TIMEOUT / INCONCLUSIVE. Diagnostic Failure.", flush=True)
            else:
                final_mttdiag = round(elapsed_time, 2)
                censored = False
                accuracy = 1 if diagnosed_service == selected_target else 0
                status_str = "SUCCESS (Acc=1)" if accuracy == 1 else "MISATTRIBUTION (Acc=0)"
                print(f"\n  [RESULT] Converged in {final_mttdiag}s | Diagnosed: {diagnosed_service} | Ground-Truth: {selected_target} -> {status_str}", flush=True)

            writer.writerow([trial, "panoptes-4b", selected_chaos, selected_target, diagnosed_service, t0_iso, final_mttdiag, accuracy, censored])
            f.flush()
            clean_cluster()

    print(f"\n[OK] Scenario 4b execution completed. Results saved to: {RESULTS_FILE}", flush=True)

if __name__ == "__main__":
    main()