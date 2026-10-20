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
SEARCH_POOL = ["frontend", "checkout", "cart", "payment", "shipping", "currency"]

# --- Self-Healing Networking ---
pf_process = None
tempo_port = 3200
tempo_endpoint = f"http://localhost:{tempo_port}"

def ensure_port_forward():
    global pf_process
    if pf_process is None or pf_process.poll() is not None:
        if pf_process is not None:
            print("\n[WARN] Port-forward tunnel dropped. Re-establishing...")
            try:
                pf_process.terminate()
            except Exception:
                pass
        else:
            print(f"[SETUP] Opening network tunnel to Grafana Tempo on port {tempo_port}...")
        
        subprocess.run(f"fuser -k {tempo_port}/tcp 2>/dev/null", shell=True)
        pf_process = subprocess.Popen(
            ["kubectl", "port-forward", "svc/tempo", f"{tempo_port}:3200", "-n", MONITORING_NAMESPACE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)

def stop_port_forward():
    if pf_process:
        print("\n[TEARDOWN] Closing network tunnel...")
        pf_process.terminate()

atexit.register(stop_port_forward)

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def ensure_cluster_stability():
    """
    Check cluster health non-intrusive.
    Only acts if essential pods are in state NotReady or CrashLoop.
    """
    print("[HEALTH-CHECK] Validating live infrastructure readiness...")
    max_retries = 6 
    for attempt in range(max_retries):
        try:
            ensure_port_forward()
            res = subprocess.run(
                ["kubectl", "get", "pods", "-n", MONITORING_NAMESPACE, "-o", "json"],
                capture_output=True, text=True, check=True
            )
            pods = json.loads(res.stdout)["items"]
            
            unhealthy = False
            for pod in pods:
                name = pod["metadata"]["name"]
                if "tempo" in name or "prometheus-kube-prometheus-stack-prometheus" in name:
                    statuses = pod.get("status", {}).get("containerStatuses", [])
                    for cs in statuses:
                        if not cs.get("ready", False):
                            print(f"[WARN] Critical pod {name} is not ready yet.")
                            unhealthy = True
            
            if unhealthy:
                raise Exception("Critical monitoring pods are not ready.")
            
            req = urllib.request.Request(f"{tempo_endpoint}/ready", headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    print("[HEALTH-CHECK] Infrastructure is live and healthy.")
                    return True
        except Exception:
            print(f"  -> Waiting for observability stack response (Attempt {attempt+1}/{max_retries})...")
            if attempt == 2:
                print("[RECOVERY] Restarting Tempo and Prometheus due to unresponsiveness...")
                subprocess.run("kubectl rollout restart statefulset/tempo -n monitoring", shell=True)
                subprocess.run("kubectl rollout restart statefulset/prometheus-kube-prometheus-stack-prometheus -n monitoring", shell=True)
            time.sleep(5)
            
    print("[FATAL] Infrastructure did not recover in time. Marking trial as censored.")
    return False

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
    run_cmd(f"kubectl delete networkchaos dynamic-network-delay -n {APP_NAMESPACE} 2>/dev/null")
    run_cmd(f"kubectl delete podchaos dynamic-pod-kill -n {APP_NAMESPACE} 2>/dev/null")
    run_cmd(f"kubectl delete stresschaos dynamic-cpu-stress -n {APP_NAMESPACE} 2>/dev/null")

def prime_seen_traces(seen_traces):
    ensure_port_forward()
    for svc in SEARCH_POOL:
        queries = [
            {"tags": f"service.name={svc}", "minDuration": "1000ms", "limit": 10},
            {"tags": f"service.name={svc} error=true", "limit": 10},
            {"tags": f"service.name={svc} status=error", "limit": 10}
        ]
        for q in queries:
            params = urllib.parse.urlencode(q)
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
    ensure_port_forward()
    for attempt_delay in [1, 2, 4]:
        for svc in SEARCH_POOL:
            queries = [
                {"tags": f"service.name={svc}", "minDuration": "1000ms", "limit": 5},
                {"tags": f"service.name={svc} error=true", "limit": 5},
                {"tags": f"service.name={svc} status=error", "limit": 5}
            ]
            for q in queries:
                params = urllib.parse.urlencode(q)
                url = f"{tempo_endpoint}/api/search?{params}"
                try:
                    req = urllib.request.Request(url, headers={"Accept": "application/json"})
                    with urllib.request.urlopen(req, timeout=6) as response:
                        data = json.loads(response.read().decode())
                        for t in data.get("traces", []):
                            trace_id = t.get("traceID")
                            if trace_id and trace_id not in seen_traces:
                                seen_traces.add(trace_id)
                                return trace_id
                except Exception:
                    time.sleep(0.5)
        time.sleep(attempt_delay)
    
    global pf_process
    if pf_process:
        pf_process.terminate()
        pf_process = None
    ensure_port_forward()
    return None

def analyze_standard_trace(trace_id):
    ensure_port_forward()
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

    ensure_port_forward()

    seen_traces = set()
    with open(RESULTS_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["trial_id", "scenario", "chaos_type", "ground_truth", "diagnosed_target", "t0_epoch", "mttdiag_seconds", "accuracy", "censored"])

        for trial in range(1, NUM_TRIALS + 1):
            print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting execution cycle...")
            
            ensure_cluster_stability()
            
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