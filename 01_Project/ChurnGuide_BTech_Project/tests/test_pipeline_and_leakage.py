"""
Unit tests for Pipeline isolation and data leakage prevention.
Verifies that test partition rows never influence preprocessing statistics,
imputation medians, scaling parameters, or model fitting.
"""

import os
import pytest
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from src.train_experiment import build_preprocessor
from src.project_manager import get_project

TELCO_PATH = os.path.join("data", "Telco-Customer-Churn.csv")

def test_zero_leakage_in_preprocessing():
    """
    Strict Leakage Test:
    Verify that ColumnTransformer fits exclusively on X_train.
    Verify that changing X_test values does NOT alter training statistics.
    """
    df = pd.read_csv(TELCO_PATH)
    numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    cat_cols = ["Contract", "InternetService", "PaymentMethod"]
    features = df[numeric_cols + cat_cols].copy()
    
    # Coerce TotalCharges blanks to NaN
    features["TotalCharges"] = pd.to_numeric(features["TotalCharges"].astype(str).str.strip(), errors="coerce")
    target = (df["Churn"] == "Yes").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.20, random_state=42, stratify=target
    )

    preprocessor = build_preprocessor(numeric_cols, cat_cols)

    # Fit ONLY on training partition
    preprocessor.fit(X_train)

    num_imputer = preprocessor.named_transformers_['num'].named_steps['imputer']
    num_scaler = preprocessor.named_transformers_['num'].named_steps['scaler']

    # Recorded statistics from training partition
    train_medians = num_imputer.statistics_
    train_means = num_scaler.mean_
    train_scales = num_scaler.scale_

    # Verify that training medians match the true X_train medians
    expected_medians = X_train[numeric_cols].median().values
    np.testing.assert_allclose(train_medians, expected_medians, err_msg="Imputer did not use X_train medians.")

    # Now transform a synthetic test set with extreme outliers and missing values
    extreme_test = X_test.copy()
    extreme_test['MonthlyCharges'] = 999999.0
    extreme_test['TotalCharges'] = np.nan # Test row missing TotalCharges

    # Transform extreme test
    trans_extreme = preprocessor.transform(extreme_test)

    # Verify that imputer used the training median to impute the extreme test row's missing TotalCharges
    # TotalCharges is at index 2 in numeric_cols: (train_median - train_mean) / train_scale
    expected_imputed_scaled = (train_medians[2] - train_means[2]) / train_scales[2]
    np.testing.assert_allclose(trans_extreme[:, 2], expected_imputed_scaled, err_msg="Leakage! Test imputation did not use training median.")

def test_categorical_unseen_levels_no_crash():
    """Verify that unseen categories in test or inference do not crash the pipeline."""
    numeric_cols = ["tenure"]
    cat_cols = ["Contract"]

    train_df = pd.DataFrame({
        "tenure": [12, 24, 36],
        "Contract": ["Month-to-month", "One year", "Two year"]
    })

    test_unseen = pd.DataFrame({
        "tenure": [6],
        "Contract": ["Three-Year-Special-Enterprise-Deal"] # Completely new category
    })

    prep = build_preprocessor(numeric_cols, cat_cols)
    prep.fit(train_df)

    # Should transform without exception
    transformed = prep.transform(test_unseen)
    assert transformed.shape[0] == 1
    # Category columns (after the numeric column) should all be 0 for unknown category
    assert np.all(transformed[0, 1:] == 0.0)

def test_saved_demo_pipelines_predict_proba():
    """Verify pre-trained demo pipelines produce calibrated probabilities between 0.0 and 1.0."""
    for proj_id in ["telecom_public_demo", "saas_b2b_demo"]:
        proj = get_project(proj_id)
        assert proj.exists(), f"Project {proj_id} must exist."
        
        pipeline = proj.get_pipeline()
        dataset = proj.get_dataset()
        config = proj.get_config()
        
        features = dataset[config["numeric_features"] + config["categorical_features"]].head(25)
        probs = pipeline.predict_proba(features)

        assert probs.shape == (25, 2)
        assert (probs >= 0.0).all() and (probs <= 1.0).all()
        np.testing.assert_allclose(probs.sum(axis=1), np.ones(25))
