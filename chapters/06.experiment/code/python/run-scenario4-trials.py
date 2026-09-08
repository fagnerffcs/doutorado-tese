#!/usr/bin/env python3
import time
import random
import subprocess
import csv
import json
import urllib.request
import urllib.parse
from datetime import datetime

# ==============================================================================
# METHODOLOGICAL CONFIGURATION - SCENARIO 4 (PANOPTES / OTel / Tempo / Prometheus)
# Methodology: Wang et al. (ASE 2024) / Barata et al. (Cluster 2026)
# ==============================================================================
NUM_TRIALS = 30
TIMEOUT_SECONDS = 300
POLLING_INTERVAL_SECONDS = 3
APP_NAMESPACE = "otel-demo"
RESULTS_FILE = "scenario4_diagnostic_trials.csv"

# Observability API endpoints in the cluster (PANOPTES Stack)
TEMPO_ENDPOINT = "http://localhost:3200"
PROMETHEUS_ENDPOINT = "http://localhost:9090"

# Critical microservice target pool in Astronomy Shop checkout flow
TARGET_POOL = ["payment", "cart", "shipping", "currency"]

def run_cmd(cmd):
    """Executes shell command capturing stdout and stderr."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def generate_chaos_manifest(target_service):
    """Declaratively generates Chaos Mesh manifest for the selected target."""
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

def clean_cluster():
    """Ensures clean removal of any existing chaos injection resource."""
    run_cmd(f"kubectl delete networkchaos dynamic-network-delay -n {APP_NAMESPACE} 2>/dev/null")

def query_tempo_traces(t0_unix):
    """
    Queries Tempo API searching for frontend traces with duration >= 1500ms after T0.
    """
    try:
        params = urllib.parse.urlencode({
            "service.name": "frontend",
            "minDuration": "1500ms",
            "start": str(int(t0_unix)),
            "limit": 5
        })
        url = f"{TEMPO_ENDPOINT}/api/search?{params}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            return data.get("traces", [])
    except Exception:
        return []

def analyze_trace_root_cause(trace_id):
    """
    Traverses the distributed trace tree and isolates the microservice with highest self-time.
    """
    try:
        url = f"{TEMPO_ENDPOINT}/api/traces/{trace_id}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as response:
            trace_data = json.loads(response.read().decode())

        max_duration = 0
        culprit_service = None

        batches = trace_data.get("batches", [])
        for batch in batches:
            svc_name = "unknown"
            for attr in batch.get("resource", {}).get("attributes", []):
                if attr.get("key") == "service.name":
                    svc_name = attr.get("value", {}).get("stringValue", "")

            for scope_span in batch.get("scopeSpans", []):
                for span in scope_span.get("spans", []):
                    start = int(span.get("startTimeUnixNano", 0))
                    end = int(span.get("endTimeUnixNano", 0))
                    duration_ms = (end - start) / 1e6

                    # Evaluates whether the span retained the bulk of the 2000ms network delay
                    if duration_ms >= 1800 and duration_ms > max_duration:
                        max_duration = duration_ms
                        for target in TARGET_POOL:
                            if target in svc_name.lower():
                                culprit_service = target

        return culprit_service
    except Exception:
        return None

def run_panoptes_rca_agent(t0):
    """
    Deterministic RCA agent based on unified telemetry (Scenario 4).
    Performs active polling on trace backend until identifying anomalous root span or hitting 300s.
    """
    t0_unix = t0

    while (time.time() - t0) < TIMEOUT_SECONDS:
        traces = query_tempo_traces(t0_unix)
        
        if traces:
            for t in traces:
                trace_id = t.get("traceID")
                suspected_target = analyze_trace_root_cause(trace_id)
                if suspected_target:
                    t_diag = time.time() - t0
                    return suspected_target, t_diag

        time.sleep(POLLING_INTERVAL_SECONDS)

    return "inconclusive", TIMEOUT_SECONDS

def main():
    print("======================================================================")
    print("  EXPERIMENT SCENARIO 4: PANOPTES (OTel + Tempo) + DETERMINISTIC RCA")
    print("  Methodology: Wang et al. (ASE 2024) / Barata et al. (Cluster 2026)")
    print("======================================================================")

    with open(RESULTS_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["trial_id", "scenario", "ground_truth", "diagnosed_target", 
                         "t0_epoch", "mttdiag_seconds", "accuracy", "censored"])

        for trial in range(1, NUM_TRIALS + 1):
            print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting cycle...")

            # 1. Cluster State Restoration and Cooldown (20s)
            clean_cluster()
            print("  -> Waiting for cluster stabilization (20s)...")
            time.sleep(20)

            # 2. Randomized Blind Fault Injection Selection
            selected_target = random.choice(TARGET_POOL)
            manifest_content = generate_chaos_manifest(selected_target)

            with open("/tmp/current_chaos.yaml", "w") as m:
                m.write(manifest_content)

            # 3. Injection Execution and Authoritative T0 Capture
            t0 = time.time()
            t0_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            run_cmd("kubectl apply -f /tmp/current_chaos.yaml")
            print(f"  -> Fault injected blindly ({selected_target} @ 2000ms). T0: {t0_iso}")

            # Traffic propagation delay (10s)
            time.sleep(10)

            # 4. Correlated Algorithmic Diagnosis via Distributed Trace API
            print("  -> RCA agent inspecting anomalous traces in Grafana Tempo...")
            diagnosed_service, elapsed_time = run_panoptes_rca_agent(t0)

            # 5. Diagnostic Accuracy Evaluation and Statistical Right-Censoring
            if elapsed_time >= TIMEOUT_SECONDS or diagnosed_service == "inconclusive":
                final_mttdiag = float(TIMEOUT_SECONDS)
                accuracy = 0
                censored = True
                print(f"  [RESULT] TIMEOUT / INCONCLUSIVE (>= {TIMEOUT_SECONDS}s). Diagnostic Failure (Acc = 0, Censored = True).")
            else:
                final_mttdiag = round(elapsed_time, 2)
                censored = False
                accuracy = 1 if diagnosed_service == selected_target else 0
                status_str = "SUCCESS (Acc=1)" if accuracy == 1 else "MISATTRIBUTION (Acc=0)"
                print(f"  [RESULT] Converged in {final_mttdiag}s | Diagnosed: {diagnosed_service} | Ground-Truth: {selected_target} -> {status_str}")

            # 6. Persistent CSV Logging
            writer.writerow([trial, "panoptes", selected_target, diagnosed_service, 
                             t0_iso, final_mttdiag, accuracy, censored])
            f.flush()

            # 7. Post-trial teardown
            clean_cluster()

    print(f"\n[OK] Scenario 4 execution completed. Results persisted to: {RESULTS_FILE}")

if __name__ == "__main__":
    main()