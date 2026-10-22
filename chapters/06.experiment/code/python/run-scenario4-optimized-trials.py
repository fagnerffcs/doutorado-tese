#!/usr/bin/env python3
import csv
from datetime import datetime, timezone
import json
import random
import re
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
EVIDENCE_LOG_FILE = "scenario4b_evidence_audit.jsonl"
TARGET_POOL = ["payment", "cart", "shipping", "currency"]
SEARCH_POOL = ["frontend", "checkout", "payment", "cart", "shipping", "currency"]

pf_tempo = None
pf_loki = None
pf_prom = None
tempo_port = 3200
loki_port = 3100
prom_port = 9090
tempo_endpoint = f"http://localhost:{tempo_port}"
loki_endpoint = f"http://localhost:{loki_port}"
prom_endpoint = f"http://localhost:{prom_port}"

TRACE_ID_REGEX = re.compile(r'(?:traceID|trace_id|traceId)["\s:=]+([a-fA-F0-9]{32})')

CRITICAL_LOG_PATTERNS = [
    re.compile(r"rpc error:\s*code\s*=\s*(?:Unavailable|DeadlineExceeded|Internal|Canceled)", re.IGNORECASE),
    re.compile(r"context deadline exceeded", re.IGNORECASE),
    re.compile(r"connection refused|reset by peer|broken pipe|eof|transport is closing", re.IGNORECASE),
    re.compile(r"http\s*(?:status)?\s*5\d{2}", re.IGNORECASE),
    re.compile(r"failed to (?:call|charge|convert|ship|get|empty|add)", re.IGNORECASE),
    re.compile(r"panic|fatal|sigterm|sigkill|killed|oom", re.IGNORECASE)
]

STRICT_PEER_PATTERNS = {
    "payment": re.compile(r"(?:paymentservice|oteldemo\.paymentservice|payment:8080|payment\.otel-demo)", re.IGNORECASE),
    "shipping": re.compile(r"(?:shippingservice|oteldemo\.shippingservice|shipping:8080|shipping\.otel-demo|getquote|shiporder)", re.IGNORECASE),
    "currency": re.compile(r"(?:currencyservice|oteldemo\.currencyservice|currency:8080|currency\.otel-demo)", re.IGNORECASE),
    "cart": re.compile(r"(?:cartservice|oteldemo\.cartservice|cart:8080|cart\.otel-demo)", re.IGNORECASE)
}

def ensure_port_forwards():
    global pf_tempo, pf_loki, pf_prom
    if pf_tempo is None or pf_tempo.poll() is not None:
        if pf_tempo is not None:
            try:
                pf_tempo.terminate()
            except Exception:
                pass
        subprocess.run(f"fuser -k {tempo_port}/tcp 2>/dev/null", shell=True, timeout=5)
        pf_tempo = subprocess.Popen(
            ["kubectl", "port-forward", "svc/tempo", f"{tempo_port}:3200", "-n", MONITORING_NAMESPACE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(1)

    if pf_loki is None or pf_loki.poll() is not None:
        if pf_loki is not None:
            try:
                pf_loki.terminate()
            except Exception:
                pass
        subprocess.run(f"fuser -k {loki_port}/tcp 2>/dev/null", shell=True, timeout=5)
        pf_loki = subprocess.Popen(
            ["kubectl", "port-forward", "svc/loki", f"{loki_port}:3100", "-n", MONITORING_NAMESPACE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(1)

    if pf_prom is None or pf_prom.poll() is not None:
        if pf_prom is not None:
            try:
                pf_prom.terminate()
            except Exception:
                pass
        subprocess.run(f"fuser -k {prom_port}/tcp 2>/dev/null", shell=True, timeout=5)
        pf_prom = subprocess.Popen(
            ["kubectl", "port-forward", "svc/kube-prometheus-stack-prometheus", f"{prom_port}:9090", "-n", MONITORING_NAMESPACE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)

def stop_port_forwards():
    for proc in (pf_tempo, pf_loki, pf_prom):
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass

atexit.register(stop_port_forwards)

def run_cmd(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return None

def ensure_cluster_stability():
    print("[HEALTH-CHECK] Validating live infrastructure readiness (Prometheus + Loki + Tempo)...", flush=True)
    max_retries = 6
    for attempt in range(max_retries):
        try:
            ensure_port_forwards()
            req_t = urllib.request.Request(f"{tempo_endpoint}/ready")
            req_l = urllib.request.Request(f"{loki_endpoint}/ready")
            req_p = urllib.request.Request(f"{prom_endpoint}/-/ready")
            with urllib.request.urlopen(req_t, timeout=3) as rt, \
                 urllib.request.urlopen(req_l, timeout=3) as rl, \
                 urllib.request.urlopen(req_p, timeout=3) as rp:
                if rt.status == 200 and rl.status == 200 and rp.status == 200:
                    print("[HEALTH-CHECK] Full PANOPTES stack (M + L + T) is live and healthy.", flush=True)
                    return True
        except Exception:
            print(f"  -> Waiting for observability stack response (Attempt {attempt+1}/{max_retries})...", flush=True)
            time.sleep(3)
    print("[WARN] Readiness check incomplete, proceeding with active tunnels...", flush=True)
    return True

def wait_for_workload_recovery():
    for svc in TARGET_POOL:
        run_cmd(f"kubectl rollout status deployment/{svc} -n {APP_NAMESPACE} --timeout=30s 2>/dev/null")

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
        subprocess.run(
            f"kubectl delete networkchaos,podchaos,stresschaos --all -n {APP_NAMESPACE} --grace-period=0 --force --ignore-not-found --wait=false 2>/dev/null",
            shell=True,
            timeout=5
        )
    except Exception:
        pass

def query_prometheus_cpu_rates():
    ensure_port_forwards()
    rates = {t: 0.0 for t in TARGET_POOL}
    promql = f'sum by (pod) (rate(container_cpu_usage_seconds_total{{namespace="{APP_NAMESPACE}", container!="", container!="POD"}}[1m])) * 1000'
    params = urllib.parse.urlencode({"query": promql})
    url = f"{prom_endpoint}/api/v1/query?{params}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            results = data.get("data", {}).get("result", [])
            for item in results:
                pod_name = item.get("metric", {}).get("pod", "").lower()
                val_mcpu = float(item.get("value", [0, "0"])[1])
                for target in TARGET_POOL:
                    if target in pod_name:
                        rates[target] += val_mcpu
    except Exception:
        pass

    if all(v == 0.0 for v in rates.values()):
        res = run_cmd(f"kubectl top pods -n {APP_NAMESPACE} --no-headers 2>/dev/null")
        if res and res.stdout:
            for line in res.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 2:
                    pod_name = parts[0].lower()
                    cpu_raw = parts[1]
                    val = float(cpu_raw[:-1]) if cpu_raw.endswith("m") else float(cpu_raw) * 1000.0
                    for target in TARGET_POOL:
                        if target in pod_name:
                            rates[target] += val
    return rates

def fetch_loki_window(start_sec, end_sec, seen_logs):
    ensure_port_forwards()
    start_ns = int(start_sec * 1e9)
    end_ns = int(end_sec * 1e9)
    logql = f'{{namespace="{APP_NAMESPACE}"}}'
    params = urllib.parse.urlencode({
        "query": logql,
        "start": str(start_ns),
        "end": str(end_ns),
        "limit": 400,
        "direction": "forward"
    })
    url = f"{loki_endpoint}/loki/api/v1/query_range?{params}"
    log_events = []
    linked_traces = []

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            streams = data.get("data", {}).get("result", [])
            for stream in streams:
                labels = stream.get("stream", {})
                source_service = " ".join([
                    labels.get("app_kubernetes_io_name", ""),
                    labels.get("app", ""),
                    labels.get("pod", ""),
                    labels.get("container", ""),
                    labels.get("service_name", "")
                ]).lower()

                for ts_ns, line in stream.get("values", []):
                    if int(ts_ns) < start_ns:
                        continue
                    sig_key = f"{ts_ns}:{hash(line)}"
                    if sig_key in seen_logs:
                        continue
                    seen_logs.add(sig_key)

                    if not any(p.search(line) for p in CRITICAL_LOG_PATTERNS):
                        continue

                    match = TRACE_ID_REGEX.search(line)
                    tid = match.group(1).lower() if match else None
                    if tid and tid not in linked_traces:
                        linked_traces.append(tid)

                    matched_targets = []
                    for target, pat in STRICT_PEER_PATTERNS.items():
                        if pat.search(line) and target not in source_service:
                            matched_targets.append(target)

                    if not matched_targets:
                        for target in TARGET_POOL:
                            if target in source_service:
                                matched_targets.append(target)

                    for t in matched_targets:
                        log_events.append({
                            "target": t,
                            "timestamp_ns": ts_ns,
                            "source_pod": labels.get("pod", source_service),
                            "trace_id": tid,
                            "excerpt": line.strip()[:160]
                        })
    except Exception:
        pass

    return log_events, linked_traces

def prime_baselines(seen_traces, seen_logs):
    ensure_port_forwards()
    now = time.time()
    start_sec = int(now - 90)
    for svc in SEARCH_POOL:
        for q in [
            {"tags": f"service.name={svc}", "minDuration": "800ms", "start": start_sec, "limit": 25},
            {"tags": f"service.name={svc} status=error", "start": start_sec, "limit": 25},
            {"tags": f"service.name={svc} error=true", "start": start_sec, "limit": 25}
        ]:
            params = urllib.parse.urlencode(q)
            url = f"{tempo_endpoint}/api/search?{params}"
            try:
                req = urllib.request.Request(url, headers={"Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=3) as response:
                    data = json.loads(response.read().decode())
                    for t in data.get("traces", []):
                        tid = t.get("traceID")
                        if tid:
                            seen_traces.add(tid.lower())
            except Exception:
                pass

    _, _ = fetch_loki_window(now - 30, now, seen_logs)
    baseline_cpu = query_prometheus_cpu_rates()
    return baseline_cpu

def calculate_exclusive_self_time(span, spans_dict):
    children_intervals = []
    for child_id in span["children"]:
        if child_id in spans_dict:
            c = spans_dict[child_id]
            children_intervals.append([c["start"], c["end"]])
    if not children_intervals:
        return span["duration"]

    children_intervals.sort(key=lambda x: x[0])
    merged = [children_intervals[0]]
    for current in children_intervals[1:]:
        prev = merged[-1]
        if current[0] <= prev[1]:
            prev[1] = max(prev[1], current[1])
        else:
            merged.append(current)

    children_duration_ms = sum([m[1] - m[0] for m in merged]) / 1e6
    return max(0.0, span["duration"] - children_duration_ms)

def resolve_client_span_peer(service_name, span_name, span_attrs_dict):
    peer_fields = " ".join([
        span_name,
        span_attrs_dict.get("rpc.service", ""),
        span_attrs_dict.get("net.peer.name", ""),
        span_attrs_dict.get("server.address", ""),
        span_attrs_dict.get("http.url", ""),
        span_attrs_dict.get("url.full", "")
    ]).lower()

    for target, pat in STRICT_PEER_PATTERNS.items():
        if target not in service_name and pat.search(peer_fields):
            return target
    return None

def isolate_root_cause_from_trace(trace_id, t0_epoch_sec):
    ensure_port_forwards()
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

    spans = {}
    t0_ns = int((t0_epoch_sec - 2.0) * 1e9)
    newest_span_start = 0

    for batch in batches:
        service_name = "unknown"
        for attr in batch.get("resource", {}).get("attributes", []):
            if attr.get("key") == "service.name":
                service_name = attr.get("value", {}).get("stringValue", "unknown").lower()

        for scope_span in batch.get("scopeSpans", []):
            for span in scope_span.get("spans", []):
                span_id = span.get("spanId")
                start = int(span.get("startTimeUnixNano", 0))
                end = int(span.get("endTimeUnixNano", 0))
                if start > newest_span_start:
                    newest_span_start = start
                dur_ms = (end - start) / 1e6
                status_code = span.get("status", {}).get("code")
                is_err = (status_code == 2 or status_code == "STATUS_CODE_ERROR")

                attr_dict = {}
                for a in span.get("attributes", []):
                    k = a.get("key", "")
                    v = a.get("value", {}).get("stringValue", "")
                    if k and v:
                        attr_dict[k] = v

                spans[span_id] = {
                    "span_id": span_id,
                    "service": service_name,
                    "name": span.get("name", ""),
                    "kind": str(span.get("kind", "")),
                    "attrs": attr_dict,
                    "parent": span.get("parentSpanId"),
                    "start": start,
                    "end": end,
                    "duration": dur_ms,
                    "is_error": is_err,
                    "children": []
                }

    if newest_span_start > 0 and newest_span_start < t0_ns:
        return None

    for span_id, s in spans.items():
        pid = s["parent"]
        if pid and pid in spans:
            spans[pid]["children"].append(span_id)

    error_candidates = []
    for span_id, s in spans.items():
        self_time = calculate_exclusive_self_time(s, spans)
        s["self_time"] = round(self_time, 2)
        if s["is_error"]:
            peer_target = resolve_client_span_peer(s["service"], s["name"], s["attrs"])
            if peer_target:
                error_candidates.append((peer_target, s, "client_rpc_error_to_peer"))
            else:
                for t in TARGET_POOL:
                    if t in s["service"]:
                        error_candidates.append((t, s, "service_error_span"))

    if error_candidates:
        chosen_target, chosen_span, reason = error_candidates[0]
        return {
            "culprit": chosen_target,
            "modality": "TEMPO_TRACE_ERROR",
            "evidence_id": f"trace:{trace_id}/span:{chosen_span['span_id']}",
            "summary": f"{reason} on {chosen_span['service']} ({chosen_span['name']}) dur={chosen_span['duration']:.1f}ms self={chosen_span['self_time']:.1f}ms",
            "raw_span": chosen_span
        }

    max_self_time = 0.0
    culprit_target = None
    culprit_span = None
    attribution_mode = ""

    for span_id, s in spans.items():
        self_time = s["self_time"]
        if self_time < 1200.0:
            continue

        matched_target = None
        mode = ""
        for t in TARGET_POOL:
            if t in s["service"]:
                matched_target = t
                mode = "direct_self_time"
                break

        if not matched_target:
            peer_target = resolve_client_span_peer(s["service"], s["name"], s["attrs"])
            if peer_target:
                matched_target = peer_target
                mode = "l4_client_wait_self_time"

        if matched_target and self_time > max_self_time:
            max_self_time = self_time
            culprit_target = matched_target
            culprit_span = s
            attribution_mode = mode

    if culprit_target and culprit_span:
        return {
            "culprit": culprit_target,
            "modality": "TEMPO_SELF_TIME",
            "evidence_id": f"trace:{trace_id}/span:{culprit_span['span_id']}",
            "summary": f"{attribution_mode} isolated {culprit_target} via span {culprit_span['service']}:{culprit_span['name']} self_time={max_self_time:.1f}ms (total={culprit_span['duration']:.1f}ms)",
            "raw_span": culprit_span
        }

    return None

def search_tempo_anomalies(t0_epoch_sec, seen_traces):
    ensure_port_forwards()
    candidates = []
    start_sec = int(t0_epoch_sec) - 1
    end_sec = int(time.time()) + 2

    for svc in SEARCH_POOL:
        queries = [
            {"tags": f"service.name={svc}", "minDuration": "1500ms", "start": start_sec, "end": end_sec, "limit": 10},
            {"tags": f"service.name={svc} status=error", "start": start_sec, "end": end_sec, "limit": 10},
            {"tags": f"service.name={svc} error=true", "start": start_sec, "end": end_sec, "limit": 10}
        ]
        for q in queries:
            params = urllib.parse.urlencode(q)
            url = f"{tempo_endpoint}/api/search?{params}"
            try:
                req = urllib.request.Request(url, headers={"Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=3) as response:
                    data = json.loads(response.read().decode())
                    for t in data.get("traces", []):
                        tid = t.get("traceID", "").lower()
                        if tid and tid not in seen_traces:
                            seen_traces.add(tid)
                            candidates.append(tid)
            except Exception:
                pass
    return candidates

def run_panoptes_rca_agent(t0, seen_traces, seen_logs, baseline_cpu):
    attempt = 0
    last_loki_ts = t0
    loki_hit_counts = {t: 0 for t in TARGET_POOL}
    loki_first_evidence = {}
    prom_sustained_hits = {t: 0 for t in TARGET_POOL}

    while (time.time() - t0) < TIMEOUT_SECONDS:
        attempt += 1
        now = time.time()
        elapsed = int(now - t0)
        print(f"      [POLL #{attempt}] Elapsed: {elapsed}s. Scanning PANOPTES (Tempo + Loki + Prometheus)...", flush=True)

        log_events, loki_trace_ids = fetch_loki_window(last_loki_ts - 1, now + 1, seen_logs)
        last_loki_ts = now

        for ev in log_events:
            t = ev["target"]
            loki_hit_counts[t] += 1
            if t not in loki_first_evidence:
                loki_first_evidence[t] = ev

        for tid in loki_trace_ids:
            if tid not in seen_traces:
                seen_traces.add(tid)
                verdict = isolate_root_cause_from_trace(tid, t0)
                if verdict:
                    verdict["modality"] = "LOKI_TO_TEMPO_CORRELATION"
                    return verdict, time.time() - t0

        tempo_candidates = search_tempo_anomalies(t0, seen_traces)
        for tid in tempo_candidates:
            verdict = isolate_root_cause_from_trace(tid, t0)
            if verdict:
                return verdict, time.time() - t0

        top_log_target = max(loki_hit_counts, key=loki_hit_counts.get)
        if loki_hit_counts[top_log_target] >= 2:
            ev = loki_first_evidence[top_log_target]
            return {
                "culprit": top_log_target,
                "modality": "LOKI_LOG_SIGNATURE",
                "evidence_id": f"loki_ns:{ev['timestamp_ns']}/pod:{ev['source_pod']}",
                "summary": f"Log exception pattern ({loki_hit_counts[top_log_target]} hits): {ev['excerpt']}",
                "raw_log": ev
            }, time.time() - t0

        if elapsed >= 12:
            current_cpu = query_prometheus_cpu_rates()
            for t in TARGET_POOL:
                delta_mcpu = current_cpu.get(t, 0.0) - baseline_cpu.get(t, 0.0)
                if delta_mcpu >= 250.0 or current_cpu.get(t, 0.0) >= 450.0:
                    prom_sustained_hits[t] += 1
                    if prom_sustained_hits[t] >= 2:
                        return {
                            "culprit": t,
                            "modality": "PROMETHEUS_METRIC_SATURATION",
                            "evidence_id": f"promql:container_cpu_usage_seconds_total[{t}]",
                            "summary": f"CPU saturation on {t}: current={current_cpu[t]:.1f}mCPU vs baseline={baseline_cpu.get(t, 0.0):.1f}mCPU (delta=+{delta_mcpu:.1f}mCPU)",
                            "raw_metrics": {"baseline_mcpu": baseline_cpu, "current_mcpu": current_cpu}
                        }, time.time() - t0
                else:
                    prom_sustained_hits[t] = max(0, prom_sustained_hits[t] - 1)

        time.sleep(POLLING_INTERVAL_SECONDS)

    return None, TIMEOUT_SECONDS

def main():
    print("======================================================================", flush=True)
    print("  EXPERIMENT SCENARIO 4b: PANOPTES MULTIMODAL RCA + EVIDENCE AUDIT", flush=True)
    print("======================================================================", flush=True)

    ensure_port_forwards()
    seen_traces = set()
    seen_logs = set()

    with open(RESULTS_FILE, mode="w", newline="") as f_csv, \
         open(EVIDENCE_LOG_FILE, mode="w") as f_audit:

        writer = csv.writer(f_csv)
        writer.writerow([
            "trial_id", "scenario", "chaos_type", "ground_truth",
            "diagnosed_target", "t0_epoch", "mttdiag_seconds",
            "accuracy", "censored", "detection_modality",
            "evidence_id", "evidence_summary"
        ])

        for trial in range(1, NUM_TRIALS + 1):
            print(f"\n[Trial {trial:02d}/{NUM_TRIALS}] Starting execution cycle...", flush=True)

            ensure_cluster_stability()
            clean_cluster()
            wait_for_workload_recovery()
            print("  -> Waiting for cluster stabilization (20s)...", flush=True)
            time.sleep(20)
            print("  -> Priming telemetry caches & capturing baseline metrics...", flush=True)
            baseline_cpu = prime_baselines(seen_traces, seen_logs)

            selected_target = random.choice(TARGET_POOL)
            selected_chaos = random.choice(["network-delay", "pod-kill", "cpu-stress"])
            manifest_content = generate_chaos_manifest(selected_target, selected_chaos)

            with open("/tmp/current_chaos.yaml", "w") as m:
                m.write(manifest_content)

            t0 = time.time()
            t0_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            run_cmd("kubectl apply -f /tmp/current_chaos.yaml")
            print(f"  -> Fault injected blindly ({selected_target} via {selected_chaos}). T0: {t0_iso}", flush=True)

            time.sleep(8)
            verdict, elapsed_time = run_panoptes_rca_agent(t0, seen_traces, seen_logs, baseline_cpu)

            if verdict is None or elapsed_time >= TIMEOUT_SECONDS:
                final_mttdiag = float(TIMEOUT_SECONDS)
                diagnosed_service = "inconclusive"
                accuracy = 0
                censored = True
                modality = "NONE_TIMEOUT"
                evidence_id = "none"
                evidence_summary = "Right-censored at 300s operational ceiling"
                print("\n  [RESULT] TIMEOUT / INCONCLUSIVE (300.0s). Censored = True.", flush=True)
            else:
                final_mttdiag = round(elapsed_time, 2)
                diagnosed_service = verdict["culprit"]
                censored = False
                accuracy = 1 if diagnosed_service == selected_target else 0
                modality = verdict["modality"]
                evidence_id = verdict["evidence_id"]
                evidence_summary = verdict["summary"]
                status_str = "SUCCESS (Acc=1)" if accuracy == 1 else "MISATTRIBUTION (Acc=0)"
                print(f"\n  [RESULT] Converged in {final_mttdiag}s via {modality}", flush=True)
                print(f"           Diagnosed: {diagnosed_service} | Ground-Truth: {selected_target} -> {status_str}", flush=True)
                print(f"           Evidence : [{evidence_id}] {evidence_summary}", flush=True)

            writer.writerow([
                trial, "panoptes-4b", selected_chaos, selected_target,
                diagnosed_service, t0_iso, final_mttdiag,
                accuracy, censored, modality,
                evidence_id, evidence_summary
            ])
            f_csv.flush()

            audit_record = {
                "trial_id": trial,
                "scenario": "panoptes-4b",
                "t0_epoch": t0_iso,
                "chaos_type": selected_chaos,
                "ground_truth": selected_target,
                "diagnosed_target": diagnosed_service,
                "mttdiag_seconds": final_mttdiag,
                "accuracy": accuracy,
                "censored": censored,
                "detection_modality": modality,
                "evidence_id": evidence_id,
                "evidence_summary": evidence_summary,
                "baseline_cpu_mcpu": baseline_cpu,
                "raw_verdict_payload": verdict if verdict else {}
            }
            f_audit.write(json.dumps(audit_record) + "\n")
            f_audit.flush()

            clean_cluster()

    print(f"\n[OK] Scenario 4b completed. CSV saved to: {RESULTS_FILE} | Audit log: {EVIDENCE_LOG_FILE}", flush=True)

if __name__ == "__main__":
    main()