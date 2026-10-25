#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import os

os.makedirs("../../images/results", exist_ok=True)

df3 = pd.read_csv("../../06.scenario3_diagnostic_trials.csv")
df4b = pd.read_csv("scenario4b_optimized_trials.csv")

df3['event'] = (~df3['censored']).astype(int)
df4b['event'] = (~df4b['censored']).astype(int)

kmf3 = KaplanMeierFitter()
kmf4b = KaplanMeierFitter()

kmf3.fit(durations=df3['mttdiag_seconds'], event_observed=df3['event'], label='S3: Vanilla (Log-Scraping)')
kmf4b.fit(durations=df4b['mttdiag_seconds'], event_observed=df4b['event'], label='S4b: PANOPTES (Optimized RCA)')

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

ax = kmf3.plot_survival_function(color='#34495e', linewidth=2.5, ci_show=False)
kmf4b.plot_survival_function(ax=ax, color='#2ecc71', linewidth=2.5, ci_show=False)

plt.title('Kaplan-Meier Survival Estimate of Diagnostic Blindness', fontsize=14)
plt.ylabel('Probability of Remaining Undiagnosed', fontsize=12)
plt.xlabel('Diagnostic Latency ($MTTDiag$) in Seconds', fontsize=12)
plt.xlim(0, 310)
plt.ylim(0, 1.05)

plt.axvline(x=300, color='red', linestyle='--', alpha=0.6, label='Operational Timeout (300 s)')
plt.legend(loc='lower left', fontsize=11)

plt.tight_layout()
output_path = "../../images/results/kaplan_meier_survival_curve.png"
plt.savefig(output_path, dpi=300)
print(f"[OK] Graph saved in: {output_path}")

results = logrank_test(df3['mttdiag_seconds'], df4b['mttdiag_seconds'], 
                       event_observed_A=df3['event'], event_observed_B=df4b['event'])

print("\n=== STATISTICS RESULTS TO LATEX ===")
print(f"Test Statistic (Chi-Squared): {results.test_statistic:.2f}")
print(f"p-value: {results.p_value:.4e}")