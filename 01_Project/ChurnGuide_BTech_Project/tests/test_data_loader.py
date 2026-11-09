"""
Unit tests for Dynamic Data Ingestion, Schema Inference, and Validation.
Tests both Telecom Public Demo and B2B SaaS Subscriptions schemas,
anti-leakage constraints, duplicate ID detection, and error handling.
"""

import os
import pytest
import numpy as np
import pandas as pd

from src.data_loader import inspect_csv_schema, validate_mapping_and_data, clean_column_data

TELCO_PATH = os.path.join("data", "Telco-Customer-Churn.csv")
SAAS_PATH = os.path.join("data", "saas_customer_churn.csv")

def test_raw_datasets_exist():
    assert os.path.exists(TELCO_PATH), "Provisional Telecom dataset not found in data/."
    assert os.path.exists(SAAS_PATH), "B2B SaaS subscription dataset not found in data/."

def test_inspect_csv_schema_telecom():
    df = pd.read_csv(TELCO_PATH)
    schema = inspect_csv_schema(df)
    
    assert schema["total_rows"] == 7043
    assert schema["total_columns"] == 21
    assert "customerID" in schema["id_candidates"]
    assert "Churn" in schema["target_candidates"]

    # Check TotalCharges profile detects 11 whitespace blanks
    profiles = {p["name"]: p for p in schema["column_profiles"]}
    assert "TotalCharges" in profiles
    assert profiles["TotalCharges"]["missing_count"] == 11
    assert profiles["TotalCharges"]["inferred_type"] == "numeric"
    assert profiles["MonthlyCharges"]["inferred_type"] == "numeric"
    assert profiles["Contract"]["inferred_type"] == "categorical"

def test_inspect_csv_schema_saas():
    df = pd.read_csv(SAAS_PATH)
    schema = inspect_csv_schema(df)

    assert schema["total_rows"] == 1200
    assert schema["total_columns"] == 13
    assert "Account_ID" in schema["id_candidates"]
    assert "Status" in schema["target_candidates"]

    profiles = {p["name"]: p for p in schema["column_profiles"]}
    assert profiles["Monthly_Spend"]["inferred_type"] == "numeric"
    assert profiles["Plan_Tier"]["inferred_type"] == "categorical"
    assert profiles["Status"]["unique_count"] == 2

def test_validate_mapping_and_data_telecom_valid():
    df = pd.read_csv(TELCO_PATH)
    numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    cat_cols = [c for c in df.columns if c not in numeric_cols and c not in ["customerID", "Churn"]]
    features = numeric_cols + cat_cols

    success, errors, cleaned = validate_mapping_and_data(
        df,
        id_col="customerID",
        target_col="Churn",
        pos_val="Yes",
        feature_cols=features,
        numeric_cols=numeric_cols,
        categorical_cols=cat_cols
    )

    assert success is True
    assert len(errors) == 0
    assert cleaned is not None
    assert cleaned["Churn"].nunique() == 2
    assert cleaned["customerID"].nunique() == 7043

def test_validate_mapping_and_data_saas_valid():
    df = pd.read_csv(SAAS_PATH)
    numeric_cols = ["Contract_Age_Months", "User_Licenses", "Monthly_Spend", "Weekly_Active_Users", "Support_Tickets_90d", "Feature_Adoption_Score"]
    cat_cols = ["Plan_Tier", "Company_Size", "Billing_Cycle", "Payment_Method", "Auto_Renew"]
    features = numeric_cols + cat_cols

    success, errors, cleaned = validate_mapping_and_data(
        df,
        id_col="Account_ID",
        target_col="Status",
        pos_val="Churned",
        feature_cols=features,
        numeric_cols=numeric_cols,
        categorical_cols=cat_cols
    )

    assert success is True
    assert len(errors) == 0
    assert cleaned is not None
    assert cleaned["Status"].nunique() == 2
    assert cleaned["Account_ID"].nunique() == 1200

def test_reject_non_binary_target():
    df = pd.DataFrame({
        "ID": [f"ID_{i}" for i in range(100)],
        "Target": ["Low", "Medium", "High"] * 33 + ["Low"],
        "Feature1": np.random.randn(100),
        "Feature2": ["A", "B"] * 50
    })

    success, errors, _ = validate_mapping_and_data(
        df, id_col="ID", target_col="Target", pos_val="High",
        feature_cols=["Feature1", "Feature2"], numeric_cols=["Feature1"], categorical_cols=["Feature2"]
    )
    assert success is False
    assert any("strictly binary" in e for e in errors)

def test_reject_invalid_churn_value():
    df = pd.DataFrame({
        "ID": [f"ID_{i}" for i in range(100)],
        "Target": ["Retained", "Left"] * 50,
        "Feature1": np.random.randn(100),
        "Feature2": ["A", "B"] * 50
    })

    success, errors, _ = validate_mapping_and_data(
        df, id_col="ID", target_col="Target", pos_val="Churned", # Not in values
        feature_cols=["Feature1", "Feature2"], numeric_cols=["Feature1"], categorical_cols=["Feature2"]
    )
    assert success is False
    assert any("was not found in target column" in e for e in errors)

def test_reject_duplicate_ids():
    df = pd.DataFrame({
        "ID": ["CUST_1"] * 50 + [f"CUST_{i}" for i in range(50)], # 49 duplicates
        "Target": ["Yes", "No"] * 50,
        "Feature1": np.random.randn(100),
        "Feature2": ["A", "B"] * 50
    })

    success, errors, _ = validate_mapping_and_data(
        df, id_col="ID", target_col="Target", pos_val="Yes",
        feature_cols=["Feature1", "Feature2"], numeric_cols=["Feature1"], categorical_cols=["Feature2"]
    )
    assert success is False
    assert any("duplicate values" in e for e in errors)

def test_reject_leakage_target_in_features():
    df = pd.DataFrame({
        "ID": [f"ID_{i}" for i in range(100)],
        "Target": ["Yes", "No"] * 50,
        "Feature1": np.random.randn(100),
    })

    success, errors, _ = validate_mapping_and_data(
        df, id_col="ID", target_col="Target", pos_val="Yes",
        feature_cols=["Feature1", "Target"], numeric_cols=["Feature1"], categorical_cols=["Target"]
    )
    assert success is False
    assert any("cannot be included in feature columns" in e for e in errors)

def test_reject_constant_feature():
    df = pd.DataFrame({
        "ID": [f"ID_{i}" for i in range(100)],
        "Target": ["Yes", "No"] * 50,
        "Feature1": np.random.randn(100),
        "ConstantFeat": ["SameValue"] * 100
    })

    success, errors, _ = validate_mapping_and_data(
        df, id_col="ID", target_col="Target", pos_val="Yes",
        feature_cols=["Feature1", "ConstantFeat"], numeric_cols=["Feature1"], categorical_cols=["ConstantFeat"]
    )
    assert success is False
    assert any("constant" in e for e in errors)
