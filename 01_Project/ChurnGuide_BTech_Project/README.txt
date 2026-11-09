================================================================================
AI CUSTOMER ANALYTICS & CHURN PREDICTION (CHURNGUIDE)
B.Tech Major Project - Comprehensive User & Examiner Guide
================================================================================

1. PROJECT OVERVIEW & SCOPE
---------------------------
ChurnGuide is a comprehensive machine learning customer analytics platform designed
to operate across diverse business domains (telecommunications, SaaS subscriptions,
financial services, retail, and digital platforms). It models customer attrition
using historical snapshot tabular data, extracts empirical subgroup risk rates,
generates unsupervised customer segments via K-Means clustering, predicts individual
churn risk with genuine marginal perturbation sensitivity, and enables bulk scoring
of unlabelled customer portfolios.

Core Architectural Highlights:
- Multi-Business Dynamic Data Mapping: Upload arbitrary tabular customer datasets.
  The platform dynamically infers column types, checks cardinality, validates strictly
  binary outcomes (regardless of column name or positive label format), enforces
  pre-outcome anti-leakage boundaries, and builds an isolated project environment.
- Strict Anti-Leakage Protocol: Stratified 80/20 train/test split (seed 42). All
  transformers (imputation, scaling, one-hot encoding) are encapsulated inside
  scikit-learn Pipelines and fitted strictly on training folds. The held-out test
  partition is frozen and evaluated only once.
- Algorithm Competition: Evaluates Logistic Regression, Random Forest, and Gradient
  Boosting via Stratified 5-Fold Cross Validation on the training partition. Model
  selection is driven purely by training CV ROC-AUC without accessing test rows.
- Two Pre-Trained Benchmark Projects:
  1. Telecom Public Sample Demo (`telecom_public_demo`): 7,043 consumer accounts from
     the IBM Telco provisional dataset (Gradient Boosting winner, 0.8493 CV ROC-AUC).
  2. B2B SaaS Subscriptions (`saas_b2b_demo`): 1,200 enterprise software accounts
     (SYNTHETIC fixture explicitly created for cross-domain software plumbing verification;
     Logistic Regression winner, 0.7084 CV ROC-AUC).
- Explainability & Sensitivity Attribution: One-at-a-Time Marginal Perturbation
  Sensitivity against training-fold cohort medians/modes (Delta P = P_full - P_perturbed).
  Honest scientific transparency: clearly labeled as empirical model sensitivity associations,
  strictly non-causal. Retention suggestions are labeled as general business review heuristics.
- Portfolio Bulk Scoring: Upload customer CSVs without requiring a target/churn column.
  Includes pre-packaged unlabelled test sets: `data/telco_scoring_unlabeled.csv` and
  `data/saas_scoring_unlabeled.csv`.
- Customer Segmentation: Unsupervised K-Means clustering (k=4) on standardized numeric
  features. Features an honest fallback explanation if numeric features < 2.
- Light-Themed Executive UI: Clean, responsive white/emerald green theme (#0fa37f),
  interactive real-time churn risk simulator with live SVG gauge animations, active project
  switcher dropdown in navigation, 3-step ML studio wizard, downloadable academic thesis PDF,
  and zero external cloud dependencies.

2. SUPPORTED INPUT CONTRACT & DATA BOUNDS
----------------------------------------
Supported Input:
- Format: Tabular CSV file with UTF-8 encoding.
- Input Schema: Exactly one historical customer snapshot record per row.
- Features: All feature columns must represent customer behavior or attributes
  observed strictly BEFORE the churn observation window.
- Target: A single confirmed binary outcome column with exactly 2 distinct classes
  and at least 10 instances per class. The target does not need to be named "Churn"
  or encoded "Yes/No".

Explicitly OUT OF SCOPE (Reported honestly):
- Raw time-series transaction/event logs (e.g. streaming clickstream event logs).
- Automatic future churn label generation.
- Arbitrary non-tabular files (PDF, unstructured text, audio, images).
- Cross-sectional evaluation is an evaluation of snapshot association; operational
  forecasting requires longitudinal temporal forward testing.

3. PREREQUISITES
----------------
- Operating System: Windows 10 or Windows 11 (tested on Windows 11 64-bit).
- Python: Version 3.10 or newer (tested on Python 3.13.7 64-bit).
- Web Browser: Google Chrome, Microsoft Edge, or Mozilla Firefox.
- Offline Capability: Fully local and offline. No paid APIs, cloud services, or accounts.

4. QUICK START INSTRUCTIONS (WINDOWS & MACOS)
----------------------------------------------
Method A: One-Click Windows Launcher (Windows 10 / 11)
1. Double-click "START_HERE.bat" in this directory.
2. Even if Python is not installed, the launcher automatically downloads and configures
   official Python, sets up dependencies, loads models, starts the local server, and opens:
   http://127.0.0.1:5000 in under 2 seconds on returning clicks.

Method B: One-Click macOS Launcher (Apple Silicon & Intel Macs)
1. Double-click "START_HERE.command" in Finder (or run `bash START_HERE.sh` in Terminal).
2. The script automatically detects or provisions Python 3.10+, configures the environment,
   and automatically opens http://127.0.0.1:5000 in your default Mac browser (Safari/Chrome).

Method C: Manual Command-Line Launch (Cross-Platform)
1. Open PowerShell, Terminal, or Command Prompt in this project directory:
   cd "path/to/ChurnGuide_BTech_Project"
2. Create and activate a virtual environment:
   Windows: python -m venv .venv && .venv\Scripts\activate
   macOS:   python3 -m venv .venv && source .venv/bin/activate
3. Install required libraries:
   pip install -r requirements.txt
4. Launch the application:
   python app.py
5. Open your browser and navigate to: http://127.0.0.1:5000

5. TESTING & VERIFICATION SUMMARY
---------------------------------
Automated Test Suite: 18 passed / 18 total (100% passing rate)
- `tests/test_data_loader.py` (10 tests):
  * Verification of raw datasets in data/ (provisional telecom CSV & synthetic SaaS fixture).
  * Automated schema inference and blank detection (11 whitespace blanks in TotalCharges).
  * Target candidate detection, ID detection, and cardinality checking.
  * Validation rules: non-binary targets rejected, missing target values rejected,
    insufficient class count rejected, duplicate customer IDs rejected, direct target/ID
    leakage into features rejected, constant features rejected.
- `tests/test_pipeline_and_leakage.py` (3 tests):
  * Zero-leakage verification: ColumnTransformer fitted exclusively on training fold.
    Extreme test values (999999.0 and missing values) transformed strictly via training
    medians and scaling parameters.
  * Unseen category level handling: OneHotEncoder with handle_unknown='ignore' verified.
  * Pre-trained demo pipelines prediction calibration and probability bounds [0.0, 1.0].
- `tests/test_explain_and_app.py` (5 tests):
  * Project listing, switching, and persistent active project state isolation.
  * Individual customer explanation via One-at-a-Time Marginal Perturbation Sensitivity.
  * Bulk scoring on unlabelled customer CSV without target column.
  * Unsupervised K-Means segmentation and honest fallback when numeric features < 2.
  * Full Flask web navigation, page routing, and downloadable scored CSV export.

6. DATASET CITATION & PROVENANCE
--------------------------------
1. Telecom Public Sample Dataset:
   - Source: Public IBM Telco Customer Churn dataset repository:
     https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv
   - License Notice: The host repository includes an Apache-2.0 license file. This dataset
     is cited and used as a provisional public sample for academic B.Tech evaluation.
   - Rows: 7,043 customers | Columns: 21 | Blank values: 11 in TotalCharges (imputed via training median).
2. B2B SaaS Subscriptions Dataset:
   - File: `data/saas_customer_churn.csv`
   - Notice: Explicitly generated as a SYNTHETIC fixture for software plumbing verification
     and multi-domain demonstration. Never presented as client data.
   - Rows: 1,200 accounts | Columns: 13 | Target: `Status` ("Churned" vs "Active").

7. TROUBLESHOOTING & SUPPORT
----------------------------
- "Port 5000 is already in use":
  Close any existing Python or Flask background processes, or edit `app.py` line 496 to
  specify `port=5001`.
- "OneDrive file lock / permission denied":
  If running inside a OneDrive directory, OneDrive sync may lock `.venv` files. Pause
  OneDrive sync or move the project folder to a standard local folder (e.g. `C:\projects`).
================================================================================
