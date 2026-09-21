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
import sys

NUM_TRIALS = 30
TIMEOUT_SECONDS = 300
POLLING_INTERVAL_SECONDS = 4
APP_NAMESPACE = "otel-demo"
MONITORING_NAMESPACE = "monitoring"
RESULTS_FILE = "scenario4_diagnostic_trials.csv"

TARGET_POOL = ["payment", "cart", "shipping", "currency"]
SEARCH_POOL = ["frontend", "checkoutservice", "cartservice", "paymentservice", "shippingservice", "currencyservice"]

# --- Static Networking ---
pf_process = None
TEMPO_LOCAL_PORT = 3201
TEMPO_REMOTE_PORT = 3200
tempo_endpoint = f"http://localhost:{TEMPO_LOCAL_PORT}"

def verify_tempo_health():
    print("\n[PRE-FLIGHT] Validating Tempo API and telemetry pipeline...")
    max_retries = 12
    for attempt in range(1, max_retries + 1):
        url = f"{tempo_endpoint}/api/search?tags=service.name=frontend&limit=1"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_data = response.read().decode()
                if not raw_data:
                    print(f"      [WARN] Empty payload. Retrying ({attempt}/{max_retries})...")
                    time.sleep(5)
                    continue
                    
                data = json.loads(raw_data)
                traces = data.get("traces", [])
                if len(traces) > 0:
                    print(f"[PRE-FLIGHT] SUCCESS! Tempo is operational and recording spans.\n")
                    return
                else:
                    print(f"      [WARN] API is alive, but 0 traces found. Is load-generator running? Retrying ({attempt}/{max_retries})...")
        except Exception as e:
            print(f"      [WARN] Connection failed: {e}. Retrying ({attempt}/{max_retries})...")
        
        time.sleep(5)
        
    print("\n[FATAL] Pre-flight check failed! Tempo is not receiving telemetry data.")
    print("Aborting experiment execution to prevent false positives and invalid data.")
    sys.exit(1)

def start_port_forward():
    global pf_process
    subprocess.run("pkill -f 'kubectl port-forward svc/tempo'", shell=True, stderr=subprocess.DEVNULL)
    time.sleep(1)

    print(f"[SETUP] Opening tunnel (Local: {TEMPO_LOCAL_PORT} -> Cluster: {TEMPO_REMOTE_PORT})...")
    err_log = open("/tmp/port_forward_err.log", "w")
    pf_process = subprocess.Popen(
        ["kubectl", "port-forward", "svc/tempo", f"{TEMPO_LOCAL_PORT}:{TEMPO_REMOTE_PORT}", "-n", MONITORING_NAMESPACE],
        stdout=subprocess.DEVNULL,
        stderr=err_log
    )
    time.sleep(3)

def stop_port_forward():
    if pf_process:
        print("\n[TEARDOWN] Closing network tunnel...")
        pf_process.terminate()
        pf_process.wait()

atexit.register(stop_port_forward)
# --------------------------

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

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
      workers: 1
      load: 60
  duration: "180s"
"""

def clean_cluster():
    run_cmd(f"kubectl delete networkchaos dynamic-network-delay -n {APP_NAMESPACE} 2>/dev/null")
    run_cmd(f"kubectl delete podchaos dynamic-pod-kill -n {APP_NAMESPACE} 2>/dev/null")
    run_cmd(f"kubectl delete stresschaos dynamic-cpu-stress -n {APP_NAMESPACE} 2>/dev/null")

def prime_seen_traces(seen_traces):
    for svc in SEARCH_POOL:
        params = urllib.parse.urlencode({"tags": f"service.name={svc}", "minDuration": "800ms", "limit": 10})
        url = f"{tempo_endpoint}/api/search?{params}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                for t in data.get("traces", []):
                    trace_id = t.get("traceID")
                    if trace_id: seen_traces.add(trace_id)
        except Exception:
            pass

def check_new_anomaly(seen_traces):
    for svc in SEARCH_POOL:
        params = urllib.parse.urlencode({"tags": f"service.name={svc}", "minDuration": "800ms", "limit": 5})
        url = f"{tempo_endpoint}/api/search?{params}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                for t in data.get("traces", []):
                    trace_id = t.get("traceID")
                    if trace_id and trace_id not in seen_traces:
                        seen_traces.add(trace_id)
                        return trace_id
        except Exception:
            return None
    return None

def analyze_standard_trace(trace_id):
    url = f"{tempo_endpoint}/api/traces/{trace_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as response:
            trace_json = json.loads(response.read().decode())
    except Exception:
        return None

    error_services = []
    longest_service = "unknown"
    max_duration = 0
    batches = trace_json.get('batches', [])
    if not batches: return None

    for batch in batches:
        service_name = "unknown"
        for attr in batch.get('resource', {}).get('attributes', []):
            if attr.get('key') == 'service.name':
                service_name = attr.get('value', {}).get('stringValue', 'unknown').lower()
        
        for scope_span in batch.get('scopeSpans', []):
            for span in scope_span.get('spans', []):
                start = int(span.get('startTimeUnixNano', 0))
                end = int(span.get('endTimeUnixNano', 0))
                duration = (end - start) / 1e6
                
                status_code = span.get('status', {}).get('code')
                if status_code == 2 or status_code == 'STATUS_CODE_ERROR':
                    error_services.append(service_name)
                
                if duration > max_duration:
                    max_duration = duration
                    longest_service = service_name

    if error_services:
        culprit = error_services[-1]
        for t in TARGET_POOL:
            if t in culprit: return t
        return culprit

    if max_duration > 1000:
        for t in TARGET_POOL:
            if t in longest_service: return t
        return longest_service

    return "unknown-service"

def run_standard_rca_agent(t0, seen_traces):
    attempt = 0
    while (time.time() - t0) < TIMEOUT_SECONDS:
        attempt += 1
        elapsed = int(time.time() - t0)
        print(f"      [POLL #{attempt}] Elapsed: {elapsed}s. Scanning Tempo for anomalies...", end="\r", flush=True)
        
        if (time.time() - t0) >= TIMEOUT_SECONDS:
            return "inconclusive", TIMEOUT_SECONDS

        trace_id = check_new_anomaly(seen_traces)
        if trace_id:
            print(f"\n      [DEBUG] Found anomalous trace ID: {trace_id}. Analyzing (Standard RCA)...")
            culprit = analyze_standard_trace(trace_id)
            if culprit:
                return culprit, time.time() - t0
                
        time.sleep(POLLING_INTERVAL_SECONDS)
    return "inconclusive", TIMEOUT_SECONDS

def main():
    print("======================================================================")
    print("  EXPERIMENT SCENARIO 4a: STANDARD DISTRIBUTED TRACING RCA")
    print("======================================================================")

    start_port_forward()
    verify_tempo_health()
    seen_traces = set()
    
    with open(RESULTS_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["trial_id", "scenario", "chaos_type", "ground_truth", "diagnosed_target", "t0_epoch", "mttdiag_seconds", "accuracy", "censored"])

        for trial in range(1, NUM_TRIALS + 1):
            print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting execution cycle...")
            clean_cluster()
            print("  -> Waiting for cluster stabilization (20s)...")
            time.sleep(20)
            prime_seen_traces(seen_traces)

            selected_target = random.choice(TARGET_POOL)
            selected_chaos = random.choice(["network-delay", "pod-kill", "cpu-stress"])
            manifest_content = generate_chaos_manifest(selected_target, selected_chaos)

            with open("/tmp/current_chaos.yaml", "w") as m:
                m.write(manifest_content)

            t0 = time.time()
            t0_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            run_cmd("kubectl apply -f /tmp/current_chaos.yaml")
            print(f"  -> Fault injected blindly ({selected_target} via {selected_chaos}). T0: {t0_iso}")

            time.sleep(10)
            diagnosed_service, elapsed_time = run_standard_rca_agent(t0, seen_traces)

            if elapsed_time >= TIMEOUT_SECONDS or diagnosed_service == "inconclusive":
                final_mttdiag = float(TIMEOUT_SECONDS)
                accuracy = 0
                censored = True
                print("  [RESULT] TIMEOUT / INCONCLUSIVE. Diagnostic Failure.")
            else:
                final_mttdiag = round(elapsed_time, 2)
                censored = False
                accuracy = 1 if diagnosed_service == selected_target else 0
                status_str = "SUCCESS (Acc=1)" if accuracy == 1 else "MISATTRIBUTION (Acc=0)"
                print(f"  [RESULT] Converged in {final_mttdiag}s | Diagnosed: {diagnosed_service} | Ground-Truth: {selected_target} -> {status_str}")

            writer.writerow([trial, "panoptes-standard", selected_chaos, selected_target, diagnosed_service, t0_iso, final_mttdiag, accuracy, censored])
            f.flush()
            clean_cluster()

    print(f"\n[OK] Scenario 4a execution completed. Results saved to: {RESULTS_FILE}")

if __name__ == "__main__":
    main()
