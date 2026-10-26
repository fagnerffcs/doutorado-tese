#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

os.makedirs("../../images/results", exist_ok=True)

df3 = pd.read_csv("scenario3_diagnostic_trials.csv")
df3s = pd.read_csv("scenario3_diagnostic_trials_stratified.csv")
df4a = pd.read_csv("scenario4_diagnostic_trials.csv")
df4b = pd.read_csv("scenario4b_optimized_trials.csv")

df3["event"] = (df3["accuracy"] == 1).astype(int)
df3s["event"] = (df3s["accuracy"] == 1).astype(int)
df4a["event"] = (df4a["accuracy"] == 1).astype(int)
df4b["event"] = (df4b["accuracy"] == 1).astype(int)

kmf3 = KaplanMeierFitter()
kmf3s = KaplanMeierFitter()
kmf4a = KaplanMeierFitter()
kmf4b = KaplanMeierFitter()

kmf3.fit(durations=df3["mttdiag_seconds"], event_observed=df3["event"], label="S3: Vanilla CLI Baseline (Acc=20.0%)")
kmf3s.fit(durations=df3s["mttdiag_seconds"], event_observed=df3s["event"], label="S3-Strat: Vanilla Replicated (Acc=23.3%)")
kmf4a.fit(durations=df4a["mttdiag_seconds"], event_observed=df4a["event"], label="S4a: Monomodal Trace RCA (Acc=0.0%)")
kmf4b.fit(durations=df4b["mttdiag_seconds"], event_observed=df4b["event"], label="S4b: PANOPTES Multimodal RCA (Acc=83.3%)")

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

ax = kmf3.plot_survival_function(color="#34495e", linewidth=2.5, ci_show=False)
kmf3s.plot_survival_function(ax=ax, color="#7f8c8d", linestyle="--", linewidth=2.0, ci_show=False)
kmf4a.plot_survival_function(ax=ax, color="#e67e22", linestyle=":", linewidth=2.5, ci_show=False)
kmf4b.plot_survival_function(ax=ax, color="#2ecc71", linewidth=2.8, ci_show=False)

plt.ylabel("Probability of Fault Remaining Undiagnosed P(T > t)", fontsize=12)
plt.xlabel("Diagnostic Latency (MTTDiag) in Seconds", fontsize=12)
plt.xlim(0, 310)
plt.ylim(0, 1.05)

plt.axvline(x=300, color="red", linestyle="--", alpha=0.6, label="Operational Timeout Ceiling (300 s)")
plt.legend(loc="center right", fontsize=10.5)

plt.tight_layout()
output_path = "../../images/results/kaplan_meier_survival_curve.png"
plt.savefig(output_path, dpi=300)
print(f"[OK] Graph saved in: {output_path}")

results = logrank_test(
    df3["mttdiag_seconds"], df4b["mttdiag_seconds"],
    event_observed_A=df3["event"], event_observed_B=df4b["event"]
)

print("\n=== STATISTICS RESULTS TO LATEX ===")
print(f"Test Statistic (Chi-Squared): {results.test_statistic:.2f}")
print(f"p-value: {results.p_value:.4e}")
