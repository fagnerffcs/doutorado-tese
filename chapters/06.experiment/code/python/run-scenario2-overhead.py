#!/usr/bin/env python3
import time
import subprocess
import csv
from datetime import datetime

NUM_SAMPLES = 30
SAMPLE_INTERVAL_SECONDS = 5
OUTPUT_FILE = "scenario2_overhead_panoptes.csv"
WORKLOAD_NAMESPACE = "otel-demo"
MONITORING_NAMESPACE = "monitoring"

def parse_cpu(cpu_str):
    if cpu_str.endswith('m'):
        return float(cpu_str[:-1])
    elif cpu_str.endswith('n'):
        return float(cpu_str[:-1]) / 1_000_000.0
    return float(cpu_str) * 1000.0

def parse_memory(mem_str):
    if mem_str.endswith('Mi'):
        return float(mem_str[:-2])
    elif mem_str.endswith('Gi'):
        return float(mem_str[:-2]) * 1024.0
    elif mem_str.endswith('Ki'):
        return float(mem_str[:-2]) / 1024.0
    return float(mem_str) / (1024.0 * 1024.0)

def sample_namespace_resources(namespace):
    cmd = ["kubectl", "top", "pods", "-n", namespace, "--no-headers"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return 0.0, 0.0
    
    cpu_total = 0.0
    mem_total = 0.0
    for line in res.stdout.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 3:
            cpu_total += parse_cpu(parts[1])
            mem_total += parse_memory(parts[2])
    return cpu_total, mem_total

print(f"[{datetime.now().isoformat()}] Starting Scenario 2 sampling: {NUM_SAMPLES} samples every {SAMPLE_INTERVAL_SECONDS}s...")

with open(OUTPUT_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "sample_id", "timestamp", 
        "workload_cpu_millicores", "workload_memory_mib",
        "panoptes_cpu_millicores", "panoptes_memory_mib",
        "total_cluster_cpu_millicores", "total_cluster_memory_mib"
    ])

    for sample_id in range(1, NUM_SAMPLES + 1):
        try:
            w_cpu, w_mem = sample_namespace_resources(WORKLOAD_NAMESPACE)
            p_cpu, p_mem = sample_namespace_resources(MONITORING_NAMESPACE)
            
            tot_cpu = w_cpu + p_cpu
            tot_mem = w_mem + p_mem
            ts = datetime.utcnow().isoformat()

            writer.writerow([
                sample_id, ts,
                round(w_cpu, 2), round(w_mem, 2),
                round(p_cpu, 2), round(p_mem, 2),
                round(tot_cpu, 2), round(tot_mem, 2)
            ])
            f.flush()

            print(f"Sample {sample_id:02d}/{NUM_SAMPLES}: "
                  f"Workload CPU={w_cpu:.1f}m, RAM={w_mem:.1f}MiB | "
                  f"PANOPTES CPU={p_cpu:.1f}m, RAM={p_mem:.1f}MiB")

        except Exception as e:
            print(f"Error in sample {sample_id}: {e}")

        if sample_id < NUM_SAMPLES:
            time.sleep(SAMPLE_INTERVAL_SECONDS)

print(f"\n[OK] Scenario 2 completed. Saved to: {OUTPUT_FILE}")