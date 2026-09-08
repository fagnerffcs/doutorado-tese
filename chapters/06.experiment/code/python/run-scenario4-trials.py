#!/usr/bin/env python3
import csv
from datetime import datetime
import json
import random
import subprocess
import time
import urllib.parse
import urllib.request

# ==============================================================================
# METHODOLOGICAL CONFIGURATION - SCENARIO 4 (PANOPTES / OTel / Tempo)
# Methodology: Wang et al. (ASE 2024) / Barata et al. (Cluster 2026)
# ==============================================================================
NUM_TRIALS = 30
TIMEOUT_SECONDS = 300
POLLING_INTERVAL_SECONDS = 4
APP_NAMESPACE = "otel-demo"
RESULTS_FILE = "scenario4_diagnostic_trials.csv"

TEMPO_ENDPOINT = "http://localhost:3200"

# Target microservice pool in Astronomy Shop checkout flow
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
  run_cmd(
      "kubectl delete networkchaos dynamic-network-delay -n"
      f" {APP_NAMESPACE} 2>/dev/null"
  )


def prime_seen_traces(seen_traces):
  """Pre-fetches anomalous traces during cooldown to prevent false positives.
  
  Makes the RCA agent immune to clock drift between host and Kubernetes VM.
  """
  for target in TARGET_POOL:
    params = urllib.parse.urlencode({
        "tags": f"service.name={target}",
        "minDuration": "1500ms",
        "limit": 20,
    })
    url = f"{TEMPO_ENDPOINT}/api/search?{params}"
    try:
      req = urllib.request.Request(url, headers={"Accept": "application/json"})
      with urllib.request.urlopen(req, timeout=3) as response:
        data = json.loads(response.read().decode())
        for t in data.get("traces", []):
          trace_id = t.get("traceID")
          if trace_id:
            seen_traces.add(trace_id)
    except Exception:
      pass


def check_new_service_latency_anomaly(service_name, seen_traces):
  """Queries Tempo API for new anomalous traces that bypass the seen_traces set."""
  params = urllib.parse.urlencode({
      "tags": f"service.name={service_name}",
      "minDuration": "1500ms",
      "limit": 10,
  })
  url = f"{TEMPO_ENDPOINT}/api/search?{params}"

  try:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=3) as response:
      data = json.loads(response.read().decode())
      traces = data.get("traces", [])

      for t in traces:
        trace_id = t.get("traceID")
        if trace_id and trace_id not in seen_traces:
          # New anomalous trace discovered!
          seen_traces.add(trace_id)
          return True
  except Exception:
    pass

  return False


def run_panoptes_rca_agent(t0, seen_traces):
  """Deterministic RCA agent based on distributed trace traversal (Scenario 4)."""
  while (time.time() - t0) < TIMEOUT_SECONDS:
    for target in TARGET_POOL:
      if (time.time() - t0) >= TIMEOUT_SECONDS:
        return "inconclusive", TIMEOUT_SECONDS

      if check_new_service_latency_anomaly(target, seen_traces):
        t_diag = time.time() - t0
        return target, t_diag

    time.sleep(POLLING_INTERVAL_SECONDS)

  return "inconclusive", TIMEOUT_SECONDS


def main():
  print("======================================================================")
  print("  EXPERIMENT SCENARIO 4: PANOPTES (OTel + Tempo) + DETERMINISTIC RCA")
  print("  Methodology: Wang et al. (ASE 2024) / Barata et al. (Cluster 2026)")
  print("======================================================================")

  # Global state tracker for anomalous traces
  seen_traces = set()

  with open(RESULTS_FILE, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "trial_id",
        "scenario",
        "ground_truth",
        "diagnosed_target",
        "t0_epoch",
        "mttdiag_seconds",
        "accuracy",
        "censored",
    ])

    for trial in range(1, NUM_TRIALS + 1):
      print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting execution cycle...")

      # 1. State Restoration and Cooldown (20s)
      clean_cluster()
      print("  -> Waiting for cluster stabilization (20s)...")
      time.sleep(20)

      # Prime the tracker to ignore lingering slow traces from previous trials
      prime_seen_traces(seen_traces)

      # 2. Randomized Blind Fault Injection Selection
      selected_target = random.choice(TARGET_POOL)
      manifest_content = generate_chaos_manifest(selected_target)

      with open("/tmp/current_chaos.yaml", "w") as m:
        m.write(manifest_content)

      # 3. Fault Injection Execution (T0)
      t0 = time.time()
      t0_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
      run_cmd("kubectl apply -f /tmp/current_chaos.yaml")
      print(
          f"  -> Fault injected blindly ({selected_target} @ 2000ms). T0:"
          f" {t0_iso}"
      )

      # Traffic propagation window (10s)
      time.sleep(10)

      # 4. Correlated Algorithmic Diagnosis via Tempo Trace API
      print("  -> RCA agent querying anomalous traces in Grafana Tempo...")
      diagnosed_service, elapsed_time = run_panoptes_rca_agent(t0, seen_traces)

      # 5. Diagnostic Accuracy Evaluation and Statistical Right-Censoring
      if elapsed_time >= TIMEOUT_SECONDS or diagnosed_service == "inconclusive":
        final_mttdiag = float(TIMEOUT_SECONDS)
        accuracy = 0
        censored = True
        print(
            "  [RESULT] TIMEOUT / INCONCLUSIVE (>= 300s). Diagnostic Failure"
            " (Acc = 0, Censored = True)."
        )
      else:
        final_mttdiag = round(elapsed_time, 2)
        censored = False
        accuracy = 1 if diagnosed_service == selected_target else 0
        status_str = (
            "SUCCESS (Acc=1)" if accuracy == 1 else "MISATTRIBUTION (Acc=0)"
        )
        print(
            f"  [RESULT] Converged in {final_mttdiag}s | Diagnosed:"
            f" {diagnosed_service} | Ground-Truth: {selected_target} ->"
            f" {status_str}"
        )

      # 6. Persistent CSV Logging
      writer.writerow([
          trial,
          "panoptes",
          selected_target,
          diagnosed_service,
          t0_iso,
          final_mttdiag,
          accuracy,
          censored,
      ])
      f.flush()

      # 7. Post-trial cleanup
      clean_cluster()

  print(
      f"\n[OK] Scenario 4 execution completed. Results saved to: {RESULTS_FILE}"
  )


if __name__ == "__main__":
  main()
