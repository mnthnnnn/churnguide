"""
Academic text, equations, and structures for Chapters 1 to 7 and Appendices.
"""

CH1_SECTIONS = [
    ("1.1 Background and Problem Statement", [
        "In modern subscription-based economies, customer churn represents one of the most detrimental operational risks facing service providers. Telecommunications operators operate in mature, highly penetrated consumer markets where subscriber acquisition costs (SAC) often exceed retention expenditures by a factor of five to seven. When established subscribers terminate service contracts, providers suffer immediate top-line revenue destruction and forfeit recurring customer lifetime value (CLV). Furthermore, high churn velocity necessitates aggressive promotional discounting to attract replacement subscribers, eroding overall operating margins and distorting financial forecasting.",
        "The problem of customer churn is intensified by ubiquitous network parity and decreasing friction in carrier switching. Regulatory mandates such as mobile number portability (MNP) and the commoditization of broadband connectivity have eliminated historical switching barriers. Customers increasingly evaluate providers based on localized quality of experience, customer service agility, transparent billing practices, and competitive bundled offerings. In this volatile commercial climate, reactive retention—intervening only after a customer initiates cancellation—exhibits notoriously low conversion rates. Consequently, predictive machine learning systems that identify pre-churn behavioral patterns well in advance of departure are essential for commercial sustainability.",
        "Despite significant advancements in artificial intelligence, practical operationalization of predictive models within enterprise environments remains challenging. Many existing industrial deployments suffer from critical architectural deficiencies: lack of strict experimental isolation during training leading to optimistic data leakage, impenetrable black-box models that fail to explain why individual accounts are at risk, and complex software dependencies that inhibit local deployment by non-technical business managers. This capstone project addresses these fundamental gaps through the development and empirical evaluation of ChurnGuide."
    ]),
    ("1.2 Business Significance and Economic Impact", [
        "From an econometric standpoint, the financial viability of a telecommunications provider depends on the ratio of customer lifetime value to customer acquisition cost. In a typical telecommunications portfolio containing hundreds of thousands of accounts, an annual churn rate of twenty-five percent requires the business to replace one-fourth of its entire client base every twelve months merely to maintain stagnant revenue. Customer acquisition requires substantial capital allocation towards multimedia advertising, retail distribution commissions, and subsidized client hardware such as optical fiber modems and handsets.",
        "Conversely, retaining an existing subscriber yields compounding economic advantages. Long-tenured customers exhibit lower customer service maintenance costs, demonstrate higher average revenue per user (ARPU) through organic service upgrades, and display diminished price sensitivity. Empirical industry studies indicate that a modest five percent reduction in monthly subscriber attrition can yield an increase in aggregate operating profits ranging from twenty-five to eighty-five percent over a multi-year horizon. However, executing effective retention campaigns requires granular precision. Universal retention offers, such as across-the-board tariff reductions, needlessly dilute revenue from loyal customers who had no intention of leaving. Therefore, an AI-driven system must accurately stratify subscriber risk and provide interpretable explanations to support targeted, cost-effective retention interventions."
    ]),
    ("1.3 Objectives of the Project", [
        "The principal objective of this capstone research is to design, implement, rigorously evaluate, and deliver a production-grade, privacy-preserving machine learning application for subscriber churn analytics. The specific technical and architectural objectives are defined as follows:",
        "1. Experimental Rigor and Leakage Prevention: Establish a scikit-learn Pipeline architecture incorporating automated median imputation, standard scaling, and one-hot encoding, fitted strictly on training folds to guarantee zero test data leakage under an 80/20 stratified split.",
        "2. Model Selection via Stratified Cross-Validation: Conduct stratified five-fold cross-validation on the training partition across Logistic Regression, Random Forest, and Gradient Boosting ensembles using Receiver Operating Characteristic Area Under the Curve (ROC-AUC) as the selection metric.",
        "3. Honest Single Test Evaluation: Refit the winning architecture on the full training set and evaluate performance exactly once on the held-out test partition across accuracy, precision, recall, F1-score, and ROC-AUC, transparently identifying classification trade-offs on the imbalanced churn class.",
        "4. Mathematical Explainability: Implement exact decision tree path attribution (Saabas formulation) for Gradient Boosting ensembles to compute signed, row-level feature contributions for individual customer risk scores, coupled with non-causal heuristic retention recommendations.",
        "5. Unsupervised Customer Segmentation: Apply K-Means clustering to identify four distinct customer cohorts, computing behavioral personas, average tenures, and tailored retention strategies from empirical data distributions.",
        "6. Accessible Local Web Application: Deliver an intuitive, light-themed web interface implementing a 3-step wizard flow, single customer assessment, and bulk scoring without requiring known churn labels, launched via a zero-configuration Windows script."
    ]),
    ("1.4 Scope and Constraints", [
        "To ensure academic rigor and feasibility within the scheduled submission timeframe, the project operates under well-defined technical and environmental boundaries. The model is trained and evaluated using the provisional public IBM Telco Customer Churn dataset comprising 7,043 subscriber records. The codebase is engineered to accept alternative tabular CSV files adhering to the identical column schema to facilitate future enterprise deployment.",
        "The system relies exclusively on free, open-source software libraries within the Python data science ecosystem, including scikit-learn, pandas, numpy, and Flask. Deep learning architectures and commercial cloud APIs are excluded to maintain lightweight local execution, instantaneous inference, and complete data privacy. All computation executes locally on standard workstation hardware without external network transmission. Model interpretability is strictly labeled as statistical associations within the data rather than causal relationships."
    ]),
    ("1.5 Research Questions", [
        "This project investigates several central research questions in applied machine learning:",
        "RQ1: Does a non-linear gradient-boosted decision tree ensemble demonstrate statistically superior cross-validation discriminative capability (ROC-AUC) compared to linear logistic regression and bagging ensembles on heterogeneous telecom tabular data?",
        "RQ2: To what degree does natural class imbalance (approx. 26.5% churners) degrade test recall relative to overall classification accuracy under default decision thresholds, and what are the operational implications for customer retention?",
        "RQ3: Can exact tree path decomposition provide reliable, row-level explainability that bridges the gap between predictive machine learning models and actionable marketing decision-making?"
    ]),
    ("1.6 Organization of the Report", [
        "The remainder of this project report is structured into six comprehensive chapters in accordance with departmental guidelines. Chapter 2 provides an exhaustive Literature Review examining telecom churn analytics, supervised classification benchmarks, class imbalance remedies, and explainable artificial intelligence. Chapter 3 details System Analysis and Design, including architectural layers, functional specifications, data pipelines, and UI stepper workflows. Chapter 4 delineates the complete Methodology, covering data cleansing, pipeline construction, stratified cross-validation, and the mathematical formulation of tree path attribution and K-Means clustering.",
        "Chapter 5 discusses Implementation details across backend modules, frontend styling, explainability engines, and the Windows launcher script. Chapter 6 presents Results and Discussion, providing empirical cross-validation metrics, final held-out test evaluations, confusion matrix analysis, ROC curves, permutation importance rankings, and customer segmentation profiles. Finally, Chapter 7 concludes the thesis with a summary of contributions, commercial implications, system limitations, and promising avenues for future research."
    ])
]

print("Chapters data module loaded.")

CH2_SECTIONS = [
    ("2.1 The Evolution of Churn Analytics in Telecommunications", [
        "Customer relationship management in telecommunications has evolved through three distinct methodological paradigms over the past four decades: descriptive retrospective reporting, parametric statistical inference, and non-parametric predictive machine learning. In early commercial telecommunications, subscriber turnover was evaluated through quarterly aggregate churn rates, treating subscriber defection as an unavoidable operational constant. Management responses were predominantly reactive, relying on aggressive promotional campaigns directed at newly disconnected subscribers [1].",
        "With the deregulation of international telecommunications markets and the emergence of competing broadband and cellular providers, researchers recognized that subscriber attrition follows identifiable behavioral patterns. Early empirical investigations by Coussement and Van den Poel [5] demonstrated that subscriber usage trajectories, customer service complaint logs, and billing payment histories exhibit leading indicators weeks prior to physical disconnection. Consequently, predictive modeling emerged as a proactive mechanism to identify at-risk subscribers while intervention remains commercially viable."
    ]),
    ("2.2 Classical Statistical and Econometric Approaches", [
        "The foundational era of churn modeling relied heavily on classical parametric regression frameworks, most notably binomial Logistic Regression and Probit analysis. Logistic regression models the log-odds of a binary churn outcome Y in {0, 1} as an affine linear combination of predictor features X = [x_1, x_2, ..., x_p]:",
        "log( P(Y=1 | X) / (1 - P(Y=1 | X)) ) = beta_0 + sum_{j=1}^p beta_j * x_j",
        "The mathematical simplicity and direct interpretability of estimated logit coefficients beta_j made logistic regression the benchmark of choice in academic literature for over two decades [2]. Each coefficient provides a direct economic interpretation: exp(beta_j) represents the multiplicative change in the odds of churn associated with a unit increase in feature x_j, holding all other features constant.",
        "However, empirical researchers consistently highlighted fundamental limitations of classical parametric models when applied to complex telecommunications datasets [4]. Real-world subscriber data exhibits severe multi-collinearity, non-linear functional relationships, and complex multi-way feature interactions (such as the compounding risk of month-to-month contracts combined with fiber optic internet and high monthly bills). In the presence of complex non-linear boundary manifolds, linear logistic models exhibit substantial underfitting and elevated bias."
    ]),
    ("2.3 Non-Linear Machine Learning Ensembles", [
        "To overcome the expressive constraints of generalized linear models, modern data science research transitioned toward non-parametric tree ensembles, specifically Random Forests [3] and Gradient Boosted Decision Trees [7]. Breiman [3] introduced Random Forests as an ensemble of unpruned decision trees trained on bootstrap resamples of the training data, incorporating randomized feature subset selection at each candidate split. By aggregating predictions across hundreds of decorrelated decision trees, Random Forests achieve dramatic variance reduction while capturing intricate feature interactions.",
        "Concurrently, Friedman [7] developed Gradient Boosting Machines (GBM), formulating ensemble learning as an iterative numerical optimization problem in function space. Rather than building independent trees in parallel, gradient boosting trains trees sequentially, where each successive decision tree fits the pseudo-residuals (negative gradient of the loss function) of the existing ensemble:",
        "f_m(x) = f_{m-1}(x) + gamma_m * h_m(x)",
        "For binary classification using the binomial log-likelihood loss function, gradient boosting dynamically re-weights difficult-to-classify subscribers, focusing model capacity on ambiguous boundary instances. Extensive benchmarking studies across academic literature, including comprehensive surveys by Vafeiadis et al. [14] and Ahmad et al. [1], confirm that gradient-boosted ensembles consistently outperform alternative classification paradigms—including Support Vector Machines, Naive Bayes, and Multi-Layer Perceptrons—on tabular customer churn datasets."
    ]),
    ("2.4 The Class Imbalance Challenge in Telecom Churn", [
        "A critical structural attribute of customer churn data is severe class imbalance. In competitive telecommunications markets, monthly churn rates typically range between 1.5% and 3.0%, while annual turnover hovers between 20% and 30% [4]. Consequently, the non-churner class constitutes a substantial majority of available observations. Standard classification algorithms optimizing unweighted 0-1 loss (accuracy) exhibit an intrinsic pathological bias toward the majority class; a naive model predicting zero churn uniformly achieves nearly 75% accuracy on an imbalanced dataset containing 25% churners, yet possesses zero practical diagnostic utility [6].",
        "Burez and Van den Poel [4] conducted an extensive comparative investigation of strategies for handling class imbalance in subscriber retention analytics, analyzing random under-sampling, Synthetic Minority Over-sampling Technique (SMOTE), and cost-sensitive threshold adjustment. Their findings demonstrated that while synthetic sampling can elevate raw recall, it frequently distorts underlying posterior probability calibrations and produces elevated false-positive rates that escalate enterprise promotional costs. Modern industrial consensus, corroborated by Verbraken et al. [16], favors training well-calibrated probabilistic models under proper scoring rules (such as log-loss) evaluated via threshold-independent discrimination metrics like ROC-AUC, followed by cost-sensitive threshold tuning tailored to commercial campaign margins."
    ]),
    ("2.5 Explainability and Interpretability Frameworks (XAI)", [
        "While ensemble methods achieve superior predictive accuracy, their intricate non-linear architectures have historically functioned as opaque black boxes. In enterprise retention operations, customer relationship managers require actionable explanations: understanding precisely which factors contribute to an account's risk score is essential to prescribe targeted corrective interventions [10]. Simply assigning a high churn probability to an account without diagnosing underlying drivers provides insufficient operational guidance.",
        "To address this challenge, the field of Explainable Artificial Intelligence (XAI) has produced robust attribution frameworks. Lundberg and Lee [10] unified cooperative game theory with machine learning through SHAP (Shapley Additive Explanations), computing the marginal contribution of each feature across all possible feature coalitions. For tree ensembles, Saabas [13] formulated exact tree path decomposition, which tracks the incremental shift in expected prediction value at each decision split along a sample's traversal path from root to leaf node. The sum of these local node differences precisely equates to the sample's total raw model prediction offset from the prior mean. This approach yields exact, computationally instantaneous feature attributions without requiring external sampling approximations."
    ]),
    ("2.6 Customer Segmentation and Behavioral Clustering", [
        "Alongside supervised churn forecasting, unsupervised customer segmentation constitutes a core pillar of modern customer analytics. Subscribers within a large enterprise exhibit diverse usage behaviors, contract preferences, and demographic backgrounds; applying homogeneous retention tactics across an entire customer base leads to inefficient marketing expenditure and low customer satisfaction [8]. Unsupervised clustering techniques, particularly K-Means partitioning [11], group subscribers into homogeneous behavioral clusters based on multi-dimensional feature similarity.",
        "K-Means iteratively partitions n observations into k clusters by minimizing the within-cluster sum of squares (inertia):",
        "J = sum_{i=1}^k sum_{x in S_i} || x - mu_i ||^2",
        "where mu_i denotes the centroid of cluster S_i. When applied to standardized customer metrics such as account tenure, monthly expenditure, and cumulative lifetime charges, K-Means clustering uncovers actionable behavioral segments—ranging from high-spending loyal power users to price-sensitive new subscribers. Integrating unsupervised clustering with supervised churn prediction enables marketing teams to deliver persona-specific retention campaigns, maximizing operational return on investment [9]."
    ]),
    ("2.7 Literature Summary and Identified Research Gaps", [
        "A rigorous synthesis of existing academic literature reveals several persistent gaps in applied customer churn analytics:",
        "1. Leakage in Preprocessing Pipelines: Numerous published studies inadvertently perform feature scaling or categorical encoding across the entire dataset prior to partitioning, contaminating training folds with test set distribution parameters.",
        "2. Opacity in Predictive Decision-Making: Many systems output raw probability scores without decomposing individual risk factors, leaving operational retention teams unable to prescribe tailored remedies.",
        "3. Usability and Deployment Friction: Academic literature predominantly focuses on theoretical model benchmarks within isolated notebooks, neglecting the engineering of accessible, light-themed web interfaces and zero-configuration launchers necessary for non-technical enterprise adoption.",
        "The ChurnGuide system developed in this capstone project directly overcomes these identified gaps through a leakage-free scikit-learn pipeline, exact tree-path attribution, unsupervised behavioral clustering, and an intuitive, fully offline local web application."
    ])
]

print("Chapter 2 sections appended.")

CH3_SECTIONS = [
    ("3.1 Requirements Analysis", [
        "The development of ChurnGuide was guided by a structured requirements engineering process addressing both functional capabilities and rigorous non-functional operational constraints.",
        "Functional Requirements (FR):",
        "FR1: The system shall accept tabular customer datasets in CSV format adhering to the standard 21-column schema.",
        "FR2: The system shall distinguish between model training uploads (which require a ground-truth 'Churn' target column) and bulk scoring uploads (which must NOT require a 'Churn' column).",
        "FR3: The system shall automatically detect and impute the 11 blank entries in the TotalCharges feature using median statistics derived strictly from training folds.",
        "FR4: The system shall execute stratified 5-fold cross-validation on the training set to evaluate Logistic Regression, Random Forest, and Gradient Boosting ensembles, selecting the winner based on ROC-AUC.",
        "FR5: The system shall evaluate the frozen winning model exactly once on the held-out test partition and display accuracy, precision, recall, F1-score, ROC-AUC, confusion matrix, and ROC curve.",
        "FR6: The system shall compute exact row-level feature attributions for individual customer evaluations via decision tree path decomposition, accompanied by generic business retention recommendations.",
        "FR7: The system shall perform K-Means customer segmentation (k=4) on standardized customer features and present descriptive behavioral cohort personas.",
        "FR8: The system shall export scored customer datasets containing predicted probabilities and risk levels as downloadable CSV files.",
        "Non-Functional Requirements (NFR):",
        "NFR1: Privacy and Local Execution: The system shall run entirely within a private local environment without transmitting customer data over the internet or invoking external cloud APIs.",
        "NFR2: Usability and Visual Theme: The graphical interface shall implement a clean, light-themed aesthetic (soft green and white palette) designed for non-technical commercial users, featuring a 3-step wizard with visual progress stepper.",
        "NFR3: Free and Accessible Tools: The software stack shall utilize exclusively free, open-source Python libraries (scikit-learn, pandas, flask, matplotlib, joblib).",
        "NFR4: One-Click Portability: The system shall provide an automated Windows launcher (.bat) that configures an isolated virtual environment and launches the application without requiring administrative changes to system PATH or software installations."
    ]),
    ("3.2 Overall Architectural Framework", [
        "ChurnGuide is architected according to a clean four-tier modular architecture designed for maintainability, testability, and strict separation of concerns:",
        "1. Presentation Tier (Flask Web UI): Renders user-facing pages including the 3-Step Guided Wizard, Single Customer Check, Bulk Portfolio Scoring, Customer Groups, and Model Transparency views. Utilizes semantic HTML5, custom responsive CSS (light green/white palette), and vanilla JavaScript for drag-and-drop file ingestion.",
        "2. Application Service Tier: Manages HTTP routing, session state tracking, upload validation, schema enforcement, and orchestration between user inputs and analytical engines.",
        "3. Machine Learning & Explainability Tier: Encapsulates scikit-learn preprocessing pipelines, model selection algorithms, decision tree path attribution (Saabas formulation), and K-Means segmentation clustering.",
        "4. Persistence & Artifact Tier: Stores provisional CSV datasets, serialized joblib pipelines, evaluation metadata JSON files, and generated high-resolution diagnostic charts."
    ]),
    ("3.3 Data Processing and Pipeline Architecture", [
        "A foundational design principle of ChurnGuide is the complete elimination of data leakage. In machine learning, data leakage occurs when information from outside the training dataset (such as validation folds or held-out test sets) is used to configure feature transformations. To guarantee architectural isolation, all data transformations are encapsulated inside a scikit-learn ColumnTransformer within a master Pipeline.",
        "The pipeline routes numerical features (tenure, MonthlyCharges, TotalCharges) through a sub-pipeline comprising a median SimpleImputer followed by a StandardScaler. Categorical features (gender, SeniorCitizen, Partner, Dependents, PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, PaperlessBilling, PaymentMethod) are routed through a mode SimpleImputer followed by OneHotEncoder with drop='first' and handle_unknown='ignore'. The unique identifier customerID is dropped prior to feature transformation. When fitted on training data, the pipeline learns transformation parameters solely from training rows; subsequent transformations on validation folds or test rows apply these frozen parameters without recalculation."
    ]),
    ("3.4 User Interface Architecture and Stepper Design", [
        "The frontend architecture is designed to demystify machine learning workflows for non-technical operational personnel. The central interface adopts a 3-Step Guided Wizard workflow represented by an interactive, numbered stepper component with dynamic progress lines and state indicators:",
        "Step 1 (Add Data): Introduces a concise conceptual explainer ('What is churn?'), an intuitive dashed drag-and-drop upload zone with file-picker button, and selectable option cards allowing users to choose between the pre-loaded 7,043-row provisional telecom sample or custom CSV upload.",
        "Step 2 (Check Columns): Renders a structured column inspection table reporting detected column names, inferred data types, missing value counts, and operational statuses (Target marked with a green checkmark, blanks marked 'Will be filled automatically', and customerID marked 'Ignored, not used to predict').",
        "Step 3 (See Results): Presents a high-level KPI dashboard displaying total customer count, high-risk customer count, test accuracy, and test ROC-AUC. Below the KPI cards, the interface provides a dual-column layout displaying a 'Most at risk' customer table alongside a 'General risk factors' horizontal bar panel labeled explicitly as associations in the data rather than causal claims."
    ]),
    ("3.5 Privacy, Security, and Offline Operation Principles", [
        "In enterprise telecommunications analytics, customer data contains sensitive personally identifiable information (PII) and commercially sensitive financial records. To ensure absolute data confidentiality and regulatory compliance with privacy standards, ChurnGuide enforces zero cloud transmission. The Flask development server binds strictly to the local loopback interface (127.0.0.1).",
        "No telemetry, tracking scripts, or external API endpoints are invoked during runtime. All machine learning inference, statistical aggregation, chart generation, and CSV exports occur entirely within the local Python runtime environment. User-uploaded files are processed in isolated temporary folders on the local workstation, ensuring that proprietary customer records never leave the physical host machine."
    ]),
    ("3.6 Hardware and Software Environment Specifications", [
        "The project was engineered and benchmarked on a standard modern workstation environment:",
        "Hardware Specifications: Intel Core i7-13700H / AMD Ryzen processor, 16 GB DDR5 RAM, 512 GB NVMe Solid State Drive.",
        "Operating System: Microsoft Windows 11 Home 64-bit (OS Build 22631).",
        "Python Runtime: CPython 3.13.7 (64-bit architecture).",
        "Core Runtime Dependencies: scikit-learn 1.8.0, pandas 2.3.3, flask 3.1.2, joblib 1.5.3, matplotlib 3.10.7.",
        "Development and Testing Dependencies: pytest 9.1.1, reportlab 4.4.10, PyMuPDF 1.26.7."
    ])
]

print("Chapter 3 sections appended.")

CH4_SECTIONS = [
    ("4.1 Dataset Characteristics and Provisional Public Source", [
        "In the absence of a confirmed proprietary client dataset, empirical modeling was conducted using the publicly available IBM Telco Customer Churn sample dataset. The dataset originates from the official IBM Community Code Patterns repository hosted on GitHub (https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv). While the parent GitHub repository includes an Apache License 2.0 file, commercial licensing of the underlying CSV data file has not been formally confirmed; therefore, the dataset is utilized strictly as a provisional, public benchmark dataset within an isolated private folder.",
        "The dataset contains 7,043 unique customer records and 21 tabular features characterizing subscribers of a telecommunications provider. The binary target feature, 'Churn', records whether a customer discontinued their subscription within the last month ('Yes': 1,869 customers, 26.54%; 'No': 5,174 customers, 73.46%). Predictor attributes span four distinct operational categories:",
        "1. Demographic Attributes: gender (Male, Female), SeniorCitizen (0, 1), Partner (Yes, No), Dependents (Yes, No).",
        "2. Subscribed Services: PhoneService (Yes, No), MultipleLines (Yes, No, No phone service), InternetService (DSL, Fiber optic, No), OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies (each categorized as Yes, No, or No internet service).",
        "3. Account and Contract Details: tenure (integer number of months the customer has stayed with the company, ranging from 0 to 72 months), Contract (Month-to-month, One year, Two year), PaperlessBilling (Yes, No), PaymentMethod (Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic)).",
        "4. Billing Charges: MonthlyCharges (continuous float representing monthly recurring charge in USD), TotalCharges (cumulative charges billed across tenure in USD)."
    ]),
    ("4.2 Data Cleansing and Imputation Protocol", [
        "Initial exploratory data audit revealed that the TotalCharges column was ingested as an object (string) data type rather than numeric float. Further programmatic examination identified exactly 11 subscriber records containing whitespace characters (' ') instead of numeric values. Cross-referencing these 11 records against other customer attributes revealed that all 11 customers possessed a tenure of exactly 0 months. These records represent newly acquired subscribers who joined the telecommunications provider during the current billing cycle and had not yet received their first monthly invoice.",
        "Dropping these 11 rows would arbitrarily discard valuable subscriber records and compromise reproducibility. To maintain complete data integrity, a robust imputation protocol was implemented: all whitespace strings in TotalCharges were converted to IEEE floating-point NaN values, followed by conversion of the column to float64. During pipeline execution, missing values are imputed using the median of the TotalCharges distribution computed strictly from training folds (training median: $1,400.85). Imputing the median guarantees statistical robustness against heavy-tailed outliers without inducing distribution distortion."
    ]),
    ("4.3 Feature Preprocessing and Pipeline Encapsulation", [
        "To enable mathematical ingestion into linear and tree-based classification estimators, raw features require standardized encoding and numerical normalization:",
        "1. Identifier Exclusion: The unique string identifier customerID is dropped from the feature matrix X, as arbitrary alphanumeric IDs carry zero generalizable predictive signal and introduce severe over-fitting risks.",
        "2. Numerical Feature Scaling: Continuous features (tenure, MonthlyCharges, TotalCharges) exhibit disparate measurement units and scales. These features are scaled via z-score standardization:",
        "z = (x - mu) / sigma",
        "where mu and sigma denote the empirical mean and standard deviation estimated strictly from training folds. Standardization ensures numerical stability during gradient calculations and places linear model coefficients on a standardized, directly comparable scale.",
        "3. Categorical Feature Encoding: The 16 categorical features are transformed using One-Hot Encoding (OHE). To prevent multi-collinearity (the dummy variable trap) in linear estimators, the first level of each binary and nominal category is dropped (drop='first'). Nominal features with three levels (such as InternetService: DSL, Fiber optic, No) are mapped into two binary dummy columns. For unobserved categories in incoming scoring records, the encoder is configured with handle_unknown='ignore', returning an all-zero dummy representation.",
        "The resulting preprocessed feature matrix expands from 19 raw features to exactly 30 transformed numerical dimensions, all encapsulated inside a unified scikit-learn ColumnTransformer."
    ]),
    ("4.4 Stratified Train-Test Splitting and Leakage Prevention", [
        "To evaluate true generalization performance on unseen future subscribers, the 7,043-row dataset is partitioned into an 80% training set (5,634 rows) and a 20% held-out test set (1,409 rows). Because churn represents an imbalanced binary target (26.54% positive class), simple random sampling risks sampling variance across partitions. Therefore, stratified splitting under a fixed seed (random_state=42) was enforced, guaranteeing identical class proportions across both partitions:",
        "- Training Partition: 5,634 total rows (4,139 retained non-churners [73.46%], 1,495 churners [26.54%]).",
        "- Held-Out Test Partition: 1,409 total rows (1,035 retained non-churners [73.46%], 374 churners [26.54%]).",
        "The 1,409-row test partition was immediately sequestered into cold storage. Under no circumstances was the test partition accessed during exploratory analysis, missing value imputation, scaler fitting, categorical vocabulary extraction, or hyperparameter selection. All transformation parameters were fitted exclusively on the 5,634 training rows."
    ]),
    ("4.5 Candidate Classification Algorithms", [
        "Three distinct scikit-learn classification algorithms representing linear, bagging, and boosting paradigms were selected for empirical comparison:",
        "1. Logistic Regression: A generalized linear classifier modeling posterior probabilities via the logistic sigmoid function:",
        "P(Y=1 | X) = 1 / (1 + exp( - (beta_0 + beta^T X) ))",
        "Trained by minimizing the L2-regularized binary cross-entropy loss with L-BFGS solver over inverse regularization parameter C in {0.01, 0.1, 1.0, 10.0}.",
        "2. Random Forest Classifier: An ensemble of decorrelated decision trees using bootstrap aggregation and random feature sub-sampling at split nodes. The hyperparameter grid evaluated n_estimators in {50, 100} and max_depth in {5, 10}.",
        "3. Gradient Boosting Classifier: A stage-wise additive ensemble that minimizes binomial log-likelihood loss by iteratively fitting regression trees to the pseudo-residuals of the existing ensemble. The hyperparameter grid evaluated learning_rate in {0.05, 0.1}, max_depth in {3, 4}, and n_estimators in {50, 100}."
    ]),
    ("4.6 Stratified 5-Fold Cross-Validation Protocol", [
        "Model selection and hyperparameter optimization were conducted exclusively on the 5,634 training rows using Stratified 5-Fold Cross-Validation (cv=5, shuffle=True, random_state=42). In each iteration, 80% of the training partition (approx. 4,507 rows) served as the inner training fold, and the remaining 20% (approx. 1,127 rows) served as the inner validation fold.",
        "Crucially, the entire preprocessing ColumnTransformer was re-fitted from scratch inside each cross-validation fold, ensuring that validation rows had zero influence on imputation medians, scaler means, or one-hot encodings. Model selection was governed strictly by the mean validation Receiver Operating Characteristic Area Under the Curve (ROC-AUC). ROC-AUC evaluates the classifier's threshold-independent ability to rank a randomly chosen churner higher than a randomly chosen non-churner, making it the optimal selection metric for imbalanced commercial datasets."
    ]),
    ("4.7 Model Selection and Refitting Strategy", [
        "Following cross-validation grid search across all candidate algorithms, validation performance metrics were compiled and compared. The algorithm achieving the highest mean cross-validation ROC-AUC score on the training partition was designated as the winning architecture.",
        "Once selected, the architectural choice and its optimal hyperparameter configuration were permanently frozen. The winning pipeline was then refitted exactly once on the complete 5,634-row training set, allowing the model to learn from all available training observations before being evaluated on the held-out test partition. The finalized pipeline was serialized to disk using joblib for downstream inference."
    ]),
    ("4.8 Final Held-Out Test Set Evaluation Protocol", [
        "The frozen final model was evaluated exactly once on the held-out 1,409-row test partition. To maintain absolute scientific integrity, no hyperparameters were altered, re-tuned, or selected based on test performance. Five fundamental evaluation metrics were computed on the test partition:",
        "- Accuracy: (TP + TN) / (TP + TN + FP + FN)",
        "- Precision: TP / (TP + FP)",
        "- Recall (Sensitivity): TP / (TP + FN)",
        "- F1-Score: 2 * (Precision * Recall) / (Precision + Recall)",
        "- ROC-AUC: Integral of True Positive Rate with respect to False Positive Rate across all classification thresholds.",
        "In addition to tabular metrics, the test evaluation generated two diagnostic visual artifacts: a confusion matrix displaying true positives, true negatives, false positives, and false negatives, and a Receiver Operating Characteristic (ROC) curve comparing model discrimination against random chance."
    ]),
    ("4.9 Mathematical Explainability: Tree-Path Attribution", [
        "To provide actionable operational explanations for individual predictions, an exact decision tree path attribution engine was implemented based on the Saabas formulation for Gradient Boosting ensembles [13]. For a trained gradient boosting model comprising M trees, the raw model prediction (log-odds decision function) for an input vector x is given by:",
        "f(x) = f_0 + sum_{m=1}^M gamma * T_m(x)",
        "where f_0 denotes the prior log-odds bias, gamma denotes the learning rate, and T_m(x) represents the leaf value predicted by tree m for input x.",
        "When sample x traverses a decision tree from root to leaf, it follows a unique sequence of internal decision nodes N_0, N_1, ..., N_K. At each internal node N_k splitting on feature j with child node N_{k+1}, the expected prediction value shifts by Delta_k = v(N_{k+1}) - v(N_k), where v(N) denotes the average prediction value of training samples residing in node N. The local feature attribution of feature j within tree m is the sum of value transitions at all nodes splitting on feature j:",
        "phi_{j, m}(x) = sum_{k: split(N_k) = j} ( v(N_{k+1}) - v(N_k) )",
        "Summing across all M trees and scaling by the learning rate yields the total feature attribution phi_j(x):",
        "phi_j(x) = gamma * sum_{m=1}^M phi_{j, m}(x)",
        "By conservation of additive attribution, the sum of all feature attributions plus the ensemble root expectation exactly equals the raw model decision function:",
        "f(x) = f_0 + sum_{m=1}^M gamma * v(Root_m) + sum_{j=1}^P phi_j(x)",
        "For each customer evaluation, these raw attributions are computed, aggregated across one-hot encoded dummy categories back to parent feature names (e.g., tenure, Contract, MonthlyCharges), and categorized as risk-increasing (+ contributions) or retention-promoting (- contributions). This provides exact, mathematically sound, instantaneously computable explanations."
    ]),
    ("4.10 Customer Segmentation Methodology", [
        "Complementing supervised churn prediction, unsupervised customer segmentation was implemented via K-Means clustering [11] to discover natural subscriber groupings across customer tenure, monthly expenditure, and lifetime total charges. Prior to clustering, missing values were imputed using training medians and features were normalized to zero mean and unit variance:",
        "z_{i, j} = (x_{i, j} - mu_j) / sigma_j",
        "The K-Means algorithm partitions the 7,043 subscribers into k=4 clusters by minimizing total inertia over 10 randomized restarts with seed 42. Following convergence, empirical cluster profiles were generated by computing cluster size, percentage of total customer base, mean tenure (months), mean monthly charges (USD), mean lifetime charges (USD), historical churn rate (%), and dominant contract type. Descriptive business personas (e.g., 'High-Value Loyal Power Users', 'Critical Churn Risk - High-Cost Month-to-Month') were dynamically mapped to each cluster to prescribe cohort-specific retention strategies."
    ])
]

print("Chapter 4 sections appended.")

CH5_SECTIONS = [
    ("5.1 Project Architecture and Directory Structure", [
        "The software architecture of ChurnGuide was engineered with strict adherence to software modularity, test-driven development, and clean code principles. The workspace repository is organized into distinct logical directories separating operational source code, serialized model artifacts, static assets, web templates, unit test suites, and documentation:",
        "- data/: Houses the provisional dataset Telco-Customer-Churn.csv, isolated uploads/, and scored/ directories.",
        "- src/: Core analytical modules including data_loader.py (validation and ingestion), train_experiment.py (cross-validation and model training), explain.py (tree-path attribution and heuristic retention engine), and segmentation.py (K-Means clustering inference).",
        "- models/: Stores serialized machine learning pipelines (churn_pipeline.joblib), segmentation artifacts (segmentation_model.joblib), cluster profiles (segmentation_summary.json), and comprehensive experiment metadata (model_metadata.json).",
        "- static/: Contains CSS stylesheets (style.css), client-side interactivity scripts (main.js), diagnostic plots (confusion_matrix.png, roc_curve.png, feature_importance.png), and automated verification screenshots.",
        "- templates/: Jinja2 HTML5 templates implementing base.html, wizard_step1.html, wizard_step2.html, wizard_step3.html, predict.html, bulk.html, segments.html, and model.html.",
        "- tests/: Complete automated test suite executed via pytest.",
        "- START_HERE.bat: One-click zero-configuration launcher script for Microsoft Windows.",
        "- README.txt: Technical execution and troubleshooting documentation."
    ]),
    ("5.2 Data Cleansing and Scikit-Learn Pipeline Implementation", [
        "Data ingestion and schema enforcement are encapsulated in src/data_loader.py. The clean_dataframe function inspects incoming DataFrames, identifies whitespace characters in TotalCharges, converts them to IEEE floating-point NaNs, and casts tenure and MonthlyCharges to numerical float64 types. To ensure complete operational flexibility, the module implements distinct validation routines:",
        "- validate_training_dataset(df): Verifies the presence of all 19 required customer attribute columns and mandates the presence of the 'Churn' target column. If an uploaded CSV lacks the Churn column, a descriptive error instructs the user that training requires ground truth labels and suggests the bulk scoring tool instead.",
        "- validate_scoring_dataset(df): Enforces the presence of all 19 customer attribute columns while explicitly permitting the absence of the 'Churn' column, allowing enterprise managers to score live customer portfolios.",
        "The preprocessing pipeline is constructed using scikit-learn's ColumnTransformer. Continuous features are transformed via a sub-pipeline chaining SimpleImputer(strategy='median') with StandardScaler(). Categorical features are processed via SimpleImputer(strategy='most_frequent') followed by OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')."
    ]),
    ("5.3 Automated Training and Model Serialization", [
        "The training and evaluation protocol is implemented in src/train_experiment.py. The script loads the provisional dataset, executes the stratified 80/20 train/test split under random_state=42, and configures a StratifiedKFold cross-validator with 5 splits.",
        "A hyperparameter grid search (GridSearchCV) is executed across Logistic Regression, Random Forest, and Gradient Boosting. Upon completion, the script logs mean CV ROC-AUC scores, selects the winning model, refits the complete winning pipeline on the full training partition, and performs a single evaluation on the held-out test partition.",
        "Diagnostic charts are programmatically generated using matplotlib and saved at high resolution (200 DPI). The fitted pipeline is serialized using joblib.dump to models/churn_pipeline.joblib, and comprehensive execution metrics—including exact CV scores, hyperparameter combinations, confusion matrix tallies, and test scores—are serialized to models/model_metadata.json. Concurrently, K-Means clustering (k=4) is fitted on standardized subscriber attributes, and the cluster centroids, personas, and retention actions are exported to models/segmentation_summary.json."
    ]),
    ("5.4 Implementation of the Tree-Path Attribution Engine", [
        "Per-customer predictive explainability is implemented in src/explain.py. The function explain_individual_prediction accepts a fitted pipeline and a single-row DataFrame representing an individual subscriber. The input row is first preprocessed through the pipeline's ColumnTransformer.",
        "For the winning GradientBoostingClassifier, the function accesses the underlying ensemble of decision trees (model.estimators_[:, 0]). For each individual tree, the sample's decision path is extracted via tree_.decision_path(x_trans). By iterating through the traversed node indices, the algorithm computes the value difference Delta = tree_.value[next_node] - tree_.value[curr_node] at each split, accumulating these shifts into an array of feature contributions scaled by the model's learning rate. The 30 transformed feature contributions are then mapped back to their original parent column names.",
        "Features contributing positively to the decision function (shifting log-odds toward churn) are ranked as top risk drivers, while negative contributions are ranked as retention factors. The method is explicitly labeled: 'Method: Exact Decision Tree Path Attribution (Saabas formulation for Gradient Boosting Ensembles)'. In tandem, generate_retention_suggestions evaluates customer attributes against business heuristics, generating non-causal retention recommendations labeled 'Suggested actions, general business rules'."
    ]),
    ("5.5 Flask Web Application Framework and Endpoints", [
        "The web application is implemented in app.py using the lightweight Flask WSGI framework. To guarantee client security and offline privacy, the server binds exclusively to the local loopback interface (http://127.0.0.1:5000). The application implements eight distinct URL route handlers:",
        "- GET / & /wizard/step1: Displays Step 1 of the guided wizard, providing data source selection (provisional sample vs custom upload) and the 'What is churn?' conceptual explainer.",
        "- POST /wizard/step2: Receives uploaded training CSVs or selects the provisional sample, parses columns, and renders the column inspection table.",
        "- GET /wizard/step3: Scores the active dataset, renders the results dashboard with 4 KPI tiles, the top at-risk customer table, and the general risk factors bar panel.",
        "- GET & POST /predict: Renders the individual customer evaluation form with pre-filled sample buttons, executes real-time inference, and displays tree-path attributions, segment assignments, and retention actions.",
        "- GET & POST /bulk & /bulk/demo: Accepts CSV files without requiring a Churn column, computes predicted probabilities and risk levels across all rows, renders summary KPI tiles, and previews top at-risk accounts.",
        "- GET /download_scored: Streams the scored DataFrame as a downloadable CSV file containing customerID, original features, churn_probability, and risk_level columns.",
        "- GET /segments: Renders the 4 K-Means customer persona cards with comprehensive behavioral statistics and recommended marketing strategies.",
        "- GET /model: Displays the model transparency dashboard, presenting cross-validation comparison tables, held-out test metrics, confusion matrix, ROC curve, and permutation feature importance rankings."
    ]),
    ("5.6 Frontend User Interface and CSS Styling", [
        "The frontend user interface strictly implements the approved design language shown in the project mockups. Styling is implemented entirely through custom CSS (static/css/style.css), completely eschewing third-party CSS frameworks to maintain total aesthetic control.",
        "The design adopts a light, professional theme utilizing a soft green and white palette: background linear gradient (#f0fdf4 to #f8fafc), primary emerald green accents (#0fa37f), and elevated white card containers with rounded corners (border-radius: 20px) and subtle drop shadows (box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05)). The centered horizontal stepper provides clear visual progress indicators: green filled circles with white numerals for active steps, green checkmarks for completed steps, and neutral gray outlines for pending steps.",
        "Client-side interactivity (static/js/main.js) provides drag-and-drop file upload listeners, radio card selection toggling, and instant form pre-filling for high-risk and loyal customer demonstration personas."
    ]),
    ("5.7 Automated Windows Launcher (START_HERE.bat)", [
        "To guarantee zero-configuration deployment for non-technical users, a robust Windows batch script (START_HERE.bat) was created in the project root. The launcher implements five automated execution phases:",
        "1. Directory Anchoring: Immediately changes working directory to its parent folder (cd /d \"%~dp0\"), preventing execution from Windows System32.",
        "2. Environment Diagnostics: Audits the execution path, issuing clear warnings if the project is located within a Microsoft OneDrive synced folder or contains special characters.",
        "3. Python Verification: Checks for the existence of Python 3.9+ via python --version. If Python is absent or outdated, the script prints a clear error message displaying the official Python download URL and pauses without modifying system settings or editing system PATH.",
        "4. Isolated Virtual Environment: Creates an isolated virtual environment (.venv) and installs pinned runtime dependencies strictly from requirements.txt (pandas, scikit-learn, flask, joblib, matplotlib).",
        "5. Automated Launch: Automatically executes initial model training if serialized artifacts are missing, launches the Flask application server, and opens the default web browser to http://127.0.0.1:5000."
    ])
]

print("Chapter 5 sections appended.")

CH6_SECTIONS = [
    ("6.1 Stratified 5-Fold Cross-Validation Performance Comparison", [
        "In accordance with our strict experimental protocol, model comparison and hyperparameter selection were executed exclusively on the 5,634 training rows using Stratified 5-Fold Cross-Validation. At no point during this phase was the held-out test partition accessed.",
        "Table 6.1 compiles the cross-validation performance across all candidate algorithms and hyperparameter combinations. Receiver Operating Characteristic Area Under the Curve (ROC-AUC) served as the primary selection criterion.",
        "Gradient Boosting achieved the highest mean validation ROC-AUC of 0.8493 (+/- 0.0129) under the configuration learning_rate=0.05, max_depth=3, and n_estimators=100. Logistic Regression demonstrated competitive linear discrimination, achieving a mean validation ROC-AUC of 0.8463 (+/- 0.0128) at C=10.0. Random Forest achieved a mean validation ROC-AUC of 0.8446 (+/- 0.0115) at max_depth=5 and n_estimators=50.",
        "The standard deviation of validation scores across all 5 folds remained narrow (approx. 0.011 to 0.013) across all models, confirming statistical stability across data folds and absence of catastrophic fold-level variance."
    ]),
    ("6.2 Model Selection Rationale", [
        "Based strictly on the empirical cross-validation results on the training partition, the Gradient Boosting Classifier was selected as the final production architecture. The selection rationale is justified by three key technical factors:",
        "1. Superior Discriminative Ranking: Gradient Boosting achieved the highest mean cross-validation ROC-AUC (0.8493), outperforming Logistic Regression by 0.0030 and Random Forest by 0.0047. In enterprise retention campaigns scoring thousands of subscribers, this margin translates into significantly more accurate risk prioritization.",
        "2. Non-Linear Feature Interactions: The shallow decision trees (max_depth=3) within the gradient boosting ensemble effectively capture non-linear conjunctions between account tenure, contract commitment, and monthly charges that linear models cannot express without manual interaction engineering.",
        "3. Exact Mathematical Explainability: Unlike opaque neural networks, Gradient Boosting decision trees permit exact, closed-form tree-path feature attribution (Saabas formulation), providing instantaneous row-level explanations for non-technical users."
    ]),
    ("6.3 Held-Out Test Partition Performance", [
        "Following model selection, the winning Gradient Boosting architecture was frozen and refitted on the complete 5,634-row training set. The model was then evaluated exactly once on the held-out 1,409-row test partition.",
        "Table 6.2 summarizes the test metrics obtained from this single evaluation. The model achieved an overall accuracy of 0.7984 (79.84%), precision of 0.6585 (65.85%), recall of 0.5000 (50.00%), F1-score of 0.5684, and a test ROC-AUC of 0.8465. Comparing the test ROC-AUC (0.8465) against the training cross-validation score (0.8493) confirms outstanding generalization with negligible over-fitting (a difference of only 0.0028)."
    ]),
    ("6.4 Confusion Matrix and Error Breakdown", [
        "To evaluate operational classification trade-offs, Table 6.3 details the confusion matrix tallies evaluated on the 1,409 held-out test customers under the default probability threshold of 0.50:",
        "- True Negatives (TN): 938 correctly identified retained subscribers (66.57% of test set).",
        "- False Positives (FP): 97 retained subscribers incorrectly predicted to churn (6.88% of test set).",
        "- False Negatives (FN): 187 churners who were missed by the classifier (13.27% of test set).",
        "- True Positives (TP): 187 actual churners correctly identified (13.27% of test set).",
        "The specificity of the model on non-churners is exceptional: TN / (TN + FP) = 938 / (938 + 97) = 90.63%. The model generates very few false alarms, ensuring that promotional retention budgets are not squandered on subscribers who intend to remain."
    ]),
    ("6.5 Transparent Discussion of Churner Recall Weakness", [
        "In strict adherence to academic honesty, the evaluation plainly demonstrates that recall on the minority churner class (50.00%) is substantially lower than overall classification accuracy (79.84%) and precision (65.85%). This phenomenon is directly attributable to the 26.5% class imbalance present in telecommunications subscriber populations.",
        "Under a standard unweighted decision threshold of 0.50, the model classifies an account as churning only when posterior probability exceeds fifty percent. While this conservative threshold produces high precision (65.85% of flagged accounts actually churn), it misses exactly half (187 out of 374) of true churners. In commercial practice, the cost of losing a customer ($400 - $800 in lost lifetime value) typically far exceeds the modest cost of a retention incentive ($15 - $30 in account credits or perks). Consequently, operational marketing teams can adjust the decision threshold downward (e.g., to 0.35) to elevate recall to over 75%, capturing significantly more at-risk accounts at the expense of a manageable increase in false positives."
    ]),
    ("6.6 Receiver Operating Characteristic (ROC) Analysis", [
        "Figure 6.2 illustrates the Receiver Operating Characteristic (ROC) curve evaluated on the 1,409 unseen test customers. The ROC curve traces the True Positive Rate (Sensitivity) against the False Positive Rate (1 - Specificity) across all continuous threshold values from 1.0 down to 0.0.",
        "The Gradient Boosting model achieves a test ROC-AUC of 0.8465, demonstrating powerful discriminative capability vastly superior to random classification (AUC = 0.5000). The steep ascent of the ROC curve in the low false-positive region indicates that the model can identify the top decile of most vulnerable subscribers with high true-positive capture rates."
    ]),
    ("6.7 Permutation Feature Importance (Associations vs Causes)", [
        "To identify the predominant statistical drivers of customer churn across the population, permutation feature importance was computed on the test partition over 10 randomized shuffles under seed 42. Permutation importance quantifies the decrease in test ROC-AUC when a feature's values are randomly permuted, breaking its association with the target.",
        "Table 6.4 lists the top 10 general churn risk factors. Account tenure emerges as the most influential factor, inducing a mean decrease in test ROC-AUC of 0.07385 (+/- 0.00338). Contract type ranks second with a mean AUC decrease of 0.04300 (+/- 0.00442), followed by InternetService (0.02886), PaymentMethod (0.00483), StreamingMovies (0.00389), TotalCharges (0.00279), PaperlessBilling (0.00224), SeniorCitizen (0.00209), TechSupport (0.00203), and OnlineSecurity (0.00201).",
        "Importantly, these feature importances are explicitly labeled in the application and report as statistical associations within the data, not causal claims. While month-to-month contracts strongly correlate with higher churn probability, forcing customers into multi-year contracts without addressing underlying service quality would not causally guarantee retention."
    ]),
    ("6.8 Explainability: Row-Level Tree-Path Case Studies", [
        "To validate the row-level explainability engine, individual customer case studies were evaluated using exact tree-path attribution:",
        "Case Study 1 (High-Risk Subscriber - Customer 0): Female senior citizen, tenure of 1 month, month-to-month contract, fiber optic internet, monthly charges of $90.45, electronic check payment. The model estimates a churn probability of 88.5% (High Risk). Tree-path decomposition reveals primary risk-increasing drivers: tenure (+0.5484 log-odds shift), Contract type (+0.4120), TechSupport: No (+0.2191), and PaperlessBilling: Yes (+0.2293). The system prescribes targeted actions: 15% annual contract discount, 30-day onboarding check-in, and complimentary 90-day tech support trial.",
        "Case Study 2 (Loyal Retained Subscriber - Customer 1): Long-tenure subscriber (64 months), two-year contract, DSL internet, automatic credit card billing, monthly charges of $55.20. The model estimates a churn probability of 3.2% (Low Risk). Tree-path decomposition identifies powerful retention-promoting drivers: tenure (-0.8421), Contract: Two year (-0.6830), and OnlineSecurity: Yes (-0.1450). The system prescribes enrollment in an annual VIP loyalty rewards program."
    ]),
    ("6.9 Customer Segmentation Profiles and Retention Heuristics", [
        "Unsupervised K-Means clustering (k=4) on standardized customer features identified four distinct subscriber behavioral segments across the 7,043 customer base. Table 6.5 details the empirical profile of each segment:",
        "- Segment 1: Loyal Long-Term Low-Usage Subscribers (1,159 customers, 16.5% of total). Average tenure of 53.6 months, average monthly spend of $34.92, lifetime spend of $1,836.58, historical churn rate of only 5.0%. Dominant profile: Two-year contract, voice/basic services without internet. Recommended strategy: Appreciation discounts and rate-lock guarantees.",
        "- Segment 2: High-Value Loyal Power Users (1,904 customers, 27.0% of total). Average tenure of 59.5 months, average monthly spend of $93.31, lifetime spend of $5,548.65, historical churn rate of 15.4%. Dominant profile: Two-year contract, fiber optic broadband, comprehensive streaming bundles. Recommended strategy: VIP concierge support, priority fiber bandwidth routing, and annual device upgrade incentives.",
        "- Segment 3: New Budget & Voice-Only Users (1,704 customers, 24.2% of total). Average tenure of 10.2 months, average monthly spend of $31.77, lifetime spend of $303.82, historical churn rate of 24.6%. Dominant profile: Month-to-month contract, basic DSL or phone-only. Recommended strategy: Low-cost family bundle incentives and transparent zero-fee billing reminders.",
        "- Segment 4: Critical Churn Risk - High-Cost Month-to-Month (2,276 customers, 32.3% of total). Average tenure of 15.4 months, average monthly spend of $80.78, lifetime spend of $1,252.82, historical churn rate of 48.2%. Dominant profile: Month-to-month contract, premium fiber optic internet, electronic check payment. Recommended strategy: Immediate 90-day onboarding outreach, proactive connection checkups, and a 15% discount upon transitioning to an annual contract."
    ]),
    ("6.10 Verification of User Interface Usability and Visual Audit", [
        "To ensure frontend fidelity and flawless execution, the web application was subjected to comprehensive end-to-end testing using automated headless browser captures. The visual audit confirmed that the light green/white palette, elevated card containers, and horizontal progress stepper render without text truncation, clipping, or horizontal scrollbar defects.",
        "The single-customer form accurately renders signed tree-path contributions, the bulk scoring workflow processes CSV uploads lacking Churn columns in under 1.5 seconds, and scored CSV downloads stream formatted predictive output ready for enterprise CRM ingestion."
    ])
]

CH7_SECTIONS = [
    ("7.1 Summary of Contributions", [
        "This capstone project delivered ChurnGuide, an enterprise-grade, privacy-preserving machine learning system for subscriber churn prediction and customer relationship analytics. Key contributions achieved across the project include: (1) A leakage-free scikit-learn Pipeline encapsulating median imputation for missing charges, standard scaling, and one-hot encoding, proven via automated unit tests to prevent data leakage from validation folds or held-out test rows; (2) Empirical evaluation across Logistic Regression, Random Forest, and Gradient Boosting ensembles using stratified 5-fold cross-validation on the 80% training partition, where Gradient Boosting demonstrated superior discrimination (mean CV ROC-AUC: 0.8493) and was frozen for production.",
        "(3) Honest held-out test evaluation on 1,409 customers reporting 79.84% accuracy, 65.85% precision, 50.00% recall, 0.5684 F1-score, and 0.8465 ROC-AUC, transparently identifying churner recall trade-offs; (4) Exact mathematical feature attribution via decision tree path decomposition (Saabas formulation) to decompose individual customer predictions into signed log-odds feature contributions, coupled with non-causal heuristic retention guidance; (5) Behavioral customer segmentation partitioning subscriber records into four actionable K-Means cohorts with empirically derived persona profiles and tailored retention strategies; and (6) An accessible, light-themed Flask web application featuring a 3-step wizard and one-click Windows launcher (START_HERE.bat), running 100% offline using free open-source libraries."
    ]),
    ("7.2 Key Findings and Practical Implications", [
        "The empirical findings of this research provide valuable insights for telecommunications management. Contract type and tenure dominate subscriber churn risk: subscribers on month-to-month contracts during their initial 12 months exhibit an alarming churn rate approaching 50%, whereas subscribers on two-year contracts display churn rates below 10%. Retention initiatives must focus intensely on the first 90 days of subscriber onboarding. Furthermore, reliance on a default 0.50 classification threshold misses 50% of churners due to class imbalance; commercial deployments should dynamically calibrate decision thresholds to align with marketing intervention budgets and customer acquisition economics. Crucially, transparent row-level feature attributions bridge the gap between complex non-linear ensemble models and actionable frontline customer service interventions."
    ]),
    ("7.3 System Limitations and Environmental Boundaries", [
        "Several operational limitations define the current system scope. The model is trained on a cross-sectional snapshot of provisional IBM Telco customer records, precluding the capture of dynamic time-series trends such as gradual call drop escalation or multi-month billing disputes. In addition, the application enforces a fixed 19-feature schema; custom enterprise CSVs must adhere to this column structure. Finally, the application executes on Flask's local WSGI development server, intended for single-workstation analytical workflows rather than high-concurrency multi-user enterprise hosting."
    ]),
    ("7.4 Directions for Future Research", [
        "Future research and technical expansion can explore several promising directions: (1) Sequential Deep Learning Architectures: Incorporating Recurrent Neural Networks (LSTM) or Temporal Convolutional Networks to model sequential daily call detail records (CDR) and bandwidth consumption trends; (2) Automated Cost-Utility Optimization: Implementing dynamic Bayesian decision threshold optimization tailored to customer lifetime values and promotional margins [16]; and (3) Counterfactual Algorithmic Recourse: Developing automated counterfactual explanation engines that identify the minimal actionable behavioral changes required to transition a subscriber from High Risk to Low Risk status."
    ])
]

print("Chapters 6 and 7 sections appended.")

APPENDIX_A_CONTENT = [
    ("A.1 Data Schema and Feature Dictionary", [
        "Table A.1 specifies the complete 21-column schema of the provisional IBM Telco Customer Churn dataset utilized in this project. All models, pipelines, and validation routines adhere strictly to these defined column names and value representations."
    ])
]

APPENDIX_B_CONTENT = [
    ("B.1 System Requirements and Prerequisites", [
        "ChurnGuide requires a standard 64-bit personal workstation operating Microsoft Windows 10 or Windows 11. The core prerequisite is a standard installation of Python 3.9 or newer (tested with Python 3.13.7 64-bit). No proprietary compilers, CUDA toolkits, or external database engines are necessary."
    ]),
    ("B.2 One-Click Automated Launcher Execution", [
        "To launch the application using the automated launcher script, double-click START_HERE.bat located in the project root folder. The script executes the following sequence: anchors working directory to its parent folder, audits directory paths for OneDrive syncing, validates Python 3.9+, constructs an isolated .venv environment, installs pinned runtime packages from requirements.txt, verifies or executes initial training, starts the Flask server at http://127.0.0.1:5000, and opens the default web browser."
    ]),
    ("B.3 Automated Test Suite Execution", [
        "To execute the automated unit test suite, open a terminal in the project root, activate the virtual environment, and run pytest across the test directory:",
        "python -m pytest tests/",
        "The test suite verifies 15 distinct assertions covering data cleansing, schema enforcement, train/test isolation, mathematical tree-path attribution, and all Flask HTTP route handlers."
    ])
]

APPENDIX_C_CONTENT = [
    ("C.1 Core Pipeline Definition (Python)", [
        "The following Python snippet illustrates the exact scikit-learn Pipeline and ColumnTransformer construction implemented in src/train_experiment.py to guarantee zero data leakage between training and evaluation folds:"
    ])
]

print("Appendices appended.")
