#!/usr/bin/env python3
import time
import subprocess
import csv
import re
from datetime import datetime

NUM_SAMPLES = 30
SAMPLE_INTERVAL_SECONDS = 5
OUTPUT_FILE = "scenario1_workload_baseline.csv"

def parse_cpu(cpu_str):
    # Convert '15m' to 15.0 millicores
    if cpu_str.endswith('m'):
        return float(cpu_str[:-1])
    elif cpu_str.endswith('n'):
        return float(cpu_str[:-1]) / 1_000_000.0
    return float(cpu_str) * 1000.0

def parse_memory(mem_str):
    # Convert to MiB
    if mem_str.endswith('Mi'):
        return float(mem_str[:-2])
    elif mem_str.endswith('Gi'):
        return float(mem_str[:-2]) * 1024.0
    elif mem_str.endswith('Ki'):
        return float(mem_str[:-2]) / 1024.0
    return float(mem_str) / (1024.0 * 1024.0)

print(f"[{datetime.now().isoformat()}] Starting Scenario 1 collection: {NUM_SAMPLES} samples every {SAMPLE_INTERVAL_SECONDS}s...")

with open(OUTPUT_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["sample_id", "timestamp", "total_cpu_millicores", "total_memory_mib"])

    for sample_id in range(1, NUM_SAMPLES + 1):
        try:
            cmd = ["kubectl", "top", "pods", "-n", "otel-demo", "--no-headers"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            sample_cpu = 0.0
            sample_mem = 0.0

            for line in res.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 3:
                    sample_cpu += parse_cpu(parts[1])
                    sample_mem += parse_memory(parts[2])

            ts = datetime.utcnow().isoformat()
            writer.writerow([sample_id, ts, round(sample_cpu, 2), round(sample_mem, 2)])
            f.flush()
            print(f"Sample {sample_id:02d}/{NUM_SAMPLES}: CPU = {sample_cpu:.2f}m | RAM = {sample_mem:.2f} MiB")

        except Exception as e:
            print(f"Error in sample {sample_id}: {e}")

        if sample_id < NUM_SAMPLES:
            time.sleep(SAMPLE_INTERVAL_SECONDS)

print(f"\n[OK] Collection completed successfully. Data saved to: {OUTPUT_FILE}")