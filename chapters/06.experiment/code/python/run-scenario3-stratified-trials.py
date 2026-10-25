#!/usr/bin/env python3
import csv
from datetime import datetime, timezone
import json
import random
import re
import subprocess
import time

NUM_TRIALS = 30
RANDOM_SEED = 42
TIMEOUT_SECONDS = 300
POLLING_INTERVAL_SECONDS = 4
INITIAL_PROPAGATION_SLEEP = 3
APP_NAMESPACE = "otel-demo"
CHAOS_NAMESPACE = "chaos-mesh"
RESULTS_FILE = "scenario3_diagnostic_trials_stratified.csv"

TARGET_POOL = ["payment", "cart", "shipping", "currency"]
CALL_GRAPH_ORDER = ["frontend", "checkout", "cart", "payment", "shipping", "currency"]

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


def run_cmd(cmd, timeout=15):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def wait_for_workload_recovery():
    for svc in TARGET_POOL:
        run_cmd(f"kubectl rollout status deployment/{svc} -n {APP_NAMESPACE} --timeout=30s 2>/dev/null", timeout=35)


def build_balanced_trial_schedule(num_trials, seed=RANDOM_SEED):
    """
    Stratified, paired, deterministic factorial schedule (identical to Scenarios 4a and 4b):
    10 network-delay, 10 pod-kill, and 10 cpu-stress distributed uniformly across TARGET_POOL.
    """
    rng = random.Random(seed)
    chaos_types = ["network-delay", "pod-kill", "cpu-stress"]
    all_combinations = [(t, c) for c in chaos_types for t in TARGET_POOL]
    schedule = []
    while len(schedule) < num_trials:
        block = list(all_combinations)
        rng.shuffle(block)
        schedule.extend(block)
    schedule = schedule[:num_trials]
    rng.shuffle(schedule)
    return schedule


def is_exact_service_pod(pod_name, labels, service_name):
    pod_lower = pod_name.lower()
    if any(excluded in pod_lower for excluded in ("valkey", "redis", "load-generator", "loadgenerator", "frontend-proxy")):
        return False
    for k in ("app.kubernetes.io/component", "app.kubernetes.io/name", "opentelemetry.io/name", "app"):
        if labels.get(k, "").lower() == service_name:
            return True
    return pod_lower == service_name or pod_lower.startswith(f"{service_name}-")


def resolve_service_pods(service_name):
    res = run_cmd(f"kubectl get pods -n {APP_NAMESPACE} --field-selector=status.phase=Running -o json 2>/dev/null")
    matched_pods = []
    matched_label_key = None
    matched_label_val = None

    if res and res.stdout:
        try:
            data = json.loads(res.stdout)
            for item in data.get("items", []):
                pod_name = item.get("metadata", {}).get("name", "")
                labels = item.get("metadata", {}).get("labels", {})
                if is_exact_service_pod(pod_name, labels, service_name):
                    matched_pods.append(pod_name)
                    for k in ("app.kubernetes.io/name", "app.kubernetes.io/component", "app"):
                        if labels.get(k, "").lower() == service_name:
                            matched_label_key = k
                            matched_label_val = labels[k]
                            break
        except Exception:
            pass

    return matched_pods, matched_label_key, matched_label_val


def generate_chaos_manifest(target_service, chaos_type):
    pods, l_key, l_val = resolve_service_pods(target_service)
    if pods:
        pod_list_yaml = "\n".join([f"        - {p}" for p in pods])
        selector_block = f"""  selector:
    namespaces:
      - {APP_NAMESPACE}
    pods:
      {APP_NAMESPACE}:
{pod_list_yaml}"""
    elif l_key and l_val:
        selector_block = f"""  selector:
    namespaces:
      - {APP_NAMESPACE}
    labelSelectors:
      "{l_key}": "{l_val}\""""
    else:
        selector_block = f"""  selector:
    namespaces:
      - {APP_NAMESPACE}
    labelSelectors:
      app.kubernetes.io/name: {target_service}"""

    if chaos_type == "network-delay":
        return f"""apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: dynamic-network-delay
  namespace: {APP_NAMESPACE}
spec:
  action: delay
  mode: all
{selector_block}
  delay:
    latency: "2000ms"
    jitter: "100ms"
  direction: to
  duration: "180s"
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
{selector_block}
"""
    elif chaos_type == "cpu-stress":
        return f"""apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: dynamic-cpu-stress
  namespace: {APP_NAMESPACE}
spec:
  mode: one
{selector_block}
  stressors:
    cpu:
      workers: 2
      load: 100
  duration: "180s"
"""


def clean_cluster():
    print("  -> Cleaning up previous chaos experiments...", flush=True)
    res = run_cmd(
        f"kubectl delete networkchaos,podchaos,stresschaos --all -n {APP_NAMESPACE} --ignore-not-found --timeout=10s 2>/dev/null",
        timeout=15
    )
    if res is None or res.returncode != 0:
        for kind in ("networkchaos", "podchaos", "stresschaos"):
            rem = run_cmd(f"kubectl get {kind} -n {APP_NAMESPACE} -o jsonpath='{{.items[*].metadata.name}}' 2>/dev/null", timeout=5)
            if rem and rem.stdout.strip():
                for name in rem.stdout.strip().split():
                    run_cmd(
                        f"kubectl patch {kind}/{name} -n {APP_NAMESPACE} --type=merge -p '{{\"metadata\":{{\"finalizers\":[]}}}}' 2>/dev/null",
                        timeout=5
                    )
        run_cmd(
            f"kubectl delete networkchaos,podchaos,stresschaos --all -n {APP_NAMESPACE} --ignore-not-found --timeout=5s 2>/dev/null",
            timeout=10
        )


def inject_chaos_manifest(manifest_path):
    for attempt in range(1, 5):
        res = run_cmd(f"kubectl create -f {manifest_path}", timeout=15)
        if res and res.returncode == 0:
            return True
        err_msg = (res.stderr or "").strip() if res else "timeout"
        print(f"  [WARN] Chaos injection attempt {attempt}/4 failed: {err_msg}", flush=True)
        clean_cluster()
        run_cmd(f"kubectl rollout status deployment/chaos-controller-manager -n {CHAOS_NAMESPACE} --timeout=20s 2>/dev/null", timeout=25)
        time.sleep(3)
    return False


def run_vanilla_rca_agent(t0, t0_iso):
    attempt = 0
    while (time.time() - t0) < TIMEOUT_SECONDS:
        attempt += 1
        elapsed = int(time.time() - t0)
        print(f"      [POLL #{attempt}] Elapsed: {elapsed}s. Scraping pod logs via kubectl...", flush=True)

        for service in CALL_GRAPH_ORDER:
            if (time.time() - t0) >= TIMEOUT_SECONDS:
                return "inconclusive", TIMEOUT_SECONDS

            pods, _, _ = resolve_service_pods(service)
            if not pods:
                continue

            for pod in pods:
                log_res = run_cmd(f"kubectl logs {pod} -n {APP_NAMESPACE} --since-time={t0_iso} 2>/dev/null")
                if not log_res or not log_res.stdout:
                    continue

                for line in log_res.stdout.split("\n"):
                    for sig in ERROR_SIGNATURES:
                        match = sig.search(line)
                        if match:
                            if match.groups():
                                captured = match.group(1).lower()
                                for target in TARGET_POOL:
                                    if target in captured:
                                        return target, time.time() - t0
                            for target in TARGET_POOL:
                                if target in line.lower() and target != service:
                                    return target, time.time() - t0
                            return service, time.time() - t0

        time.sleep(POLLING_INTERVAL_SECONDS)

    return "inconclusive", TIMEOUT_SECONDS


def main():
    print("======================================================================", flush=True)
    print("  EXPERIMENT SCENARIO 3: STRATIFIED BASELINE + DETERMINISTIC RCA", flush=True)
    print("======================================================================", flush=True)

    trial_schedule = build_balanced_trial_schedule(NUM_TRIALS, seed=RANDOM_SEED)

    with open(RESULTS_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "trial_id", "scenario", "chaos_type", "ground_truth",
            "diagnosed_target", "t0_epoch", "mttdiag_seconds",
            "accuracy", "censored"
        ])

        trial = 1
        while trial <= NUM_TRIALS:
            print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting cycle...", flush=True)

            clean_cluster()
            wait_for_workload_recovery()
            print("  -> Waiting for cluster stabilization (20s)...", flush=True)
            time.sleep(20)

            selected_target, selected_chaos = trial_schedule[trial - 1]
            manifest_content = generate_chaos_manifest(selected_target, selected_chaos)

            with open("/tmp/current_chaos.yaml", "w") as m:
                m.write(manifest_content)

            if not inject_chaos_manifest("/tmp/current_chaos.yaml"):
                print(
                    f"  [RETRY-TRIAL] Infrastructure failed to inject chaos before T0 on Trial {trial:02d}. "
                    "Discarding non-injected attempt and repeating trial...",
                    flush=True
                )
                clean_cluster()
                continue

            t0 = time.time()
            t0_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"  -> Fault injected (Stratified): {selected_target} via {selected_chaos}. T0: {t0_iso}", flush=True)

            time.sleep(INITIAL_PROPAGATION_SLEEP)

            print("  -> RCA agent polling via Kubernetes API...", flush=True)
            diagnosed_service, elapsed_time = run_vanilla_rca_agent(t0, t0_iso)

            if elapsed_time >= TIMEOUT_SECONDS or diagnosed_service == "inconclusive":
                final_mttdiag = float(TIMEOUT_SECONDS)
                diagnosed_service = "inconclusive"
                accuracy = 0
                censored = True
                print("  [RESULT] TIMEOUT / INCONCLUSIVE (300.0s). Censored = True.", flush=True)
            else:
                final_mttdiag = round(elapsed_time, 2)
                censored = False
                accuracy = 1 if diagnosed_service == selected_target else 0
                status_str = "SUCCESS (Acc=1)" if accuracy == 1 else "MISATTRIBUTION (Acc=0)"
                print(
                    f"  [RESULT] Converged in {final_mttdiag}s | Diagnosed: {diagnosed_service} "
                    f"| Ground-Truth: {selected_target} -> {status_str}",
                    flush=True
                )

            writer.writerow([
                trial, "vanilla-stratified", selected_chaos, selected_target,
                diagnosed_service, t0_iso, final_mttdiag, accuracy, censored
            ])
            f.flush()
            clean_cluster()
            trial += 1

    print(f"\n[OK] Stratified experiment completed. Results persisted to: {RESULTS_FILE}", flush=True)


if __name__ == "__main__":
    main()
