"""
Dynamic Model Explainability and General Retention Heuristics
Implements genuine One-at-a-Time Marginal Perturbation Sensitivity against
training-fold baselines for arbitrary business schemas.
Strictly disclaims causal attribution and labels retention suggestions as heuristics.
"""

import pandas as pd
import numpy as np

def explain_customer_risk(pipeline, customer_row_dict, metadata, business_label="General Business"):
    """
    Computes per-customer feature sensitivity via marginal perturbation
    relative to training-fold typical baseline values.

    Mathematical formulation:
    Delta_P(f) = P(Churn | X_customer) - P(Churn | X_perturbed_without_f)
    where X_perturbed_without_f replaces feature f with its training-fold baseline (median/mode).
    """
    feature_cols = metadata.get("feature_columns", [])
    numeric_cols = metadata.get("numeric_features", [])
    categorical_cols = metadata.get("categorical_features", [])
    baseline_vals = metadata.get("baseline_values", {})
    winner_model = metadata.get("winner_model", "Machine Learning Pipeline")

    # Build full customer row dictionary starting with cohort baselines
    full_customer_dict = dict(baseline_vals)
    for k, v in customer_row_dict.items():
        if k in feature_cols and v is not None and str(v).strip() != "":
            full_customer_dict[k] = v

    # Auto-derive TotalCharges if tenure and MonthlyCharges provided
    if "TotalCharges" in feature_cols:
        cust_tc = customer_row_dict.get("TotalCharges")
        if cust_tc is None or str(cust_tc).strip() == "":
            try:
                t = float(full_customer_dict.get("tenure", 1))
                m = float(full_customer_dict.get("MonthlyCharges", 50))
                full_customer_dict["TotalCharges"] = round(t * m, 2)
            except Exception:
                pass

    def prepare_clean_df(row_dict):
        df_row = pd.DataFrame([row_dict])[feature_cols].copy()
        for c in numeric_cols:
            if c in df_row.columns:
                df_row[c] = pd.to_numeric(df_row[c], errors="coerce").fillna(baseline_vals.get(c, 0.0))
        for c in categorical_cols:
            if c in df_row.columns:
                df_row[c] = df_row[c].astype(str).str.strip()
        return df_row

    # Construct clean DataFrames
    customer_df = prepare_clean_df(full_customer_dict)
    baseline_df = prepare_clean_df(baseline_vals)

    # Predicted probability for this customer directly from scikit-learn Pipeline
    probs = pipeline.predict_proba(customer_df)[0]
    full_prob = float(probs[1])

    # Predicted probability for baseline typical customer
    try:
        base_prob = float(pipeline.predict_proba(baseline_df)[0, 1])
    except Exception:
        base_prob = 0.50

    # Risk level classification based on empirical probability thresholds
    if full_prob >= 0.60:
        risk_level = "High"
        badge_class = "badge-danger"
    elif full_prob >= 0.35:
        risk_level = "Medium"
        badge_class = "badge-warning"
    else:
        risk_level = "Low"
        badge_class = "badge-success"

    # Compute genuine marginal sensitivities for each feature
    sensitivities = []
    for col in feature_cols:
        val_customer = full_customer_dict.get(col)
        val_baseline = baseline_vals.get(col)

        # Skip if identical to baseline
        if str(val_customer).strip().lower() == str(val_baseline).strip().lower():
            continue

        # Perturb: replace col with baseline value in customer's row
        perturbed_dict = dict(full_customer_dict)
        perturbed_dict[col] = val_baseline
        if col in ["tenure", "MonthlyCharges"] and "TotalCharges" in feature_cols:
            try:
                perturbed_dict["TotalCharges"] = round(float(perturbed_dict.get("tenure", 1)) * float(perturbed_dict.get("MonthlyCharges", 50)), 2)
            except Exception:
                pass

        perturbed_df = prepare_clean_df(perturbed_dict)

        try:
            perturbed_prob = float(pipeline.predict_proba(perturbed_df)[0, 1])
            delta_prob = full_prob - perturbed_prob
        except Exception:
            delta_prob = 0.0

        if abs(delta_prob) > 0.002:
            sensitivities.append({
                "feature": col,
                "customer_value": str(val_customer),
                "original_value": str(val_customer),
                "baseline_value": str(val_baseline),
                "delta_p": round(delta_prob, 4),
                "delta_p_pct": round(delta_prob * 100.0, 1),
                "impact_prob": round(delta_prob, 4),
                "direction": "increases_risk" if delta_prob > 0 else "decreases_risk",
                "direction_label": "Increases Risk" if delta_prob > 0 else "Reduces Risk",
                "interpretation": f"Alters churn probability by {'+' if delta_prob > 0 else ''}{round(delta_prob * 100.0, 1)}% relative to cohort baseline ({val_baseline})."
            })

    # Sort by impact
    sensitivities.sort(key=lambda x: x["impact_prob"], reverse=True)

    # Top risk factors and protective factors
    top_drivers = [s for s in sensitivities if s["impact_prob"] > 0][:3]
    protective_drivers = [s for s in sensitivities if s["impact_prob"] < 0][:2]

    # Generate generic business review heuristics (labeled explicitly as heuristics)
    heuristics = []
    if risk_level in ["High", "Medium"]:
        heuristics.append("Schedule a dedicated proactive account review with a relationship manager before the next billing cycle.")
        
        # Domain or feature-aware non-causal review suggestions
        for d in top_drivers[:2]:
            f_name = d["feature"].lower()
            if any(k in f_name for k in ['tenure', 'contract_age', 'age', 'month']):
                heuristics.append("Provide structured onboarding assistance and early-lifecycle engagement checkups.")
            elif any(k in f_name for k in ['spend', 'charge', 'price', 'fee', 'bill']):
                heuristics.append("Audit pricing transparency, explore tailored billing schedules, or assess discount eligibility.")
            elif any(k in f_name for k in ['adoption', 'usage', 'hour', 'activity']):
                heuristics.append("Offer product education or technical enablement sessions to drive active feature engagement.")
            elif any(k in f_name for k in ['ticket', 'support', 'complaint', 'incident']):
                heuristics.append("Review open or recent customer support interactions to resolve lingering operational friction.")
            elif any(k in f_name for k in ['contract', 'renew', 'tier']):
                heuristics.append("Explore mutual term commitments with annual renewal incentives or upgrade consultation.")

        if len(heuristics) < 2:
            heuristics.append(f"Conduct a holistic account satisfaction review aligned with standard {business_label} retention practices.")
    else:
        heuristics.append("Account displays healthy engagement signals. Maintain standard customer success touchpoints.")
        heuristics.append("Consider inviting the customer to participate in product feedback panels or loyalty appreciation programs.")

    return {
        "churn_probability": round(full_prob, 4),
        "probability": round(full_prob, 4),
        "probability_percentage": round(full_prob * 100.0, 1),
        "percentage": round(full_prob * 100.0, 1),
        "baseline_probability": round(base_prob, 4),
        "risk_level": risk_level,
        "level": risk_level,
        "badge_class": badge_class,
        "attribution_method": "One-at-a-Time Marginal Perturbation Sensitivity against Training-Fold Baseline",
        "method_label": "Model Sensitivity Associations (local perturbation relative to typical customer baseline; general statistical associations, not causes)",
        "top_drivers": top_drivers,
        "top_risk_drivers": top_drivers,
        "protective_drivers": protective_drivers,
        "all_sensitivities": sensitivities,
        "heuristics": heuristics,
        "suggested_actions": heuristics,
        "heuristics_label": "Suggested Review Considerations (general business heuristics; not learned causal interventions)"
    }
