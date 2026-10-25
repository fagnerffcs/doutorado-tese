#!/usr/bin/env python3
import csv
from datetime import datetime, timezone
import subprocess
import time

NUM_SAMPLES = 30
SAMPLE_INTERVAL_SECONDS = 16
OUTPUT_FILE = "scenario2_overhead_panoptes.csv"
WORKLOAD_NAMESPACE = "otel-demo"
MONITORING_NAMESPACE = "monitoring"


def parse_cpu(cpu_str):
    if cpu_str.endswith("m"):
        return float(cpu_str[:-1])
    elif cpu_str.endswith("n"):
        return float(cpu_str[:-1]) / 1_000_000.0
    return float(cpu_str) * 1000.0


def parse_memory(mem_str):
    if mem_str.endswith("Mi"):
        return float(mem_str[:-2])
    elif mem_str.endswith("Gi"):
        return float(mem_str[:-2]) * 1024.0
    elif mem_str.endswith("Ki"):
        return float(mem_str[:-2]) / 1024.0
    return float(mem_str) / (1024.0 * 1024.0)


def sample_namespace_resources(namespace):
    cmd = ["kubectl", "top", "pods", "-n", namespace, "--no-headers"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)
    lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
    if not lines:
        raise RuntimeError(f"Empty metrics output for namespace '{namespace}'")

    cpu_total = 0.0
    mem_total = 0.0
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            cpu_total += parse_cpu(parts[1])
            mem_total += parse_memory(parts[2])
    return round(cpu_total, 2), round(mem_total, 2)


def main():
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] Starting Scenario 2 sampling: "
        f"{NUM_SAMPLES} independent samples every {SAMPLE_INTERVAL_SECONDS}s...",
        flush=True
    )

    last_reading = None

    with open(OUTPUT_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "sample_id", "timestamp",
            "workload_cpu_millicores", "workload_memory_mib",
            "panoptes_cpu_millicores", "panoptes_memory_mib",
            "total_cluster_cpu_millicores", "total_cluster_memory_mib"
        ])

        sample_id = 1
        while sample_id <= NUM_SAMPLES:
            try:
                w_cpu, w_mem = sample_namespace_resources(WORKLOAD_NAMESPACE)
                p_cpu, p_mem = sample_namespace_resources(MONITORING_NAMESPACE)

                retries = 0
                while last_reading == (w_cpu, w_mem, p_cpu, p_mem) and retries < 3:
                    time.sleep(2)
                    w_cpu, w_mem = sample_namespace_resources(WORKLOAD_NAMESPACE)
                    p_cpu, p_mem = sample_namespace_resources(MONITORING_NAMESPACE)
                    retries += 1

                last_reading = (w_cpu, w_mem, p_cpu, p_mem)
                tot_cpu = round(w_cpu + p_cpu, 2)
                tot_mem = round(w_mem + p_mem, 2)
                ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

                writer.writerow([
                    sample_id, ts,
                    w_cpu, w_mem,
                    p_cpu, p_mem,
                    tot_cpu, tot_mem
                ])
                f.flush()

                print(
                    f"Sample {sample_id:02d}/{NUM_SAMPLES}: "
                    f"Workload CPU={w_cpu:.1f}m, RAM={w_mem:.1f}MiB | "
                    f"PANOPTES CPU={p_cpu:.1f}m, RAM={p_mem:.1f}MiB",
                    flush=True
                )

                if sample_id < NUM_SAMPLES:
                    time.sleep(SAMPLE_INTERVAL_SECONDS)
                sample_id += 1

            except Exception as e:
                print(f"[WARN] Transient error in sample {sample_id}: {e}. Retrying in 5s...", flush=True)
                time.sleep(5)

    print(f"\n[OK] Scenario 2 completed. Saved to: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    main()
