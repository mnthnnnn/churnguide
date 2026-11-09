"""
Unit tests for Explainability (Marginal Perturbation), Project Isolation,
Customer Segmentation, and Flask Web Endpoints.
"""

import os
import pytest
import pandas as pd
import numpy as np

from app import app
from src.project_manager import (
    get_project, list_projects, set_active_project_id,
    get_active_project_id, get_active_project
)
from src.segmentation import run_project_segmentation

@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_project_listing_and_isolation():
    projs = list_projects()
    proj_ids = [p["id"] for p in projs]
    assert "telecom_public_demo" in proj_ids
    assert "saas_b2b_demo" in proj_ids

    # Switch project and verify active ID persists
    set_active_project_id("saas_b2b_demo")
    assert get_active_project_id() == "saas_b2b_demo"
    assert get_active_project().project_id == "saas_b2b_demo"

    set_active_project_id("telecom_public_demo")
    assert get_active_project_id() == "telecom_public_demo"

def test_explain_customer_marginal_sensitivity():
    proj = get_project("telecom_public_demo")
    metadata = proj.get_metadata()
    baseline = metadata["baseline_values"]

    # Test baseline perturbation with high-risk modifications
    customer_dict = dict(baseline)
    customer_dict["Contract"] = "Month-to-month"
    customer_dict["tenure"] = 1.0
    customer_dict["MonthlyCharges"] = 100.0

    result = proj.explain_customer(customer_dict)

    assert "probability" in result
    assert 0.0 <= result["probability"] <= 1.0
    assert result["level"] in ["Low", "Medium", "High"]
    assert "top_risk_drivers" in result
    assert len(result["top_risk_drivers"]) > 0

    driver = result["top_risk_drivers"][0]
    assert "feature" in driver
    assert "delta_p" in driver
    assert "direction" in driver
    assert "suggested_actions" in result

def test_bulk_scoring_unlabelled_csv():
    proj = get_project("telecom_public_demo")
    unlabeled_path = os.path.join("data", "telco_scoring_unlabeled.csv")
    assert os.path.exists(unlabeled_path)

    df_unlabeled = pd.read_csv(unlabeled_path).head(30)
    assert "Churn" not in df_unlabeled.columns # Strictly unlabelled

    scored = proj.score_dataframe(df_unlabeled)

    assert "Predicted_Churn_Probability" in scored.columns
    assert "Risk_Level" in scored.columns
    assert len(scored) == 30
    assert (scored["Predicted_Churn_Probability"] >= 0.0).all()
    assert (scored["Predicted_Churn_Probability"] <= 1.0).all()
    assert set(scored["Risk_Level"].unique()).issubset({"Low", "Medium", "High"})

def test_segmentation_honest_fallback_when_features_insufficient():
    # Provide only 1 numeric feature
    df_single_num = pd.DataFrame({
        "Feature1": [10, 20, 30, 40, 50] * 10,
        "Churn": [0, 1] * 25
    })
    temp_dir = os.path.join("tests", "temp_seg")
    res = run_project_segmentation(df_single_num, target_col="Churn", numeric_cols=["Feature1"], output_dir=temp_dir)

    assert res["available"] is False
    assert "Customer segmentation requires at least two continuous numerical metrics" in res["reason"]

def test_flask_navigation_and_pages(test_client):
    set_active_project_id("telecom_public_demo")

    # Index redirects to step3 when project active
    r_idx = test_client.get("/")
    assert r_idx.status_code == 302

    # Step 1
    r_step1 = test_client.get("/wizard/step1")
    assert r_step1.status_code == 200
    assert b"Find customers likely to leave" in r_step1.data

    # Step 3
    r_step3 = test_client.get("/wizard/step3")
    assert r_step3.status_code == 200
    assert b"Your results" in r_step3.data
    assert b"Gradient Boosting" in r_step3.data

    # Predict page GET
    r_pred = test_client.get("/predict")
    assert r_pred.status_code == 200
    assert b"Check one customer" in r_pred.data

    # Predict page POST
    proj = get_project("telecom_public_demo")
    sample_data = dict(proj.get_metadata()["baseline_values"])
    r_pred_post = test_client.post("/predict", data=sample_data)
    assert r_pred_post.status_code == 200
    assert b"Estimated Churn Probability" in r_pred_post.data

    # Bulk scoring GET
    r_bulk = test_client.get("/bulk")
    assert r_bulk.status_code == 200
    assert b"Bulk Customer Scoring" in r_bulk.data

    # Bulk scoring POST with demo batch
    r_bulk_post = test_client.post("/bulk", data={"use_demo_sample": "1"})
    assert r_bulk_post.status_code == 200
    assert b"Bulk Scoring Results" in r_bulk_post.data

    # Download scored CSV
    r_dl = test_client.get("/download_scored")
    assert r_dl.status_code == 200
    assert "text/csv" in r_dl.content_type

    # Customer Analytics
    r_analytics = test_client.get("/analytics")
    assert r_analytics.status_code == 200
    assert b"Customer Portfolio Analytics" in r_analytics.data

    # Customer Segments
    r_segments = test_client.get("/segments")
    assert r_segments.status_code == 200
    assert b"Customer Groups &amp; Segmentation" in r_segments.data

    # Model Report
    r_model = test_client.get("/model")
    assert r_model.status_code == 200
    assert b"Model Evaluation &amp; Transparency" in r_model.data
    assert b"Held-Out Test Set Performance" in r_model.data

    # Project Plots Serving
    r_plot = test_client.get("/project/plots/confusion_matrix.png")
    assert r_plot.status_code == 200
    assert "image/png" in r_plot.content_type

    # Switch project to SaaS B2B
    r_switch = test_client.get("/projects/switch/saas_b2b_demo?redirect=predict")
    assert r_switch.status_code == 302
    assert get_active_project_id() == "saas_b2b_demo"

    # Verify predict page now renders SaaS fields
    r_pred_saas = test_client.get("/predict")
    assert r_pred_saas.status_code == 200
    assert b"B2B Cloud SaaS Platform" in r_pred_saas.data
    assert b"Weekly_Active_Users" in r_pred_saas.data

    # Reset active back to telecom
    set_active_project_id("telecom_public_demo")
