"""
Dynamic Unsupervised Customer Segmentation via K-Means Clustering
Operates dynamically on usable numerical customer features.
Provides honest fallbacks when continuous features are insufficient.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

def run_project_segmentation(df, target_col, numeric_cols, output_dir, k=4):
    """
    Fits K-Means clustering on available numeric features.
    If numeric features < 2, returns an honest explanation of unavailability.
    """
    os.makedirs(output_dir, exist_ok=True)
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    summary_file = os.path.join(output_dir, "segmentation.json")
    model_file = os.path.join(output_dir, "segmentation.joblib")

    # Fallback validation
    if not numeric_cols or len(numeric_cols) < 2:
        result = {
            "available": False,
            "reason": "Customer segmentation requires at least two continuous numerical metrics with meaningful variation to establish multi-dimensional cluster centroids. Single-dimension or purely categorical datasets cannot be clustered geometrically without fabricating pseudo-distances. Consult univariate distributions on the Customer Analytics page."
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        return result

    if len(df) < 30:
        result = {
            "available": False,
            "reason": "Dataset size is too small (< 30 records) to derive stable unsupervised customer clusters."
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        return result

    X_num = df[numeric_cols].copy()
    y_target = df[target_col].astype(int).values if target_col in df.columns else None

    # Preprocessing: Impute median then Scale
    prep = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    X_scaled = prep.fit_transform(X_num)

    # Determine cluster count k
    k_actual = min(k, max(2, len(df) // 25))
    kmeans = KMeans(n_clusters=k_actual, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    df_clustered = df.copy()
    df_clustered['Cluster'] = clusters

    # Global medians for persona contrast
    global_medians = {col: float(X_num[col].dropna().median()) for col in numeric_cols}

    cluster_summaries = []
    total_customers = len(df)

    for c_id in range(k_actual):
        c_subset = df_clustered[df_clustered['Cluster'] == c_id]
        c_size = len(c_subset)
        c_pct = round(100.0 * c_size / total_customers, 1)

        # Compute medians
        col_medians = {}
        persona_descriptors = []
        for col in numeric_cols:
            c_med = float(c_subset[col].dropna().median())
            col_medians[col] = round(c_med, 2)
            g_med = global_medians[col]
            if g_med > 0:
                ratio = c_med / g_med
                if ratio >= 1.25:
                    persona_descriptors.append(f"High {col}")
                elif ratio <= 0.75:
                    persona_descriptors.append(f"Low {col}")

        # Compute churn rate
        churn_rate = 0.0
        if y_target is not None:
            c_churn = int(c_subset[target_col].astype(int).sum())
            churn_rate = round(100.0 * c_churn / c_size, 1) if c_size > 0 else 0.0

        persona_title = " / ".join(persona_descriptors[:2]) if persona_descriptors else "Balanced / Moderate Usage"
        if churn_rate >= 40.0:
            persona_title = f"High Risk: {persona_title}"
            action_heuristic = "Proactive retention outreach, pricing review, onboarding assistance."
        elif churn_rate <= 12.0:
            persona_title = f"Loyal Core: {persona_title}"
            action_heuristic = "Appreciation incentives, annual renewal bonuses, referral engagement."
        else:
            persona_title = f"Standard: {persona_title}"
            action_heuristic = "Routine health monitoring, engagement check-in, feature education."

        cluster_summaries.append({
            "cluster_id": c_id + 1,
            "persona_title": persona_title,
            "size": c_size,
            "percentage": c_pct,
            "churn_rate": churn_rate,
            "medians": col_medians,
            "suggested_action": action_heuristic
        })

    # Sort clusters by churn rate descending
    cluster_summaries.sort(key=lambda x: x['churn_rate'], reverse=True)

    # Save model and summary
    joblib.dump(kmeans, model_file)
    result = {
        "available": True,
        "k": k_actual,
        "numeric_features": numeric_cols,
        "clusters": cluster_summaries,
        "global_medians": global_medians,
        "total_customers": total_customers
    }

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # Generate visualization plot
    fig, ax = plt.subplots(figsize=(6.2, 4.0), dpi=200)
    c_names = [f"Cluster {c['cluster_id']}\n({c['percentage']}%)" for c in cluster_summaries]
    c_rates = [c['churn_rate'] for c in cluster_summaries]
    bar_colors = ['#ef4444' if r >= 35.0 else ('#f59e0b' if r >= 20.0 else '#0fa37f') for r in c_rates]

    bars = ax.bar(c_names, c_rates, color=bar_colors, width=0.55, alpha=0.85)
    ax.set_ylabel("Observed Churn Rate (%)", fontsize=10, fontweight='bold')
    ax.set_title("Customer Segments Churn Prevalence", fontsize=11, fontweight='bold')
    ax.grid(axis='y', linestyle=':', alpha=0.6)

    for bar, rate in zip(bars, c_rates):
        height = bar.get_height()
        ax.annotate(f"{rate:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plot_path = os.path.join(plots_dir, "segmentation_plot.png")
    plt.savefig(plot_path)
    plt.close()

    print(f"Customer segmentation saved to: {summary_file}")
    return result
