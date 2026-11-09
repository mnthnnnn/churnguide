"""
Generalized Machine Learning Training, Cross-Validation, and Evaluation Pipeline
Operates on arbitrary tabular schemas with zero test-set data leakage.
Encapsulates all preprocessing inside scikit-learn Pipelines.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)
from sklearn.inspection import permutation_importance

def build_preprocessor(numeric_cols, categorical_cols):
    """Constructs a ColumnTransformer fitted exclusively on training folds."""
    transformers = []

    if numeric_cols:
        num_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        transformers.append(('num', num_transformer, numeric_cols))

    if categorical_cols:
        cat_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
        ])
        transformers.append(('cat', cat_transformer, categorical_cols))

    if not transformers:
        raise ValueError("At least one numeric or categorical feature column must be provided.")

    return ColumnTransformer(transformers=transformers)

def train_and_evaluate_project(cleaned_df, target_col, id_col, numeric_cols, categorical_cols, output_dir):
    """
    Executes full experimental lifecycle:
    1. Stratified 80/20 train/test split.
    2. Stratified 5-Fold CV on training partition across LR, RF, GBM.
    3. Winner selection via training CV ROC-AUC.
    4. Refitting winner on full training partition.
    5. Single honest evaluation on held-out test partition.
    6. Artifact serialization into output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    feature_cols = numeric_cols + categorical_cols
    X = cleaned_df[feature_cols].copy()
    y = cleaned_df[target_col].astype(int).values

    # 1. Stratified 80/20 train/test split (seed 42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 2. Candidate models and hyperparameter grids
    candidates = {
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=1000, random_state=42),
            "params": {"classifier__C": [0.1, 1.0, 10.0]}
        },
        "Random Forest": {
            "model": RandomForestClassifier(random_state=42),
            "params": {
                "classifier__n_estimators": [50, 100],
                "classifier__max_depth": [5, 10]
            }
        },
        "Gradient Boosting": {
            "model": GradientBoostingClassifier(random_state=42),
            "params": {
                "classifier__n_estimators": [50, 100],
                "classifier__learning_rate": [0.05, 0.1],
                "classifier__max_depth": [3, 5]
            }
        }
    }

    cv_results = {}
    best_candidate_name = None
    best_candidate_score = -1.0
    best_pipeline = None
    best_params_str = ""

    print(f"Executing Stratified 5-Fold Cross-Validation on {len(X_train)} training rows...")

    for name, config in candidates.items():
        preprocessor = build_preprocessor(numeric_cols, categorical_cols)
        pipe = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', config['model'])
        ])

        grid = GridSearchCV(
            pipe,
            param_grid=config['params'],
            cv=cv,
            scoring='roc_auc',
            n_jobs=-1,
            refit=True
        )
        grid.fit(X_train, y_train)

        mean_auc = round(float(grid.best_score_), 4)
        best_idx = grid.best_index_
        std_auc = round(float(grid.cv_results_['std_test_score'][best_idx]), 4)
        
        # Clean parameter string
        params_clean = ", ".join(f"{k.replace('classifier__', '')}={v}" for k, v in grid.best_params_.items())

        cv_results[name] = {
            "mean_auc": mean_auc,
            "std_auc": std_auc,
            "params": params_clean
        }
        print(f"  {name}: Mean CV ROC-AUC = {mean_auc:.4f} (+/- {std_auc:.4f}) with [{params_clean}]")

        if mean_auc > best_candidate_score:
            best_candidate_score = mean_auc
            best_candidate_name = name
            best_pipeline = grid.best_estimator_
            best_params_str = params_clean

    print(f"Winner Selected: {best_candidate_name} (Mean CV ROC-AUC: {best_candidate_score:.4f})")

    # 3. Refit winning pipeline on full 80% training partition
    best_pipeline.fit(X_train, y_train)

    # 4. Single honest evaluation on held-out test partition
    y_test_pred = best_pipeline.predict(X_test)
    y_test_proba = best_pipeline.predict_proba(X_test)[:, 1]

    acc = round(float(accuracy_score(y_test, y_test_pred)), 4)
    prec = round(float(precision_score(y_test, y_test_pred, zero_division=0)), 4)
    rec = round(float(recall_score(y_test, y_test_pred, zero_division=0)), 4)
    f1 = round(float(f1_score(y_test, y_test_pred, zero_division=0)), 4)
    roc_auc = round(float(roc_auc_score(y_test, y_test_proba)), 4)

    cm = confusion_matrix(y_test, y_test_pred)
    tn, fp, fn, tp = [int(v) for v in cm.ravel()]

    test_metrics = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": roc_auc
    }

    cm_dict = {
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "total": int(len(y_test))
    }

    # 5. Held-out Permutation Importance
    print("Computing Permutation Feature Importance on held-out test set...")
    perm = permutation_importance(
        best_pipeline, X_test, y_test,
        scoring='roc_auc',
        n_repeats=10,
        random_state=42,
        n_jobs=-1
    )

    perm_importances = []
    for idx in np.argsort(perm.importances_mean)[::-1]:
        col_name = feature_cols[idx]
        mean_dec = float(perm.importances_mean[idx])
        std_dec = float(perm.importances_std[idx])
        perm_importances.append({
            "feature": col_name,
            "mean_decrease": round(mean_dec, 5),
            "std_error": round(std_dec, 5),
            "is_numeric": col_name in numeric_cols
        })

    # 6. Compute training fold typical values for per-customer sensitivity attribution
    baseline_values = {}
    for col in numeric_cols:
        val = float(X_train[col].dropna().median())
        baseline_values[col] = round(val, 2)

    category_levels = {}
    for col in categorical_cols:
        mode_series = X_train[col].dropna().mode()
        baseline_values[col] = str(mode_series.iloc[0]) if len(mode_series) > 0 else ""
        category_levels[col] = [str(v) for v in X_train[col].dropna().unique().tolist()]

    # 7. Generate diagnostic plots
    # (a) Confusion Matrix
    fig, ax = plt.subplots(figsize=(5, 4.2), dpi=200)
    cax = ax.matshow(cm, cmap='Greens', alpha=0.85)
    for i in range(2):
        for j in range(2):
            cell_val = cm[i, j]
            label = f"{cell_val}\n({'TN' if i==0 and j==0 else ('FP' if i==0 and j==1 else ('FN' if i==1 and j==0 else 'TP'))})"
            text_color = 'white' if cell_val > cm.max() * 0.55 else '#1f2937'
            ax.text(j, i, label, ha='center', va='center', fontsize=11, fontweight='bold', color=text_color)
    fig.colorbar(cax, fraction=0.046, pad=0.04)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Retained (0)', 'Churned (1)'], fontsize=10)
    ax.set_yticklabels(['Retained (0)', 'Churned (1)'], fontsize=10)
    ax.set_xlabel('Predicted Label', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel('Ground Truth Label', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_title(f'Test Confusion Matrix ({best_candidate_name})', fontsize=11, fontweight='bold', pad=14)
    plt.tight_layout()
    cm_path = os.path.join(plots_dir, 'confusion_matrix.png')
    plt.savefig(cm_path)
    plt.close()

    # (b) ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_test_proba)
    fig, ax = plt.subplots(figsize=(5.2, 4.2), dpi=200)
    ax.plot(fpr, tpr, color='#0fa37f', lw=2.5, label=f'{best_candidate_name} (AUC = {roc_auc:.4f})')
    ax.plot([0, 1], [0, 1], color='#9ca3af', lw=1.5, linestyle='--', label='No-Skill Chance (AUC = 0.5000)')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=10, fontweight='bold')
    ax.set_ylabel('True Positive Rate (Recall)', fontsize=10, fontweight='bold')
    ax.set_title('Test Receiver Operating Characteristic (ROC)', fontsize=11, fontweight='bold')
    ax.legend(loc='lower right', frameon=True, fontsize=9)
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    roc_path = os.path.join(plots_dir, 'roc_curve.png')
    plt.savefig(roc_path)
    plt.close()

    # (c) Top Features Permutation Importance
    top_k = min(10, len(perm_importances))
    top_features = perm_importances[:top_k][::-1]
    f_names = [f['feature'] for f in top_features]
    f_scores = [f['mean_decrease'] for f in top_features]

    fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=200)
    colors = ['#0fa37f' if f['is_numeric'] else '#3b82f6' for f in top_features]
    ax.barh(f_names, f_scores, color=colors, height=0.6, alpha=0.85)
    ax.set_xlabel('Mean Test ROC-AUC Decrease (Permutation Impact)', fontsize=10, fontweight='bold')
    ax.set_title('Top General Risk Factor Associations (Held-Out Test)', fontsize=11, fontweight='bold')
    ax.grid(axis='x', linestyle=':', alpha=0.6)
    plt.tight_layout()
    fi_path = os.path.join(plots_dir, 'feature_importance.png')
    plt.savefig(fi_path)
    plt.close()

    # 8. Save serialized pipeline and metadata
    pipeline_path = os.path.join(output_dir, "pipeline.joblib")
    joblib.dump(best_pipeline, pipeline_path)

    metadata = {
        "winner_model": best_candidate_name,
        "best_hyperparameters": best_params_str,
        "cv_scores": cv_results,
        "test_metrics": test_metrics,
        "confusion_matrix": cm_dict,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "churn_rate_train": round(float(np.mean(y_train)), 4),
        "churn_rate_test": round(float(np.mean(y_test)), 4),
        "feature_columns": feature_cols,
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
        "permutation_importance": perm_importances,
        "baseline_values": baseline_values,
        "category_levels": category_levels,
        "disclaimer": "Metrics evaluated on a held-out cross-sectional test partition. Associations represent general statistical sensitivity, not verified causal mechanisms. Operational forecasting requires longitudinal temporal evaluation."
    }

    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model artifacts successfully written to: {output_dir}")
    return metadata
