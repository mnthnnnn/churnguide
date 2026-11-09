"""
Project Management and Model Isolation Engine
Coordinates project directory lifecycle, dataset immutability,
active project state persistence, and cross-project switching.
"""

import os
import json
import shutil
import uuid
import pandas as pd
import joblib

from src.data_loader import validate_mapping_and_data, inspect_csv_schema

BASE_PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "projects"))
ACTIVE_FILE = os.path.join(BASE_PROJECTS_DIR, "active_project.json")

class Project:
    def __init__(self, project_id):
        self.project_id = project_id
        self.project_dir = os.path.join(BASE_PROJECTS_DIR, project_id)
        self.config_path = os.path.join(self.project_dir, "config.json")
        self.dataset_path = os.path.join(self.project_dir, "dataset.csv")
        self.pipeline_path = os.path.join(self.project_dir, "pipeline.joblib")
        self.metadata_path = os.path.join(self.project_dir, "metadata.json")
        self.segmentation_path = os.path.join(self.project_dir, "segmentation.json")
        self.plots_dir = os.path.join(self.project_dir, "plots")
        self._config = None
        self._metadata = None
        self._pipeline = None

    def exists(self):
        return os.path.exists(self.config_path) and os.path.exists(self.pipeline_path)

    def get_config(self):
        if self._config is None:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        return self._config

    def get_dataset(self):
        if os.path.exists(self.dataset_path):
            return pd.read_csv(self.dataset_path)
        return None

    def get_metadata(self):
        if self._metadata is None:
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)
            else:
                self._metadata = {}

        if self._metadata:
            if "total_customers" not in self._metadata:
                self._metadata["total_customers"] = self._metadata.get("train_rows", 0) + self._metadata.get("test_rows", 0)
            if "churn_rate_pct" not in self._metadata:
                rate = self._metadata.get("churn_rate_train", 0.0)
                self._metadata["churn_rate_pct"] = round(rate * 100.0, 1)
            raw_top = self._metadata.get("permutation_importance", [])
            mapped_top = []
            for item in raw_top:
                mapped_top.append({
                    "feature": item.get("feature"),
                    "importance": item.get("importance", item.get("mean_decrease", 0.0)),
                    "rank": item.get("rank", 1),
                    "is_numeric": item.get("is_numeric", True)
                })
            self._metadata["top_features"] = mapped_top
            if "cv_results" not in self._metadata:
                cv_res = {}
                for algo, info in self._metadata.get("cv_scores", {}).items():
                    cv_res[algo] = {
                        "best_params": info.get("params", {}),
                        "best_cv_roc_auc": info.get("mean_auc", 0.0),
                        "cv_std_roc_auc": info.get("std_auc", 0.0),
                        "is_winner": algo == self._metadata.get("winner_model")
                    }
                self._metadata["cv_results"] = cv_res

        return self._metadata

    def get_pipeline(self):
        if self._pipeline is None:
            if os.path.exists(self.pipeline_path):
                self._pipeline = joblib.load(self.pipeline_path)
            else:
                self._pipeline = None
        return self._pipeline

    def get_segmentation(self):
        if os.path.exists(self.segmentation_path):
            with open(self.segmentation_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"available": False, "reason": "No segmentation model found for this project."}

    def score_dataframe(self, df_unlabeled):
        """
        Scores a customer dataframe using this project's trained pipeline.
        Crucial requirement: Does NOT require the target column!
        Appends Predicted_Churn_Probability and Risk_Level.
        """
        config = self.get_config()
        feature_cols = config.get("feature_columns", [])
        numeric_cols = config.get("numeric_features", [])
        categorical_cols = config.get("categorical_features", [])

        # Clean and normalize column names (strip whitespace and match case-insensitively)
        df_clean = df_unlabeled.copy()
        df_clean.columns = [str(c).strip() for c in df_clean.columns]
        
        col_lookup = {str(c).lower(): c for c in df_clean.columns}
        rename_map = {}
        for req_col in feature_cols:
            if req_col not in df_clean.columns and req_col.lower() in col_lookup:
                rename_map[col_lookup[req_col.lower()]] = req_col
        if rename_map:
            df_clean = df_clean.rename(columns=rename_map)

        # Validate that all required feature columns exist
        missing_cols = [c for c in feature_cols if c not in df_clean.columns]
        if missing_cols:
            raise ValueError(f"Uploaded CSV is missing {len(missing_cols)} required feature column(s): {missing_cols[:5]}. "
                             f"Expected feature schema: {feature_cols}")

        pipeline = self.get_pipeline()
        if pipeline is None:
            raise RuntimeError(f"Model pipeline for project '{self.project_id}' is not loaded.")

        X = df_clean[feature_cols].copy()

        # Clean types
        for col in numeric_cols:
            X[col] = pd.to_numeric(X[col].astype(str).str.strip(), errors='coerce')
        for col in categorical_cols:
            X[col] = X[col].astype(str).str.strip()

        probs = pipeline.predict_proba(X)[:, 1]

        scored_df = df_clean.copy()
        scored_df["Predicted_Churn_Probability"] = [round(float(p), 4) for p in probs]

        risk_levels = []
        for p in probs:
            if p >= 0.65:
                risk_levels.append("High")
            elif p >= 0.35:
                risk_levels.append("Medium")
            else:
                risk_levels.append("Low")

        scored_df["Risk_Level"] = risk_levels
        return scored_df

    def explain_customer(self, customer_row_dict):
        from src.explain import explain_customer_risk
        pipeline = self.get_pipeline()
        metadata = self.get_metadata()
        config = self.get_config()
        biz_label = config.get("business_label", "General Business")
        return explain_customer_risk(pipeline, customer_row_dict, metadata, biz_label)

def list_projects():
    """Returns a list of all existing projects with their configuration."""
    os.makedirs(BASE_PROJECTS_DIR, exist_ok=True)
    projects = []

    for name in sorted(os.listdir(BASE_PROJECTS_DIR)):
        proj_dir = os.path.join(BASE_PROJECTS_DIR, name)
        config_file = os.path.join(proj_dir, "config.json")
        pipeline_file = os.path.join(proj_dir, "pipeline.joblib")
        if os.path.isdir(proj_dir) and os.path.exists(config_file) and os.path.exists(pipeline_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                projects.append(cfg)
            except Exception:
                continue

    return projects

_IN_MEMORY_ACTIVE_ID = None

def get_active_project_id():
    """Reads the active project ID from active_project.json."""
    global _IN_MEMORY_ACTIVE_ID
    if _IN_MEMORY_ACTIVE_ID:
        return _IN_MEMORY_ACTIVE_ID

    try:
        os.makedirs(BASE_PROJECTS_DIR, exist_ok=True)
        if os.path.exists(ACTIVE_FILE):
            with open(ACTIVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                proj_id = data.get("active_project_id")
                if proj_id and os.path.exists(os.path.join(BASE_PROJECTS_DIR, proj_id, "config.json")):
                    _IN_MEMORY_ACTIVE_ID = proj_id
                    return proj_id
    except Exception:
        pass

    # Fallback to first available project
    all_p = list_projects()
    if all_p:
        first_id = all_p[0]["id"]
        _IN_MEMORY_ACTIVE_ID = first_id
        return first_id

    _IN_MEMORY_ACTIVE_ID = "telecom_public_demo"
    return "telecom_public_demo"

def set_active_project_id(project_id):
    """Updates active_project.json."""
    global _IN_MEMORY_ACTIVE_ID
    _IN_MEMORY_ACTIVE_ID = project_id
    try:
        os.makedirs(BASE_PROJECTS_DIR, exist_ok=True)
        with open(ACTIVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"active_project_id": project_id}, f, indent=2)
    except Exception:
        pass

def get_project(project_id):
    """Returns a Project instance for the given project_id."""
    return Project(project_id)

def get_active_project():
    """Returns Project instance for the currently active project."""
    active_id = get_active_project_id()
    return Project(active_id)

def create_and_train_project(df_raw, name, business_label, churn_definition, outcome_window,
                             id_col, target_col, pos_val, feature_cols, numeric_cols, categorical_cols,
                             pre_outcome_confirmed=True, provenance_note=None):
    """
    Validates, isolates, and trains a new project.
    Guarantees that a training failure NEVER corrupts or overwrites the active project.
    """
    # 1. Validate mapping and data
    is_valid, errors, cleaned_df = validate_mapping_and_data(
        df_raw, id_col, target_col, pos_val, feature_cols, numeric_cols, categorical_cols
    )
    if not is_valid:
        return False, errors, None

    if not pre_outcome_confirmed:
        return False, ["You must explicitly confirm that all selected features were available before the outcome observation window."], None

    # 2. Generate isolated project ID
    slug = "".join(c.lower() if c.isalnum() else "_" for c in name).strip("_")
    unique_suffix = uuid.uuid4().hex[:6]
    project_id = f"{slug}_{unique_suffix}" if slug else f"project_{unique_suffix}"

    temp_project_dir = os.path.join(BASE_PROJECTS_DIR, project_id)
    os.makedirs(temp_project_dir, exist_ok=True)

    try:
        # 3. Save config
        config = {
            "id": project_id,
            "name": name,
            "business_label": business_label or "General Business",
            "churn_definition": churn_definition or "Customer terminated service or contract",
            "outcome_window": outcome_window or "30 days post-observation",
            "id_column": id_col if id_col != "none" else None,
            "target_column": target_col,
            "positive_target_value": str(pos_val).strip(),
            "feature_columns": [c for c in feature_cols if c in cleaned_df.columns and c != target_col and c != id_col],
            "numeric_features": [c for c in numeric_cols if c in feature_cols],
            "categorical_features": [c for c in categorical_cols if c in feature_cols],
            "pre_outcome_confirmed": True,
            "provenance_note": provenance_note or "User uploaded business dataset snapshot.",
            "is_demo": False
        }

        config_path = os.path.join(temp_project_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # 4. Save immutable copy of dataset
        dataset_path = os.path.join(temp_project_dir, "dataset.csv")
        df_raw.to_csv(dataset_path, index=False)

        # 5. Execute Training Pipeline
        from src.train_experiment import train_and_evaluate_project
        train_and_evaluate_project(
            cleaned_df,
            target_col,
            id_col if id_col != "none" else None,
            config["numeric_features"],
            config["categorical_features"],
            temp_project_dir
        )

        # 6. Execute Customer Segmentation (K-Means)
        from src.segmentation import run_project_segmentation
        run_project_segmentation(
            cleaned_df,
            target_col,
            config["numeric_features"],
            temp_project_dir,
            k=4
        )

        # 7. Training succeeded! Set as active project
        set_active_project_id(project_id)
        return True, [], project_id

    except Exception as e:
        # Clean up temporary failed folder to prevent orphan or corrupted projects
        if os.path.exists(temp_project_dir):
            shutil.rmtree(temp_project_dir, ignore_errors=True)
        return False, [f"Training failed: {str(e)}"], None
