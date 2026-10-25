#!/usr/bin/env python3
import atexit
import csv
from datetime import datetime, timezone
import json
import random
import subprocess
import time
import urllib.parse
import urllib.request

NUM_TRIALS = 30
RANDOM_SEED = 42
TIMEOUT_SECONDS = 300
POLLING_INTERVAL_SECONDS = 4
INITIAL_PROPAGATION_SLEEP = 3
APP_NAMESPACE = "otel-demo"
MONITORING_NAMESPACE = "monitoring"
CHAOS_NAMESPACE = "chaos-mesh"
RESULTS_FILE = "scenario4_diagnostic_trials.csv"

TARGET_POOL = ["payment", "cart", "shipping", "currency"]
SEARCH_POOL = ["frontend", "checkout", "payment", "cart", "shipping", "currency"]

# --- Self-Healing Networking ---
pf_process = None
tempo_port = 3200
tempo_endpoint = f"http://localhost:{tempo_port}"


def run_cmd(cmd, timeout=15):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def ensure_port_forward(force_restart=False):
    global pf_process
    if force_restart and pf_process is not None:
        try:
            pf_process.terminate()
        except Exception:
            pass
        pf_process = None

    if pf_process is None or pf_process.poll() is not None:
        if pf_process is not None:
            print("\n[WARN] Port-forward tunnel dropped. Re-establishing...", flush=True)
            try:
                pf_process.terminate()
            except Exception:
                pass
        else:
            print(f"[SETUP] Opening network tunnel to Grafana Tempo on port {tempo_port}...", flush=True)

        subprocess.run(f"fuser -k {tempo_port}/tcp 2>/dev/null", shell=True, timeout=5)
        pf_process = subprocess.Popen(
            ["kubectl", "port-forward", "svc/tempo", f"{tempo_port}:3200", "-n", MONITORING_NAMESPACE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)


def stop_port_forward():
    if pf_process:
        print("\n[TEARDOWN] Closing network tunnel...", flush=True)
        try:
            pf_process.terminate()
        except Exception:
            pass


atexit.register(stop_port_forward)


def ensure_cluster_stability():
    """
    Verifies live cluster readiness (Tempo + Chaos Mesh controller) before starting each trial.
    """
    print("[HEALTH-CHECK] Validating live infrastructure readiness (Tempo + Chaos Mesh)...", flush=True)
    max_retries = 6
    for attempt in range(max_retries):
        try:
            ensure_port_forward(force_restart=(attempt > 0))
            req = urllib.request.Request(f"{tempo_endpoint}/ready", headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    print("[HEALTH-CHECK] Tempo observability backend is live and healthy.", flush=True)
                    return True
        except Exception:
            print(f"  -> Waiting for Tempo response (Attempt {attempt + 1}/{max_retries})...", flush=True)
            time.sleep(3)

    print("[WARN] Readiness check incomplete, proceeding with active tunnel...", flush=True)
    return False


def wait_for_workload_recovery():
    for svc in TARGET_POOL:
        run_cmd(f"kubectl rollout status deployment/{svc} -n {APP_NAMESPACE} --timeout=30s 2>/dev/null", timeout=35)


def build_balanced_trial_schedule(num_trials, seed=RANDOM_SEED):
    """
    Generates a paired, deterministic, balanced factorial schedule:
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


def is_exact_target_pod(pod_name, labels, target_service):
    pod_lower = pod_name.lower()
    if any(excluded in pod_lower for excluded in ("valkey", "redis", "load-generator", "loadgenerator", "frontend", "checkout")):
        return False
    for k in ("app.kubernetes.io/component", "app.kubernetes.io/name", "opentelemetry.io/name", "app"):
        if labels.get(k, "").lower() == target_service:
            return True
    return pod_lower == target_service or pod_lower.startswith(f"{target_service}-")


def resolve_target_pods(target_service):
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
                if is_exact_target_pod(pod_name, labels, target_service):
                    matched_pods.append(pod_name)
                    for k in ("app.kubernetes.io/name", "app.kubernetes.io/component", "app"):
                        if labels.get(k, "").lower() == target_service:
                            matched_label_key = k
                            matched_label_val = labels[k]
                            break
        except Exception:
            pass

    return matched_pods, matched_label_key, matched_label_val


def generate_chaos_manifest(target_service, chaos_type):
    pods, l_key, l_val = resolve_target_pods(target_service)
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
    """
    Creates the Chaos Mesh manifest and explicitly verifies the return code.
    If a residual object exists ('Cannot update chaos spec') or the webhook is transient,
    cleans up residual resources and retries before T0 is recorded.
    """
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


def prime_seen_traces(seen_traces):
    ensure_port_forward()
    now = time.time()
    start_sec = int(now - 90)
    end_sec = int(now) + 2
    for svc in SEARCH_POOL:
        queries = [
            {"tags": f"service.name={svc}", "minDuration": "600ms", "start": start_sec, "end": end_sec, "limit": 30},
            {"tags": f"service.name={svc} error=true", "start": start_sec, "end": end_sec, "limit": 30},
            {"tags": f"service.name={svc} status=error", "start": start_sec, "end": end_sec, "limit": 30}
        ]
        for q in queries:
            params = urllib.parse.urlencode(q)
            url = f"{tempo_endpoint}/api/search?{params}"
            try:
                req = urllib.request.Request(url, headers={"Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=3) as response:
                    data = json.loads(response.read().decode())
                    for t in data.get("traces", []):
                        trace_id = t.get("traceID", "").lower()
                        if trace_id:
                            seen_traces.add(trace_id)
            except Exception:
                pass


def search_new_anomalies(t0_epoch_sec, seen_traces):
    ensure_port_forward()
    candidates = []
    start_sec = int(t0_epoch_sec)
    end_sec = int(time.time()) + 2

    for svc in SEARCH_POOL:
        queries = [
            {"tags": f"service.name={svc}", "minDuration": "1500ms", "start": start_sec, "end": end_sec, "limit": 10},
            {"tags": f"service.name={svc} error=true", "start": start_sec, "end": end_sec, "limit": 10},
            {"tags": f"service.name={svc} status=error", "start": start_sec, "end": end_sec, "limit": 10}
        ]
        for q in queries:
            params = urllib.parse.urlencode(q)
            url = f"{tempo_endpoint}/api/search?{params}"
            try:
                req = urllib.request.Request(url, headers={"Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=3) as response:
                    data = json.loads(response.read().decode())
                    for t in data.get("traces", []):
                        trace_id = t.get("traceID", "").lower()
                        if trace_id and trace_id not in seen_traces:
                            seen_traces.add(trace_id)
                            candidates.append(trace_id)
            except Exception:
                pass

    return candidates


def analyze_standard_trace(trace_id, t0_epoch_sec):
    """
    Standard Distributed Tracing RCA heuristic (Scenario 4a):
    Inspects spans starting from t0 using standard OpenTelemetry error status flags
    or maximum total span duration (inclusive duration), without self-time decomposition
    and without multimodal correlation (Loki/Prometheus).
    """
    ensure_port_forward()
    url = f"{tempo_endpoint}/api/traces/{trace_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as response:
            trace_json = json.loads(response.read().decode())
    except Exception:
        return None

    batches = trace_json.get("batches", [])
    if not batches:
        return None

    error_services = []
    longest_service = None
    max_duration = 0.0
    strict_t0_ns = int(t0_epoch_sec * 1e9)

    for batch in batches:
        service_name = "unknown"
        for attr in batch.get("resource", {}).get("attributes", []):
            if attr.get("key") == "service.name":
                service_name = attr.get("value", {}).get("stringValue", "unknown").lower()

        for scope_span in batch.get("scopeSpans", []):
            for span in scope_span.get("spans", []):
                start = int(span.get("startTimeUnixNano", 0))
                end = int(span.get("endTimeUnixNano", 0))
                if start < strict_t0_ns:
                    continue

                duration = (end - start) / 1e6
                status_code = span.get("status", {}).get("code")
                if status_code == 2 or status_code == "STATUS_CODE_ERROR":
                    error_services.append(service_name)

                if duration > max_duration:
                    max_duration = duration
                    longest_service = service_name

    if error_services:
        culprit = error_services[-1]
        for t in TARGET_POOL:
            if t in culprit:
                return t
        return culprit

    if longest_service and max_duration >= 1500.0:
        for t in TARGET_POOL:
            if t in longest_service:
                return t
        return longest_service

    return None


def run_standard_rca_agent(t0, seen_traces):
    attempt = 0
    while (time.time() - t0) < TIMEOUT_SECONDS:
        attempt += 1
        elapsed = int(time.time() - t0)
        print(f"      [POLL #{attempt}] Elapsed: {elapsed}s. Scanning Tempo for anomalies...", flush=True)

        if (time.time() - t0) >= TIMEOUT_SECONDS:
            return "inconclusive", TIMEOUT_SECONDS

        candidate_traces = search_new_anomalies(t0, seen_traces)
        for trace_id in candidate_traces:
            culprit = analyze_standard_trace(trace_id, t0)
            if culprit:
                print(f"      [DEBUG] Trace {trace_id} diagnosed culprit: {culprit}", flush=True)
                return culprit, time.time() - t0

        time.sleep(POLLING_INTERVAL_SECONDS)

    return "inconclusive", TIMEOUT_SECONDS


def main():
    print("======================================================================", flush=True)
    print("  EXPERIMENT SCENARIO 4a: STANDARD DISTRIBUTED TRACING RCA", flush=True)
    print("======================================================================", flush=True)

    ensure_port_forward()
    seen_traces = set()
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
            print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting execution cycle...", flush=True)

            ensure_cluster_stability()
            clean_cluster()
            wait_for_workload_recovery()
            print("  -> Waiting for cluster stabilization (20s)...", flush=True)
            time.sleep(20)
            prime_seen_traces(seen_traces)

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
            print(f"  -> Fault injected blindly ({selected_target} via {selected_chaos}). T0: {t0_iso}", flush=True)

            time.sleep(INITIAL_PROPAGATION_SLEEP)
            diagnosed_service, elapsed_time = run_standard_rca_agent(t0, seen_traces)

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
                trial, "panoptes-standard", selected_chaos, selected_target,
                diagnosed_service, t0_iso, final_mttdiag, accuracy, censored
            ])
            f.flush()
            clean_cluster()
            trial += 1

    print(f"\n[OK] Scenario 4a execution completed. Results saved to: {RESULTS_FILE}", flush=True)


if __name__ == "__main__":
    main()
