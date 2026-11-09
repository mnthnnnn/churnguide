"""
ChurnGuide: AI Customer Analytics & Churn Prediction Platform
Supports multi-business tabular customer churn analytics and predictive modeling.
Features dynamic schema mapping, strict leakage prevention, and light-themed UI.
"""

import os
import tempfile
# Ensure clean writable directory for matplotlib cache to avoid startup warnings
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_churnguide"))

import io
import json
import pandas as pd
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_file, session, send_from_directory, jsonify
)

from src.project_manager import (
    list_projects, get_active_project, get_project, get_active_project_id,
    set_active_project_id, create_and_train_project, BASE_PROJECTS_DIR
)
from src.data_loader import inspect_csv_schema

import tempfile
import urllib.parse

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib_churnguide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = "churnguide_secure_local_dev_key_2026"

class VercelPathFix:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get('QUERY_STRING', '')
        if '__route__' in qs:
            params = urllib.parse.parse_qs(qs)
            if '__route__' in params and params['__route__']:
                route = params['__route__'][0]
                cleaned = {k: v for k, v in params.items() if k != '__route__'}
                environ['QUERY_STRING'] = urllib.parse.urlencode(cleaned, doseq=True)
                environ['PATH_INFO'] = route if route.startswith('/') else ('/' + route)
        else:
            path = environ.get('PATH_INFO', '')
            for prefix in ['/api/index.py', '/api/index', '/api']:
                if path.startswith(prefix):
                    new_path = path[len(prefix):]
                    environ['PATH_INFO'] = new_path if new_path.startswith('/') else ('/' + new_path)
                    break

        if not environ.get('PATH_INFO') or environ.get('PATH_INFO') in ['/api/index', '/api/index.py', '/api']:
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFix(app.wsgi_app)

if os.environ.get("VERCEL") or not os.access(BASE_DIR, os.W_OK):
    UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "churnguide_uploads")
    SCORED_DIR = os.path.join(tempfile.gettempdir(), "churnguide_scored")
else:
    UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "data", "uploads"))
    SCORED_DIR = os.path.abspath(os.path.join(BASE_DIR, "data", "scored"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SCORED_DIR, exist_ok=True)

def get_common_context():
    """Returns active project and project list for layout templates."""
    active_proj = get_active_project()
    all_projs = list_projects()
    config = active_proj.get_config() if active_proj else {}
    metadata = active_proj.get_metadata() if active_proj else {}
    return {
        "active_project": active_proj,
        "all_projects": all_projs,
        "active_config": config,
        "active_metadata": metadata,
        "active_id": get_active_project_id()
    }

@app.route("/static/<path:filename>")
def serve_custom_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route("/")
def index():
    ctx = get_common_context()
    return render_template("index.html", **ctx)

@app.route("/projects/switch/<project_id>")
def switch_project(project_id):
    all_p = [p["id"] for p in list_projects()]
    if project_id in all_p:
        set_active_project_id(project_id)
        proj = get_project(project_id)
        cfg = proj.get_config()
        flash(f"Switched active business to '{cfg.get('name', project_id)}' ({cfg.get('business_label', 'Business')}).", "success")
    else:
        flash(f"Project '{project_id}' not found.", "danger")
    
    target_redir = request.args.get("redirect")
    if target_redir:
        try:
            return redirect(url_for(target_redir))
        except Exception:
            pass

    # Return to referer if available, else step3
    ref = request.referrer
    if ref and "/wizard/step2" not in ref:
        return redirect(ref)
    return redirect(url_for("wizard_step3"))

@app.route("/project/plots/<path:filename>")
def project_plot(filename):
    active_proj = get_active_project()
    plots_dir = active_proj.plots_dir
    return send_from_directory(plots_dir, filename)

# --- WIZARD FLOW ---

@app.route("/wizard/step1", methods=["GET", "POST"])
def wizard_step1():
    ctx = get_common_context()
    if request.method == "POST":
        choice = request.form.get("dataset_choice", "upload")
        demo_id = request.form.get("demo_project_id")

        if choice == "demo" and demo_id:
            all_ids = [p["id"] for p in list_projects()]
            if demo_id in all_ids:
                set_active_project_id(demo_id)
                flash(f"Loaded demo project '{demo_id}'.", "success")
                return redirect(url_for("wizard_step3"))

        # Check if user selected to start a new project from a sample template
        sample_template = request.form.get("sample_template")
        if choice == "template" or sample_template:
            template_type = sample_template or "telecom"
            if template_type == "saas":
                source_path = os.path.join("data", "saas_customer_churn.csv")
                default_name = "New SaaS Subscription Project"
                default_biz = "Cloud SaaS Services"
                default_def = "Account cancelled subscription"
            else:
                source_path = os.path.join("data", "Telco-Customer-Churn.csv")
                default_name = "New Telecom Churn Project"
                default_biz = "Telecommunications"
                default_def = "Customer terminated monthly service"

            if os.path.exists(source_path):
                df_raw = pd.read_csv(source_path)
                staged_path = os.path.join(UPLOAD_DIR, "staged_upload.csv")
                df_raw.to_csv(staged_path, index=False)

                session["staged_name"] = request.form.get("project_name", default_name).strip() or default_name
                session["staged_business"] = request.form.get("business_label", default_biz).strip() or default_biz
                session["staged_churn_def"] = request.form.get("churn_definition", default_def).strip() or default_def
                session["staged_window"] = request.form.get("outcome_window", "30 days post-observation").strip() or "30 days"

                return redirect(url_for("wizard_step2"))

        # User uploaded a custom file
        file = request.files.get("csv_file")
        if not file or file.filename == "":
            flash("Please choose a CSV file to upload or select a starting template.", "warning")
            return render_template("wizard_step1.html", **ctx)

        if not file.filename.lower().endswith(".csv"):
            flash("Invalid file format. Please upload a valid tabular .csv file.", "danger")
            return render_template("wizard_step1.html", **ctx)

        try:
            # Read and validate CSV syntax
            df_raw = pd.read_csv(file)
            if len(df_raw) < 50:
                flash(f"The uploaded CSV has only {len(df_raw)} rows. A minimum of 50 customer rows is required for training and cross-validation.", "danger")
                return render_template("wizard_step1.html", **ctx)

            # Save to temporary staging path
            staged_path = os.path.join(UPLOAD_DIR, "staged_upload.csv")
            df_raw.to_csv(staged_path, index=False)

            session["staged_name"] = request.form.get("project_name", "My Customer Churn Project").strip()
            session["staged_business"] = request.form.get("business_label", "General Business").strip()
            session["staged_churn_def"] = request.form.get("churn_definition", "Customer terminated service or contract").strip()
            session["staged_window"] = request.form.get("outcome_window", "30 days post-observation").strip()

            return redirect(url_for("wizard_step2"))

        except Exception as e:
            flash(f"Error parsing uploaded CSV file: {str(e)}", "danger")
            return render_template("wizard_step1.html", **ctx)

    return render_template("wizard_step1.html", **ctx)

@app.route("/wizard/step2", methods=["GET", "POST"])
def wizard_step2():
    ctx = get_common_context()
    staged_path = os.path.join(UPLOAD_DIR, "staged_upload.csv")

    if not os.path.exists(staged_path):
        flash("No uploaded data found. Please begin by adding your dataset in Step 1.", "info")
        return redirect(url_for("wizard_step1"))

    try:
        df_staged = pd.read_csv(staged_path)
    except Exception as e:
        flash(f"Failed to load staged dataset: {str(e)}", "danger")
        return redirect(url_for("wizard_step1"))

    schema_info = inspect_csv_schema(df_staged)

    if request.method == "POST":
        project_name = request.form.get("project_name", session.get("staged_name", "Customer Project")).strip()
        business_label = request.form.get("business_label", session.get("staged_business", "General Business")).strip()
        churn_definition = request.form.get("churn_definition", session.get("staged_churn_def", "Service terminated")).strip()
        outcome_window = request.form.get("outcome_window", session.get("staged_window", "30 days")).strip()
        id_col = request.form.get("id_column", "none")
        target_col = request.form.get("target_column")
        pos_val = request.form.get("positive_target_value")
        pre_outcome_confirmed = request.form.get("pre_outcome_confirmed") == "on"

        # Selected features and their confirmed types (automatically exclude target and ID columns)
        raw_feature_cols = request.form.getlist("selected_features")
        feature_cols = [c for c in raw_feature_cols if c != target_col and c != id_col]
        numeric_cols = []
        categorical_cols = []

        for col in feature_cols:
            col_type = request.form.get(f"type_{col}", "categorical")
            if col_type == "numeric":
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)

        # Train project
        success, errors, new_id = create_and_train_project(
            df_staged,
            name=project_name,
            business_label=business_label,
            churn_definition=churn_definition,
            outcome_window=outcome_window,
            id_col=id_col,
            target_col=target_col,
            pos_val=pos_val,
            feature_cols=feature_cols,
            numeric_cols=numeric_cols,
            categorical_cols=categorical_cols,
            pre_outcome_confirmed=pre_outcome_confirmed
        )

        if not success:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "wizard_step2.html",
                schema_info=schema_info,
                df_preview=df_staged.head(5).to_dict(orient="records"),
                columns=df_staged.columns.tolist(),
                session_meta=session,
                **ctx
            )

        flash(f"Project '{project_name}' trained and evaluated successfully! Winner model deployed.", "success")
        return redirect(url_for("wizard_step3"))

    return render_template(
        "wizard_step2.html",
        schema_info=schema_info,
        df_preview=df_staged.head(5).to_dict(orient="records"),
        columns=df_staged.columns.tolist(),
        session_meta=session,
        **ctx
    )

@app.route("/wizard/step3")
def wizard_step3():
    ctx = get_common_context()
    active_proj = ctx["active_project"]

    if not active_proj or not active_proj.exists():
        flash("No trained project active. Please add a dataset or select a demo to see results.", "info")
        return redirect(url_for("wizard_step1"))

    metadata = active_proj.get_metadata()
    config = active_proj.get_config()
    dataset = active_proj.get_dataset()

    # Generate preview table of top at-risk customers
    at_risk_preview = []
    if dataset is not None:
        try:
            # Score first 100 rows for preview
            sample_df = dataset.head(100).copy()
            id_col = config.get("id_column")
            target_col = config.get("target_column")
            
            scored_sample = active_proj.score_dataframe(sample_df)
            scored_sample = scored_sample.sort_values(by="Predicted_Churn_Probability", ascending=False)
            
            for _, row in scored_sample.head(10).iterrows():
                cid = str(row[id_col]) if id_col and id_col in row else f"Row {row.name}"
                prob = row["Predicted_Churn_Probability"]
                lvl = row["Risk_Level"]
                actual = str(row.get(target_col, "Unknown"))
                at_risk_preview.append({
                    "id": cid,
                    "probability": f"{prob*100:.1f}%",
                    "level": lvl,
                    "badge_class": "badge-danger" if lvl == "High" else ("badge-warning" if lvl == "Medium" else "badge-success"),
                    "actual": actual
                })
        except Exception:
            at_risk_preview = []

    return render_template(
        "wizard_step3.html",
        metadata=metadata,
        config=config,
        at_risk_preview=at_risk_preview,
        **ctx
    )

# --- PREDICT / CHECK ONE CUSTOMER ---

@app.route("/predict", methods=["GET", "POST"])
def predict():
    # Allow switching active business model directly via URL query param
    req_proj = request.args.get("project_id")
    if req_proj:
        all_ids = [p["id"] for p in list_projects()]
        if req_proj in all_ids:
            set_active_project_id(req_proj)
            return redirect(url_for("predict"))

    ctx = get_common_context()
    active_proj = ctx["active_project"]
    if not active_proj or not active_proj.exists():
        flash("Please train or select a business project first.", "info")
        return redirect(url_for("wizard_step1"))

    config = active_proj.get_config()
    metadata = active_proj.get_metadata()

    numeric_features = config.get("numeric_features", [])
    categorical_features = config.get("categorical_features", [])
    baseline_values = metadata.get("baseline_values", {})
    category_levels = metadata.get("category_levels", {})

    form_values = dict(baseline_values)
    prediction_result = None

    if request.method == "POST":
        # Collect customer row
        for col in numeric_features:
            val_str = request.form.get(col, "").strip()
            try:
                form_values[col] = float(val_str)
            except ValueError:
                form_values[col] = baseline_values.get(col, 0.0)

        for col in categorical_features:
            form_values[col] = request.form.get(col, baseline_values.get(col, "")).strip()

        prediction_result = active_proj.explain_customer(form_values)

    # Build quick preset sample rows for instantaneous one-click testing
    dataset = active_proj.get_dataset()
    target_col = config.get("target_column")
    pos_val = config.get("positive_target_value")

    typical_profile = dict(baseline_values)
    at_risk_example = dict(baseline_values)
    loyal_example = dict(baseline_values)

    if dataset is not None and target_col in dataset.columns:
        feature_cols = numeric_features + categorical_features
        churn_mask = dataset[target_col].astype(str).str.strip().str.lower() == str(pos_val).strip().lower()
        churn_rows = dataset[churn_mask]
        retain_rows = dataset[~churn_mask]

        if len(churn_rows) > 0:
            row_dict = churn_rows.iloc[0].to_dict()
            at_risk_example = {c: row_dict[c] for c in feature_cols if c in row_dict}
        if len(retain_rows) > 0:
            row_dict = retain_rows.iloc[0].to_dict()
            loyal_example = {c: row_dict[c] for c in feature_cols if c in row_dict}

    return render_template(
        "predict.html",
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        form_values=form_values,
        category_levels=category_levels,
        prediction_result=prediction_result,
        typical_profile=typical_profile,
        at_risk_example=at_risk_example,
        loyal_example=loyal_example,
        **ctx
    )

@app.route("/predict/train_business", methods=["POST"])
def predict_train_business():
    """
    Directly trains and deploys a new business model from the 'Check one customer' page.
    Automatically identifies target/ID/features, executes 5-fold CV, and activates the business.
    """
    business_name = request.form.get("business_name", "").strip() or "Custom Business Enterprise"
    business_label = request.form.get("business_label", "").strip() or "General Business"
    churn_definition = request.form.get("churn_definition", "").strip() or "Customer cancelled subscription or lapsed"
    outcome_window = request.form.get("outcome_window", "").strip() or "30 days post-observation"

    file = request.files.get("business_csv")
    sample_template = request.form.get("sample_template")

    if file and file.filename != "" and file.filename.lower().endswith(".csv"):
        try:
            df_raw = pd.read_csv(file)
        except Exception as e:
            flash(f"Could not parse uploaded business CSV: {str(e)}", "danger")
            return redirect(url_for("predict"))
    elif sample_template == "saas":
        path = os.path.join("data", "saas_customer_churn.csv")
        df_raw = pd.read_csv(path)
        if not request.form.get("business_name"):
            business_name = "Cloud SaaS Services"
        if not request.form.get("business_label"):
            business_label = "B2B Cloud Software"
    elif sample_template == "telecom":
        path = os.path.join("data", "Telco-Customer-Churn.csv")
        df_raw = pd.read_csv(path)
        if not request.form.get("business_name"):
            business_name = "Telecom Broadband"
        if not request.form.get("business_label"):
            business_label = "Telecommunications"
    else:
        flash("Please upload a customer CSV file or select an industry dataset template.", "warning")
        return redirect(url_for("predict"))

    if len(df_raw) < 50:
        flash(f"Dataset contains only {len(df_raw)} records. A minimum of 50 customer rows is required for stratified CV.", "danger")
        return redirect(url_for("predict"))

    # Inspect schema dynamically
    schema = inspect_csv_schema(df_raw)

    # 1. Target identification (cardinality == 2)
    target_col = None
    for p in schema["column_profiles"]:
        if p.get("is_primary_target"):
            target_col = p["name"]
            break
    if not target_col:
        for p in schema["column_profiles"]:
            if p["cardinality"] == 2:
                target_col = p["name"]
                break

    if not target_col:
        flash("Could not detect a binary outcome column (a column with exactly 2 values representing churn/non-churn). Please verify your CSV.", "danger")
        return redirect(url_for("predict"))

    # 2. Positive churn value identification
    target_prof = next((p for p in schema["column_profiles"] if p["name"] == target_col), None)
    pos_val = None
    if target_prof and target_prof.get("unique_samples"):
        samples = [str(x).strip() for x in target_prof["unique_samples"]]
        for candidate in ["yes", "1", "churn", "churned", "true", "left", "canceled", "cancelled", "lapsed"]:
            matched = next((s for s in samples if s.lower() == candidate), None)
            if matched:
                pos_val = matched
                break
        if not pos_val and len(samples) >= 2:
            pos_val = samples[1]

    # 3. ID column identification
    id_col = "none"
    for p in schema["column_profiles"]:
        if p.get("is_primary_id"):
            id_col = p["name"]
            break

    # 4. Feature columns identification
    feature_cols = []
    numeric_cols = []
    categorical_cols = []

    for p in schema["column_profiles"]:
        col = p["name"]
        if col == target_col or col == id_col:
            continue
        if p["is_constant"] or p["is_all_empty"] or p["is_excessive_cardinality"]:
            continue
        feature_cols.append(col)
        if p["inferred_type"] == "numeric":
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    if len(feature_cols) < 2:
        flash("Not enough usable feature columns found in dataset (minimum 2 required).", "danger")
        return redirect(url_for("predict"))

    # Train and evaluate project
    success, errors, new_id = create_and_train_project(
        df_raw,
        name=business_name,
        business_label=business_label,
        churn_definition=churn_definition,
        outcome_window=outcome_window,
        id_col=id_col,
        target_col=target_col,
        pos_val=pos_val,
        feature_cols=feature_cols,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        pre_outcome_confirmed=True,
        provenance_note=f"Business trained directly from Single Customer Check for {business_name}."
    )

    if not success:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for("predict"))

    active_p = get_active_project()
    meta = active_p.get_metadata() if active_p else {}
    winner = meta.get("winner_model", "Optimal ML Model")
    flash(f"Business '{business_name}' ({business_label}) trained successfully with {winner}! Now evaluating customers for this business below.", "success")
    return redirect(url_for("predict"))

# --- BULK SCORING ---

@app.route("/bulk", methods=["GET", "POST"])
def bulk():
    # Allow switching active business directly from query parameter
    req_proj = request.args.get("project_id")
    if req_proj:
        all_ids = [p["id"] for p in list_projects()]
        if req_proj in all_ids:
            set_active_project_id(req_proj)
            return redirect(url_for("bulk"))

    ctx = get_common_context()
    active_proj = ctx["active_project"]
    if not active_proj or not active_proj.exists():
        flash("Please train or select a business project first.", "info")
        return redirect(url_for("wizard_step1"))

    config = active_proj.get_config()
    scored_preview = []
    total_scored = 0
    scored_file_ready = False

    if request.method == "POST":
        file = request.files.get("bulk_csv")
        use_demo = request.form.get("use_demo_sample") == "1"

        if use_demo:
            # Use pre-packaged unlabeled sample based on active project
            if active_proj.project_id == "telecom_public_demo":
                sample_file = os.path.join("data", "telco_scoring_unlabeled.csv")
            elif active_proj.project_id == "saas_b2b_demo":
                sample_file = os.path.join("data", "saas_scoring_unlabeled.csv")
            else:
                # If custom project, drop target from its own dataset
                dataset = active_proj.get_dataset()
                target_col = config.get("target_column")
                df_sub = dataset.drop(columns=[target_col], errors="ignore").head(200) if dataset is not None and target_col in dataset.columns else None
                sample_file = None

            if sample_file and os.path.exists(sample_file):
                df_to_score = pd.read_csv(sample_file)
            elif df_sub is not None:
                df_to_score = df_sub
            else:
                flash("No pre-packaged scoring sample available for this project.", "warning")
                return redirect(url_for("bulk"))
        else:
            if not file or file.filename == "":
                flash("Please choose a CSV file of customer records to score.", "warning")
                return redirect(url_for("bulk"))
            try:
                df_to_score = pd.read_csv(file)
            except Exception as e:
                flash(f"Failed to parse uploaded CSV: {str(e)}", "danger")
                return redirect(url_for("bulk"))

        try:
            # Score customer portfolio using the active model pipeline
            scored_df = active_proj.score_dataframe(df_to_score)
            out_path = os.path.join(SCORED_DIR, "scored_customers.csv")
            scored_df.to_csv(out_path, index=False)

            total_scored = len(scored_df)
            scored_preview = scored_df.head(15).to_dict(orient="records")
            scored_file_ready = True
            flash(f"Successfully scored {total_scored} customer accounts for {config.get('name')}! Ready for download.", "success")

        except ValueError as err_val:
            # Cross-Business Fallback Check: Did the user upload a CSV matching another project?
            matched_proj = None
            uploaded_cols_lower = [str(c).strip().lower() for c in df_to_score.columns]

            for p_dict in list_projects():
                if p_dict["id"] == active_proj.project_id:
                    continue
                cand_proj = get_project(p_dict["id"])
                cand_cfg = cand_proj.get_config()
                cand_features = cand_cfg.get("feature_columns", [])
                if cand_features:
                    matches = sum(1 for f in cand_features if f.strip().lower() in uploaded_cols_lower)
                    if (matches / len(cand_features)) >= 0.8:
                        matched_proj = cand_proj
                        break

            if matched_proj:
                try:
                    set_active_project_id(matched_proj.project_id)
                    scored_df = matched_proj.score_dataframe(df_to_score)
                    out_path = os.path.join(SCORED_DIR, "scored_customers.csv")
                    scored_df.to_csv(out_path, index=False)

                    total_scored = len(scored_df)
                    scored_preview = scored_df.head(15).to_dict(orient="records")
                    scored_file_ready = True
                    matched_cfg = matched_proj.get_config()
                    flash(
                        f"Detected columns matching '{matched_cfg.get('name')}'. "
                        f"Automatically switched active business and scored {total_scored} accounts successfully!",
                        "success"
                    )
                    # Refresh context for page template
                    ctx = get_common_context()
                    active_proj = ctx["active_project"]
                    config = active_proj.get_config()
                except Exception as inner_e:
                    flash(f"Scoring error: {str(err_val)}", "danger")
            else:
                flash(
                    f"Scoring error: {str(err_val)}. "
                    f"Tip: Click 'Download Template CSV' below to get a sample file formatted for {config.get('name')}.",
                    "danger"
                )

        except Exception as e:
            flash(f"Scoring error: {str(e)}", "danger")

    return render_template(
        "bulk.html",
        config=config,
        scored_preview=scored_preview,
        total_scored=total_scored,
        scored_file_ready=scored_file_ready,
        **ctx
    )

@app.route("/bulk/sample_template")
def download_sample_template():
    """Serves a download-ready sample unlabelled CSV tailored to the active business schema."""
    active_proj = get_active_project()
    if not active_proj or not active_proj.exists():
        flash("No active business project found.", "warning")
        return redirect(url_for("bulk"))

    cfg = active_proj.get_config()
    proj_id = active_proj.project_id

    if proj_id == "saas_b2b_demo":
        sample_path = os.path.join("data", "saas_scoring_unlabeled.csv")
        if os.path.exists(sample_path):
            return send_file(sample_path, as_attachment=True, download_name="b2b_saas_customers_to_score.csv", mimetype="text/csv")
    elif proj_id == "telecom_public_demo":
        sample_path = os.path.join("data", "telco_scoring_unlabeled.csv")
        if os.path.exists(sample_path):
            return send_file(sample_path, as_attachment=True, download_name="telecom_customers_to_score.csv", mimetype="text/csv")

    dataset = active_proj.get_dataset()
    target_col = cfg.get("target_column")
    if dataset is not None:
        sample_df = dataset.drop(columns=[target_col], errors="ignore").head(50)
        buf = io.StringIO()
        sample_df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(
            io.BytesIO(buf.getvalue().encode("utf-8")),
            as_attachment=True,
            download_name=f"{cfg.get('name', 'business').lower().replace(' ', '_')}_sample_to_score.csv",
            mimetype="text/csv"
        )

    flash("No sample scoring data available for this business.", "warning")
    return redirect(url_for("bulk"))

@app.route("/download_scored")
def download_scored():
    out_path = os.path.join(SCORED_DIR, "scored_customers.csv")
    if os.path.exists(out_path):
        return send_file(out_path, as_attachment=True, download_name="scored_customers_with_risk.csv", mimetype="text/csv")
    flash("No scored file available to download. Please score a batch first.", "warning")
    return redirect(url_for("bulk"))

# --- CUSTOMER ANALYTICS ---

@app.route("/analytics")
def analytics():
    ctx = get_common_context()
    active_proj = ctx["active_project"]
    if not active_proj or not active_proj.exists():
        flash("Please train or select a project first.", "info")
        return redirect(url_for("wizard_step1"))

    df = active_proj.get_dataset()
    config = active_proj.get_config()
    target_col = config.get("target_column")
    pos_val = config.get("positive_target_value")
    numeric_features = config.get("numeric_features", [])
    categorical_features = config.get("categorical_features", [])

    if df is None:
        flash("Dataset not available for analytics.", "warning")
        return redirect(url_for("wizard_step3"))

    total_customers = len(df)
    # Binary churn mapping
    binary_y = df[target_col].astype(str).str.strip().eq(str(pos_val).strip()).astype(int)
    churn_count = int(binary_y.sum())
    churn_rate = round(100.0 * churn_count / total_customers, 1) if total_customers > 0 else 0.0

    # Categorical feature analytics: churn rate per group
    cat_analytics = []
    for col in categorical_features:
        if col in df.columns:
            group_stats = []
            for val, sub in df.groupby(col):
                sub_y = binary_y.loc[sub.index]
                size = len(sub)
                c_churn = int(sub_y.sum())
                rate = round(100.0 * c_churn / size, 1) if size > 0 else 0.0
                pct_base = round(100.0 * size / total_customers, 1)
                group_stats.append({
                    "value": str(val),
                    "count": size,
                    "percent_base": pct_base,
                    "churn_count": c_churn,
                    "churn_rate": rate
                })
            # sort by group size desc
            group_stats.sort(key=lambda x: x["count"], reverse=True)
            cat_analytics.append({
                "feature": col,
                "groups": group_stats
            })

    # Numeric feature analytics: distributions and contrast
    num_analytics = []
    for col in numeric_features:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors='coerce').dropna()
            churner_s = s.loc[binary_y == 1].dropna()
            retained_s = s.loc[binary_y == 0].dropna()

            num_analytics.append({
                "feature": col,
                "mean": round(float(s.mean()), 2) if len(s) > 0 else 0.0,
                "median": round(float(s.median()), 2) if len(s) > 0 else 0.0,
                "std": round(float(s.std()), 2) if len(s) > 0 else 0.0,
                "min": round(float(s.min()), 2) if len(s) > 0 else 0.0,
                "max": round(float(s.max()), 2) if len(s) > 0 else 0.0,
                "churner_median": round(float(churner_s.median()), 2) if len(churner_s) > 0 else 0.0,
                "retained_median": round(float(retained_s.median()), 2) if len(retained_s) > 0 else 0.0
            })

    return render_template(
        "analytics.html",
        total_customers=total_customers,
        churn_count=churn_count,
        churn_rate=churn_rate,
        cat_analytics=cat_analytics,
        num_analytics=num_analytics,
        config=config,
        **ctx
    )

# --- CUSTOMER SEGMENTS ---

@app.route("/segments")
def segments():
    ctx = get_common_context()
    active_proj = ctx["active_project"]
    if not active_proj or not active_proj.exists():
        flash("Please train or select a project first.", "info")
        return redirect(url_for("wizard_step1"))

    seg_data = active_proj.get_segmentation()
    config = active_proj.get_config()

    return render_template(
        "segments.html",
        seg_data=seg_data,
        config=config,
        **ctx
    )

# --- MODEL REPORT ---

@app.route("/model")
def model_report():
    ctx = get_common_context()
    active_proj = ctx["active_project"]
    if not active_proj or not active_proj.exists():
        flash("Please train or select a project first.", "info")
        return redirect(url_for("wizard_step1"))

    metadata = active_proj.get_metadata()
    config = active_proj.get_config()

    return render_template(
        "model.html",
        metadata=metadata,
        config=config,
        **ctx
    )

# --- DOWNLOAD ACADEMIC REPORTS & GUIDELINES ---

# --- REAL-TIME MACHINE LEARNING INFERENCE API ---

@app.route("/api/simulate_churn", methods=["POST"])
def api_simulate_churn():
    """
    Executes real-time inference using the active project's trained scikit-learn Pipeline.
    Calculates exact predictive probability, risk level, and marginal perturbation sensitivity.
    """
    data = request.get_json() or {}
    req_proj = data.get("project_id")
    if req_proj:
        active_proj = get_project(req_proj)
    else:
        # Default to telecom demo if telecom features are supplied
        if "Contract" in data or "MonthlyCharges" in data:
            active_proj = get_project("telecom_public_demo")
        else:
            active_proj = get_active_project() or get_project("telecom_public_demo")

    if not active_proj or not active_proj.exists():
        active_proj = get_project("telecom_public_demo")

    if not active_proj or not active_proj.exists():
        return jsonify({"success": False, "error": "No trained model available."}), 404

    try:
        # Run genuine scikit-learn model inference and explainability
        res = active_proj.explain_customer(data)
        return jsonify({
            "success": True,
            "probability": res.get("probability", 0.5),
            "percentage": res.get("percentage", 50.0),
            "risk_level": res.get("risk_level", "Medium"),
            "badge_class": res.get("badge_class", "badge-warning"),
            "top_drivers": res.get("top_drivers", [])[:3],
            "protective_drivers": res.get("protective_drivers", [])[:2],
            "suggested_actions": res.get("suggested_actions", [])[:2]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def find_available_port(preferred_port=5000):
    """Checks if preferred port is free, otherwise finds the next available port."""
    import socket
    for port in range(preferred_port, preferred_port + 10):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return preferred_port

if __name__ == "__main__":
    import threading
    import webbrowser

    port = find_available_port(5000)
    target_url = f"http://127.0.0.1:{port}"

    print(f"\n==================================================================")
    print(f"  ChurnGuide: AI Customer Analytics & Churn Prediction System")
    print(f"  Production Server Online at: {target_url}")
    print(f"==================================================================\n")

    # Open default browser quickly once Flask is starting up
    threading.Timer(0.3, lambda: webbrowser.open(target_url)).start()
    app.run(host="127.0.0.1", port=port, debug=False)
