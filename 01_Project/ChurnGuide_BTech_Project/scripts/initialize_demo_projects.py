"""
Initialize and Pre-train Default Demo Projects
1. Telecom Public Sample Demo (provisional public sample, IBM Telco dataset)
2. B2B SaaS Subscription Demo (SYNTHETIC fixture for software plumbing verification)
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import pandas as pd
from src.project_manager import BASE_PROJECTS_DIR, set_active_project_id
from src.data_loader import validate_mapping_and_data
from src.train_experiment import train_and_evaluate_project
from src.segmentation import run_project_segmentation

def initialize_telecom_demo():
    proj_id = "telecom_public_demo"
    proj_dir = os.path.join(BASE_PROJECTS_DIR, proj_id)
    os.makedirs(proj_dir, exist_ok=True)
    
    print("\n--- Initializing Telecom Public Sample Demo ---")
    data_path = os.path.join("data", "Telco-Customer-Churn.csv")
    df_raw = pd.read_csv(data_path)
    
    id_col = "customerID"
    target_col = "Churn"
    pos_val = "Yes"
    
    numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    categorical_cols = [
        "gender", "SeniorCitizen", "Partner", "Dependents", "PhoneService",
        "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
        "Contract", "PaperlessBilling", "PaymentMethod"
    ]
    feature_cols = numeric_cols + categorical_cols
    
    # Validate and clean
    is_valid, errors, cleaned_df = validate_mapping_and_data(
        df_raw, id_col, target_col, pos_val, feature_cols, numeric_cols, categorical_cols
    )
    if not is_valid:
        raise RuntimeError(f"Telecom demo validation failed: {errors}")
        
    config = {
        "id": proj_id,
        "name": "Telecom Customer Services",
        "business_label": "Telecommunications",
        "churn_definition": "Customer disconnected service or terminated monthly subscription",
        "outcome_window": "30 days post-observation",
        "id_column": id_col,
        "target_column": target_col,
        "positive_target_value": pos_val,
        "feature_columns": feature_cols,
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
        "pre_outcome_confirmed": True,
        "provenance_note": "Provisional public sample derived from IBM Telco Customer Churn dataset (Apache-2.0 repository license noted).",
        "is_demo": True
    }
    
    with open(os.path.join(proj_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        
    df_raw.to_csv(os.path.join(proj_dir, "dataset.csv"), index=False)
    
    # Train
    train_and_evaluate_project(
        cleaned_df, target_col, id_col, numeric_cols, categorical_cols, proj_dir
    )
    
    # Segmentation
    run_project_segmentation(
        cleaned_df, target_col, numeric_cols, proj_dir, k=4
    )
    print("Telecom Public Sample Demo initialized successfully!")

def initialize_saas_demo():
    proj_id = "saas_b2b_demo"
    proj_dir = os.path.join(BASE_PROJECTS_DIR, proj_id)
    os.makedirs(proj_dir, exist_ok=True)
    
    print("\n--- Initializing B2B SaaS Subscription Demo ---")
    data_path = os.path.join("data", "saas_customer_churn.csv")
    df_raw = pd.read_csv(data_path)
    
    id_col = "Account_ID"
    target_col = "Status"
    pos_val = "Churned"
    
    numeric_cols = [
        "Contract_Age_Months", "User_Licenses", "Monthly_Spend",
        "Weekly_Active_Users", "Support_Tickets_90d", "Feature_Adoption_Score"
    ]
    categorical_cols = [
        "Plan_Tier", "Company_Size", "Billing_Cycle", "Payment_Method", "Auto_Renew"
    ]
    feature_cols = numeric_cols + categorical_cols
    
    # Validate and clean
    is_valid, errors, cleaned_df = validate_mapping_and_data(
        df_raw, id_col, target_col, pos_val, feature_cols, numeric_cols, categorical_cols
    )
    if not is_valid:
        raise RuntimeError(f"SaaS demo validation failed: {errors}")
        
    config = {
        "id": proj_id,
        "name": "B2B Cloud SaaS Platform",
        "business_label": "B2B Cloud Software",
        "churn_definition": "Account canceled recurring software subscription or lapsed after contract term",
        "outcome_window": "Quarterly renewal observation cycle",
        "id_column": id_col,
        "target_column": target_col,
        "positive_target_value": pos_val,
        "feature_columns": feature_cols,
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
        "pre_outcome_confirmed": True,
        "provenance_note": "SYNTHETIC B2B SaaS Subscription Fixture (generated strictly to test cross-domain schema flexibility and software plumbing; not real enterprise validation).",
        "is_demo": True
    }
    
    with open(os.path.join(proj_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        
    df_raw.to_csv(os.path.join(proj_dir, "dataset.csv"), index=False)
    
    # Train
    train_and_evaluate_project(
        cleaned_df, target_col, id_col, numeric_cols, categorical_cols, proj_dir
    )
    
    # Segmentation
    run_project_segmentation(
        cleaned_df, target_col, numeric_cols, proj_dir, k=4
    )
    print("B2B SaaS Subscription Demo initialized successfully!")

if __name__ == "__main__":
    initialize_telecom_demo()
    initialize_saas_demo()
    # Set default active to telecom demo
    set_active_project_id("telecom_public_demo")
    print("\nAll demo projects initialized and active project set to 'telecom_public_demo'!")

