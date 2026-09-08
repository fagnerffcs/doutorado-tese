#!/usr/bin/env python3
import time
import random
import subprocess
import csv
import json
import re
from datetime import datetime

# ==============================================================================
# METHODOLOGICAL CONFIGURATION (Wang et al., 2024 / Barata et al., 2026)
# ==============================================================================
NUM_TRIALS = 30
TIMEOUT_SECONDS = 300
POLLING_INTERVAL_SECONDS = 5
APP_NAMESPACE = "otel-demo"
RESULTS_FILE = "scenario3_diagnostic_trials.csv"

# Critical microservice target pool in Astronomy Shop checkout flow
TARGET_POOL = ["payment", "cart", "shipping", "currency"]

# Breadth-first search (BFS) dependency topology starting from frontend
CALL_GRAPH_ORDER = ["frontend", "checkout", "cart", "payment", "shipping", "currency"]

# Calibrated regex signatures based on Astronomy Shop failure output
ERROR_SIGNATURES = [
    re.compile(r"failed POST to (\w+)", re.IGNORECASE),
    re.compile(r"Post \"http://(\w+)", re.IGNORECASE),
    re.compile(r"Failed to call (\w+) service", re.IGNORECASE),
    re.compile(r"context deadline exceeded", re.IGNORECASE),
    re.compile(r"rpc error: code = (?:Unavailable|DeadlineExceeded|Internal)", re.IGNORECASE),
    re.compile(r"Timeout while waiting for response", re.IGNORECASE),
    re.compile(r"HTTP (?:status )?5\d{2}", re.IGNORECASE),
    re.compile(r"connection refused", re.IGNORECASE),
    re.compile(r"failed to charge card", re.IGNORECASE),
    re.compile(r"deadline_exceeded", re.IGNORECASE)
]

def run_cmd(cmd):
    """Executes shell command capturing stdout and stderr."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def generate_chaos_manifest(target_service, chaos_type):
    """Declaratively generates Chaos Mesh manifest based on selected chaos type and target."""
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
    """Ensures clean removal of any existing chaos injection resources of all types."""
    run_cmd(f"kubectl delete networkchaos dynamic-network-delay -n {APP_NAMESPACE} 2>/dev/null")
    run_cmd(f"kubectl delete podchaos dynamic-pod-kill -n {APP_NAMESPACE} 2>/dev/null")
    run_cmd(f"kubectl delete stresschaos dynamic-cpu-stress -n {APP_NAMESPACE} 2>/dev/null")

def run_vanilla_rca_agent(t0, t0_iso):
    """
    Emulates deterministic RCA agent in Vanilla scenario (Wang et al., 2024):
    Performs continuous polling via native Kubernetes API (kubectl logs and top)
    along the call chain until converging on the culprit or reaching 300s.
    Strictly uses --since-time to eliminate stale logs from preceding trials.
    """
    while (time.time() - t0) < TIMEOUT_SECONDS:
        for service in CALL_GRAPH_ORDER:
            if (time.time() - t0) >= TIMEOUT_SECONDS:
                return "inconclusive", TIMEOUT_SECONDS

            # Query active service pods via API Server
            pod_cmd = f"kubectl get pods -n {APP_NAMESPACE} -l app.kubernetes.io/name={service} -o jsonpath='{{.items[*].metadata.name}}'"
            pods = run_cmd(pod_cmd).stdout.strip().split()

            if not pods:
                continue

            # Inspect logs emitted strictly after current trial injection T0
            for pod in pods:
                log_cmd = f"kubectl logs {pod} -n {APP_NAMESPACE} --since-time={t0_iso}"
                logs = run_cmd(log_cmd).stdout

                for line in logs.split('\n'):
                    for sig in ERROR_SIGNATURES:
                        match = sig.search(line)
                        if match:
                            # If regex explicitly captured downstream service name via capture group
                            if match.groups():
                                captured = match.group(1).lower()
                                for target in TARGET_POOL:
                                    if target in captured:
                                        t_diag = time.time() - t0
                                        return target, t_diag

                            # If log line textually references a downstream service from TARGET_POOL
                            for target in TARGET_POOL:
                                if target in line.lower() and target != service:
                                    t_diag = time.time() - t0
                                    return target, t_diag

                            # Otherwise attribute fault to the service emitting the error log
                            t_diag = time.time() - t0
                            return service, t_diag

            # Emulate resource inspection overhead via native metrics-server polling
            _ = run_cmd(f"kubectl top pods -n {APP_NAMESPACE} --no-headers")

        time.sleep(POLLING_INTERVAL_SECONDS)

    return "inconclusive", TIMEOUT_SECONDS

def main():
    print("======================================================================")
    print("  EXPERIMENT SCENARIO 3: VANILLA BASELINE + DETERMINISTIC RCA")
    print("  Methodology: Wang et al. (ASE 2024) / Barata et al. (Cluster 2026)")
    print("======================================================================")

    with open(RESULTS_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["trial_id", "scenario", "chaos_type", "ground_truth", "diagnosed_target", 
                         "t0_epoch", "mttdiag_seconds", "accuracy", "censored"])

        for trial in range(1, NUM_TRIALS + 1):
            print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting cycle...")

            # 1. Cluster State Restoration and Cooldown (20s)
            clean_cluster()
            print("  -> Waiting for cluster stabilization (20s)...")
            time.sleep(20)

            # 2. Randomized Blind Fault Injection Selection (Microservice and Chaos Type)
            selected_target = random.choice(TARGET_POOL)
            selected_chaos = random.choice(["network-delay", "pod-kill", "cpu-stress"])
            manifest_content = generate_chaos_manifest(selected_target, selected_chaos)

            with open("/tmp/current_chaos.yaml", "w") as m:
                m.write(manifest_content)

            # 3. Injection Execution and Authoritative T0 Capture
            t0 = time.time()
            t0_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            run_cmd("kubectl apply -f /tmp/current_chaos.yaml")
            print(f"  -> Fault injected blindly ({selected_target} via {selected_chaos}). T0: {t0_iso}")

            # Traffic propagation delay (10s)
            time.sleep(10)

            # 4. Active RCA Agent Polling with Strict Temporal Isolation
            print("  -> RCA agent polling via Kubernetes API...")
            diagnosed_service, elapsed_time = run_vanilla_rca_agent(t0, t0_iso)

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
            writer.writerow([trial, "vanilla", selected_chaos, selected_target, diagnosed_service, 
                             t0_iso, final_mttdiag, accuracy, censored])
            f.flush()

            # 7. Post-trial teardown
            clean_cluster()

    print(f"\n[OK] Experiment completed. Results persisted to: {RESULTS_FILE}")

if __name__ == "__main__":
    main()