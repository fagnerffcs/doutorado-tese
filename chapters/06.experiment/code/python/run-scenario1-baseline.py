#!/usr/bin/env python3
import csv
from datetime import datetime, timezone
import subprocess
import time

NUM_SAMPLES = 30
SAMPLE_INTERVAL_SECONDS = 16
OUTPUT_FILE = "scenario1_workload_baseline.csv"
WORKLOAD_NAMESPACE = "otel-demo"


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


def fetch_namespace_metrics(namespace):
    cmd = ["kubectl", "top", "pods", "-n", namespace, "--no-headers"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)
    lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
    if not lines:
        raise RuntimeError(f"No pod metrics returned for namespace '{namespace}'")

    sample_cpu = 0.0
    sample_mem = 0.0
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            sample_cpu += parse_cpu(parts[1])
            sample_mem += parse_memory(parts[2])
    return round(sample_cpu, 2), round(sample_mem, 2)


def main():
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] Starting Scenario 1 baseline collection: "
        f"{NUM_SAMPLES} independent samples every {SAMPLE_INTERVAL_SECONDS}s...",
        flush=True
    )

    last_reading = None

    with open(OUTPUT_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_id", "timestamp", "total_cpu_millicores", "total_memory_mib"])

        sample_id = 1
        while sample_id <= NUM_SAMPLES:
            try:
                sample_cpu, sample_mem = fetch_namespace_metrics(WORKLOAD_NAMESPACE)

                retries = 0
                while last_reading == (sample_cpu, sample_mem) and retries < 3:
                    time.sleep(2)
                    sample_cpu, sample_mem = fetch_namespace_metrics(WORKLOAD_NAMESPACE)
                    retries += 1

                last_reading = (sample_cpu, sample_mem)
                ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                writer.writerow([sample_id, ts, sample_cpu, sample_mem])
                f.flush()
                print(
                    f"Amostra {sample_id:02d}/{NUM_SAMPLES}: CPU = {sample_cpu:.2f}m | RAM = {sample_mem:.2f} MiB",
                    flush=True
                )

                if sample_id < NUM_SAMPLES:
                    time.sleep(SAMPLE_INTERVAL_SECONDS)
                sample_id += 1

            except Exception as e:
                print(f"[WARN] Transitory error in sample {sample_id}: {e}. Retry in 5s...", flush=True)
                time.sleep(5)

    print(f"\n[OK] Collection completed successfully. Data saved to: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    main()
