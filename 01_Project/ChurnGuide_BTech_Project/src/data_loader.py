"""
Dynamic Tabular Data Ingestion, Schema Inference, and Validation
Supports arbitrary business tabular snapshots with binary churn outcomes.
Guarantees zero silent leakage and strict schema compliance.
"""

import pandas as pd
import numpy as np

def inspect_csv_schema(df):
    """
    Analyzes an uploaded dataframe and infers column types, missingness,
    cardinality, and potential target/ID candidates.
    Returns a comprehensive structured schema profile.
    """
    total_rows = len(df)
    schema_info = []
    target_candidates = []
    id_candidates = []

    for col in df.columns:
        series = df[col]
        clean_s = series.astype(str).str.strip()
        is_missing = series.isna() | clean_s.isin(["", "nan", "NaN", "None", "null", "NULL", "NA"])
        missing_count = int(is_missing.sum())
        missing_pct = round(100.0 * missing_count / total_rows, 1) if total_rows > 0 else 0.0

        valid_series = series[~is_missing]
        unique_vals = valid_series.unique()
        cardinality = len(unique_vals)
        sample_vals = [str(v) for v in unique_vals[:3]]
        unique_samples = [str(v) for v in unique_vals[:12]]

        # Type inference
        col_lower = str(col).lower()
        is_id_candidate = False
        is_target_candidate = False

        # Attempt numeric conversion check
        is_numeric = False
        if pd.api.types.is_numeric_dtype(series):
            is_numeric = True
        else:
            # Try coercing to numeric to see if numbers are stored as strings (like TotalCharges)
            coerced = pd.to_numeric(clean_s, errors='coerce')
            valid_num_count = coerced.notna().sum()
            if total_rows > 0 and (valid_num_count / total_rows) > 0.85 and cardinality > 10:
                is_numeric = True

        # Candidate heuristics
        has_id_keyword = any(term in col_lower for term in ['id', 'uuid', 'key', 'code', 'customer_id', 'account_id', 'customerid'])
        if has_id_keyword and cardinality > (0.5 * total_rows):
            is_id_candidate = True
            id_candidates.append(col)
        elif cardinality == total_rows and total_rows > 50 and not is_numeric:
            is_id_candidate = True
            id_candidates.append(col)

        has_churn_keyword = any(term in col_lower for term in ['churn', 'status', 'target', 'label', 'attrition', 'left', 'exited', 'cancel'])
        if cardinality == 2 and has_churn_keyword:
            is_target_candidate = True
            target_candidates.append(col)
        elif cardinality == 2 and not is_id_candidate:
            # Fallback binary column
            is_target_candidate = True

        inferred_type = "numeric" if is_numeric else "categorical"
        is_constant = cardinality <= 1
        is_all_empty = missing_count == total_rows
        is_excessive_cardinality = (not is_numeric) and cardinality > 100 and (not is_id_candidate)

        schema_info.append({
            "name": col,
            "inferred_type": inferred_type,
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "cardinality": cardinality,
            "unique_count": cardinality,
            "sample_values": sample_vals,
            "unique_samples": unique_samples,
            "is_id_candidate": is_id_candidate,
            "is_target_candidate": is_target_candidate,
            "is_constant": is_constant,
            "is_all_empty": is_all_empty,
            "is_excessive_cardinality": is_excessive_cardinality
        })

    # Pick single primary target (prioritize churn keywords)
    strong_targets = [p["name"] for p in schema_info if p["cardinality"] == 2 and any(k in str(p["name"]).lower() for k in ['churn', 'status', 'target', 'label', 'attrition', 'left', 'exited', 'cancel'])]
    all_binary = [p["name"] for p in schema_info if p["cardinality"] == 2]
    primary_target = strong_targets[0] if strong_targets else (all_binary[0] if all_binary else None)

    # Pick single primary ID candidate
    primary_id = id_candidates[0] if id_candidates else None

    # Update primary flags in profiles
    for p in schema_info:
        p["is_primary_target"] = (p["name"] == primary_target)
        p["is_primary_id"] = (p["name"] == primary_id)
        # Only mark as target candidate if it's the primary target or a strong target candidate
        if strong_targets:
            p["is_target_candidate"] = (p["name"] in strong_targets)
        else:
            p["is_target_candidate"] = (p["cardinality"] == 2)

    return {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "column_profiles": schema_info,
        "target_candidates": strong_targets if strong_targets else all_binary,
        "id_candidates": id_candidates,
        "primary_target": primary_target,
        "primary_id": primary_id
    }

def clean_column_data(series, col_type):
    """Clean and standardize a single column series based on confirmed type."""
    if col_type == "numeric":
        # Strip whitespace, coerce to float, replace inf with NaN
        cleaned = pd.to_numeric(series.astype(str).str.strip(), errors='coerce')
        cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
        return cleaned
    else:
        # Categorical: clean whitespace, treat empty as NaN
        cleaned = series.astype(str).str.strip()
        cleaned = cleaned.replace({"": np.nan, "nan": np.nan, "None": np.nan, "null": np.nan})
        return cleaned

def validate_mapping_and_data(df, id_col, target_col, pos_val, feature_cols, numeric_cols, categorical_cols):
    """
    Validates user mapping, checks binary target requirements, prevents leakage,
    and returns a clean, typed dataframe ready for modeling.
    """
    errors = []

    # 1. Dataset size validation
    if len(df) < 50:
        errors.append("Dataset must contain at least 50 customer rows for reliable cross-validation and evaluation.")

    # 2. Duplicate column names validation
    if len(df.columns) != len(set(df.columns)):
        errors.append("CSV contains duplicate column names. Ensure all column headers are unique.")

    # 3. Target column validation
    if not target_col or target_col not in df.columns:
        errors.append("A valid Target Column indicating customer churn outcome must be selected.")
        return False, errors, None

    target_series = df[target_col].dropna()
    unique_target_vals = [str(v).strip() for v in target_series.unique() if str(v).strip() != ""]

    if len(unique_target_vals) != 2:
        errors.append(f"Target column '{target_col}' must be strictly binary (exactly 2 distinct classes). "
                      f"Detected {len(unique_target_vals)} values: {unique_target_vals[:5]}. "
                      f"Multi-class or continuous target columns are not supported.")
        return False, errors, None

    # 4. Positive churn value validation
    if not pos_val or str(pos_val).strip() not in unique_target_vals:
        errors.append(f"Specified Churn Value '{pos_val}' was not found in target column '{target_col}'. "
                      f"Available values are: {unique_target_vals}.")

    # 5. Class balance and minimum count validation
    # Map target to binary 0/1
    binary_target = df[target_col].astype(str).str.strip().apply(lambda x: 1 if x == str(pos_val).strip() else (0 if x in unique_target_vals else np.nan))
    missing_target_count = binary_target.isna().sum()
    if missing_target_count > 0:
        errors.append(f"Target column contains {missing_target_count} missing or unrecognized values. "
                      f"All training rows must possess a confirmed binary outcome.")

    class_counts = binary_target.value_counts()
    churn_count = class_counts.get(1, 0)
    retained_count = class_counts.get(0, 0)

    if churn_count < 10 or retained_count < 10:
        errors.append(f"Insufficient samples per class for stratified 5-fold cross-validation. "
                      f"Churners: {churn_count}, Retained: {retained_count}. Both classes require at least 10 instances.")

    # 6. ID column validation
    if id_col and id_col != "none":
        if id_col not in df.columns:
            errors.append(f"Selected ID column '{id_col}' does not exist in the dataset.")
        else:
            id_series = df[id_col].dropna()
            if len(id_series) != len(id_series.unique()):
                dup_count = len(id_series) - len(id_series.unique())
                errors.append(f"Selected ID column '{id_col}' contains {dup_count} duplicate values. "
                              f"Customer ID must be unique per historical snapshot row.")

    # 7. Feature selection validation
    if not feature_cols or len(feature_cols) < 2:
        errors.append("At least two feature columns must be selected to build a predictive model.")

    if target_col in feature_cols:
        errors.append(f"Target column '{target_col}' cannot be included in feature columns (prevents direct label leakage).")

    if id_col and id_col in feature_cols:
        errors.append(f"ID column '{id_col}' cannot be included in feature columns (identifiers do not generalize).")

    # 8. Feature cleaning and type validation
    cleaned_df = pd.DataFrame()
    cleaned_df[target_col] = binary_target

    if id_col and id_col != "none" and id_col in df.columns:
        cleaned_df[id_col] = df[id_col].astype(str).str.strip()

    for col in feature_cols:
        if col not in df.columns:
            errors.append(f"Feature column '{col}' does not exist in dataset.")
            continue

        raw_series = df[col]
        col_type = "numeric" if col in numeric_cols else "categorical"

        cleaned_col = clean_column_data(raw_series, col_type)

        # Check for 100% missing
        if cleaned_col.isna().all():
            errors.append(f"Feature column '{col}' is entirely empty / missing. Remove this column from features.")
            continue

        # Check for zero variance (constant value)
        valid_vals = cleaned_col.dropna().unique()
        if len(valid_vals) <= 1:
            errors.append(f"Feature column '{col}' is constant (has only 1 unique value: {valid_vals}). "
                          f"Constant features carry no predictive signal; remove from features.")
            continue

        # High cardinality categorical check
        if col_type == "categorical" and len(valid_vals) > 100:
            errors.append(f"Categorical feature '{col}' has {len(valid_vals)} unique values (exceeds limit of 100). "
                          f"High-cardinality text (names, notes, free text) cannot be modeled reliably with one-hot encoding.")
            continue

        cleaned_df[col] = cleaned_col

    if errors:
        return False, errors, None

    return True, [], cleaned_df
