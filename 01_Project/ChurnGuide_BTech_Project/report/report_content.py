"""
Comprehensive academic text, data, and metadata for B.Tech Project Report.
Follows CSE GCET Safapora guidelines strictly.
"""

PROJECT_TITLE = "AI CUSTOMER ANALYTICS & CHURN PREDICTION"
DEGREE_TEXT = "Bachelor of Technology in\nComputer Science & Engineering"
DEPARTMENT_TEXT = "Department of Computer Science and Engineering\nGovt. College Of Engineering & Technology Safapora Ganderbal J&K"
SUBMISSION_MONTH_YEAR = "November 2026"

# Placeholders as strictly instructed
SUPERVISOR_FIELD = "[Supervisor Name]"
SUPERVISOR_DESIG_FIELD = "[Supervisor Designation]"
HOD_FIELD = "[Head of Department]"
HOD_DESIG_FIELD = "Head, Department of Computer Science & Engineering"
GROUP_FIELD = "[Group Number: <Group Number>]"
DATE_FIELD = "[Date: <Date of Submission>]"

CANDIDATES = [
    {"name": "[Student Name 1]", "enrolment": "[Enrolment Number 1]"},
    {"name": "[Student Name 2]", "enrolment": "[Enrolment Number 2]"},
    {"name": "[Student Name 3]", "enrolment": "[Enrolment Number 3]"},
    {"name": "[Student Name 4]", "enrolment": "[Enrolment Number 4]"}
]

ABSTRACT_TEXT = (
    "Customer retention represents a strategic priority in modern telecommunications, "
    "where competitive saturation and low switching barriers inflict severe revenue volatility. "
    "Acquiring new subscribers requires significantly higher capital expenditure than preserving established accounts. "
    "This project presents ChurnGuide, an end-to-end, privacy-preserving machine learning system designed to forecast subscriber churn, "
    "deliver exact row-level predictive attribution, and group subscribers into actionable behavioral cohorts. "
    "Utilizing the public provisional IBM Telco Customer Churn dataset comprising 7,043 subscriber records, "
    "a rigorous experimental protocol was established with an 80/20 stratified train-test split under random seed 42. "
    "All preprocessing procedures, including median imputation of missing charges, standard scaling, and one-hot encoding, "
    "were strictly encapsulated within scikit-learn Pipelines to guarantee zero data leakage between evaluation folds. "
    "Stratified five-fold cross-validation on the training partition compared Logistic Regression, Random Forest, and Gradient Boosting ensembles. "
    "Gradient Boosting achieved the superior mean validation ROC-AUC score of 0.8493, outperforming Logistic Regression (0.8463) and Random Forest (0.8446). "
    "The frozen Gradient Boosting model evaluated once on the held-out test partition yielded an accuracy of 79.84 percent, "
    "precision of 65.85 percent, recall of 50.00 percent, F1-score of 0.5684, and test ROC-AUC of 0.8465. "
    "The evaluation demonstrates that recall on the minority churner class represents the weaker metric due to class imbalance. "
    "Explainability is achieved via exact decision tree path attribution, decomposing raw model predictions into signed feature attributions. "
    "Furthermore, unsupervised four-cluster K-Means segmentation identifies distinct subscriber personas to guide targeted retention interventions. "
    "The software architecture features a lightweight, accessible web application developed with Python and Flask, "
    "accompanied by an automated one-click Windows launcher. "
    "The system operates entirely offline using open-source utilities without reliance on external cloud services."
)

ABBREVIATIONS = [
    ("AUC", "Area Under the Curve"),
    ("CSV", "Comma-Separated Values"),
    ("CV", "Cross-Validation"),
    ("DSL", "Digital Subscriber Line"),
    ("FN", "False Negative"),
    ("FP", "False Positive"),
    ("FPR", "False Positive Rate"),
    ("GB", "Gradient Boosting"),
    ("GCET", "Govt. College Of Engineering & Technology"),
    ("GUI", "Graphical User Interface"),
    ("IDE", "Integrated Development Environment"),
    ("IEEE", "Institute of Electrical and Electronics Engineers"),
    ("KPI", "Key Performance Indicator"),
    ("LR", "Logistic Regression"),
    ("ML", "Machine Learning"),
    ("OHE", "One-Hot Encoding"),
    ("RAM", "Random Access Memory"),
    ("RF", "Random Forest"),
    ("ROC", "Receiver Operating Characteristic"),
    ("SHAP", "Shapley Additive Explanations"),
    ("TN", "True Negative"),
    ("TNR", "Times New Roman"),
    ("TP", "True Positive"),
    ("TPR", "True Positive Rate"),
    ("UI", "User Interface"),
    ("URL", "Uniform Resource Locator"),
    ("VENV", "Virtual Environment"),
    ("WSGI", "Web Server Gateway Interface"),
    ("XAI", "Explainable Artificial Intelligence")
]

NOTATIONS = [
    ("|x|", "Absolute value of scalar quantity x"),
    ("beta_j", "Regression coefficient associated with feature dimension j"),
    ("mu", "Arithmetic mean of feature distribution"),
    ("sigma", "Standard deviation of feature distribution"),
    ("z", "Standardized z-score / log-odds decision function output"),
    ("P(Y=1|X)", "Posterior conditional probability of positive churn outcome"),
    ("L(y, f(x))", "Logarithmic loss / binary cross-entropy objective function"),
    ("Delta_v", "Incremental change in node value along an ensemble decision path"),
    ("k", "Number of clusters in unsupervised partitioning algorithm")
]

REFERENCES_LIST = [
    "Ahmad, A. K., Jafar, A., & Aljoumaa, K. (2019). Customer churn prediction in telecom using machine learning in big data platform. Journal of Big Data, 6(1): 28-51. doi: 10.1186/s40537-019-0191-6.",
    "Amin, A., Al-Obeidat, F., Shah, B., & Adnan, A. (2019). Customer churn prediction in telecommunication industry using data preparation and classification techniques. Neural Computing and Applications, 31(7): 2701–2712. doi: 10.1007/s00521-017-3199-4.",
    "Breiman, L. (2001). Random Forests. Machine Learning, 45(1): 5–32. doi: 10.1023/A:1010933404324.",
    "Burez, J., & Van den Poel, D. (2009). Handling class imbalance in customer churn prediction. Expert Systems with Applications, 36(3): 4626–4636. doi: 10.1016/j.eswa.2008.05.027.",
    "Coussement, K., & Van den Poel, D. (2008). Churn prediction in subscription services: An application of support vector machines while comparing two parameter-selection techniques. Expert Systems with Applications, 34(1): 313–327. doi: 10.1016/j.eswa.2006.09.038.",
    "De Caigny, A., Coussement, K., & De Bock, K. W. (2018). A new hybrid classification algorithm for customer churn prediction based on logistic regression and decision trees. European Journal of Operational Research, 269(2): 760–772. doi: 10.1016/j.ejor.2018.02.009.",
    "Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. The Annals of Statistics, 29(5): 1189–1232. doi: 10.1214/aos/1013203451.",
    "Keramati, A., Jafari-Eskandari, M., & Moztarzadeh, H. (2014). A proposed framework for customer churn prediction in telecom industry: A case study of an Iranian mobile operator. Journal of Information Technology and Computer Science, 6(2): 34–45.",
    "Lalwani, P., Mishra, M. K., Chadhar, J. S., & Sethi, P. (2022). Customer churn prediction system: a machine learning approach. Computing, 104(2): 271–294. doi: 10.1007/s00607-021-00908-y.",
    "Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. In Advances in Neural Information Processing Systems (NeurIPS 2017), 30: 4765–4774.",
    "MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. In Proc. 5th Berkeley Symp. Math. Statist. Prob., 1: 281–297.",
    "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12: 2825–2830.",
    "Saabas, A. (2014). Interpreting random forests with treeinterpreter. Technical Report, GitHub Repository: https://github.com/andosa/treeinterpreter.",
    "Vafeiadis, T., Diamantaras, K. I., Sarigiannidis, G., & Chatzisavvas, K. C. (2015). A comparison of machine learning techniques for customer churn prediction. Simulation Modelling Practice and Theory, 55: 1–9. doi: 10.1016/j.simpat.2015.03.003.",
    "Verbeke, W., Dejaeger, K., Martens, D., Hur, J., & Baesens, B. (2012). New insights into churn prediction in the telecommunication sector: A profit driven data mining approach. European Journal of Operational Research, 218(1): 211–229. doi: 10.1016/j.ejor.2011.09.031.",
    "Verbraken, T., Verbeke, W., & Baesens, B. (2013). A novel profit maximizing metric for measuring classification performance of customer churn prediction models. IEEE Transactions on Knowledge and Data Engineering, 25(5): 961–973. doi: 10.1109/TKDE.2012.50."
]

