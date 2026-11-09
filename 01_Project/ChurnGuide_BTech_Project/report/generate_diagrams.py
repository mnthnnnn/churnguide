"""
Generate High-Quality Architectural and Workflow Diagrams for Report.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = 'report'
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Figure 1.1: Subscription Churn Lifecycle Diagram
fig, ax = plt.subplots(figsize=(7, 2.8), dpi=250)
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')

# Boxes: Acquisition -> Onboarding -> Service Usage -> Churn Risk -> Retention Action -> Churn / Retention
stages = [
    ("Acquisition\n& Onboarding", 0.6, 2.0, "#dbeafe", "#1e40af"),
    ("Active Service\nUsage", 2.6, 2.0, "#e0f2fe", "#0369a1"),
    ("Risk Detection\n(ChurnGuide)", 4.6, 2.0, "#fef3c7", "#92400e"),
    ("Proactive Action\n& Retention", 6.6, 2.0, "#dcfce7", "#166534"),
    ("Customer\nOutcome", 8.6, 2.0, "#f3f4f6", "#374151")
]

for text, x, y, bg, border in stages:
    box = patches.FancyBboxPatch(
        (x - 0.75, y - 0.65), 1.5, 1.3,
        boxstyle="round,pad=0.1,rounding_size=0.15",
        facecolor=bg, edgecolor=border, linewidth=1.5
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold', color=border)

# Arrows between stages
for i in range(len(stages) - 1):
    x_start = stages[i][1] + 0.8
    x_end = stages[i+1][1] - 0.8
    ax.annotate(
        "", xy=(x_end, 2.0), xytext=(x_start, 2.0),
        arrowprops=dict(arrowstyle="->", color="#6b7280", lw=2, mutation_scale=15)
    )

# Sub-labels for outcome
ax.text(8.6, 1.0, "[Loyal Retained: 73.5%]\n[Lost Churner: 26.5%]", ha='center', va='center', fontsize=7.5, color="#4b5563", style='italic')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig1_churn_lifecycle.png'), bbox_inches='tight')
plt.close(fig)
print("Generated fig1_churn_lifecycle.png")

# 2. Figure 3.1: System Architecture Diagram
fig, ax = plt.subplots(figsize=(7.5, 3.6), dpi=250)
ax.set_xlim(0, 11)
ax.set_ylim(0, 6)
ax.axis('off')

# Layers: Presentation Layer (Flask UI), Application Service Layer, Core ML Engine, Storage & Artifacts
layers = [
    ("Presentation Layer (Flask Web UI)", 5.5, 5.0, 9.5, 1.0, "#ecfdf5", "#059669",
     "3-Step Wizard | Check One Customer | Bulk Scoring | Customer Groups | Model Transparency"),
    ("Application & Explainability Layer", 5.5, 3.4, 9.5, 1.0, "#eff6ff", "#2563eb",
     "Validation Engine | Tree-Path Attribution (Saabas) | Heuristic Retention Rules | K-Means Inference"),
    ("Core Machine Learning & Data Layer", 5.5, 1.8, 9.5, 1.0, "#fef3c7", "#d97706",
     "ColumnTransformer Pipeline | Gradient Boosting Classifier | 80/20 Stratified Train-Test | Joblib Serialization")
]

for title, x, y, w, h, bg, border, sub in layers:
    box = patches.FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.1,rounding_size=0.15",
        facecolor=bg, edgecolor=border, linewidth=1.5
    )
    ax.add_patch(box)
    ax.text(x, y + 0.2, title, ha='center', va='center', fontsize=10, fontweight='bold', color=border)
    ax.text(x, y - 0.2, sub, ha='center', va='center', fontsize=8, color="#374151")

# Connecting arrows
ax.annotate("", xy=(5.5, 3.9), xytext=(5.5, 4.5),
            arrowprops=dict(arrowstyle="<->", color="#6b7280", lw=2, mutation_scale=15))
ax.annotate("", xy=(5.5, 2.3), xytext=(5.5, 2.9),
            arrowprops=dict(arrowstyle="<->", color="#6b7280", lw=2, mutation_scale=15))

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig3_system_architecture.png'), bbox_inches='tight')
plt.close(fig)
print("Generated fig3_system_architecture.png")

# 3. Figure 3.2: Scikit-learn Pipeline Architecture Diagram
fig, ax = plt.subplots(figsize=(7.5, 3.2), dpi=250)
ax.set_xlim(0, 11)
ax.set_ylim(0, 5)
ax.axis('off')

# Raw Input -> ColumnTransformer (Num Pipe / Cat Pipe) -> Concatenation -> Gradient Boosting -> Output
components = [
    ("Raw Customer Record\n(19 Raw Features)", 1.2, 2.5, "#f3f4f6", "#4b5563"),
    ("Numeric Pipeline\nMedian Imputer ->\nStandardScaler (3 cols)", 4.0, 3.6, "#dbeafe", "#1d4ed8"),
    ("Categorical Pipeline\nMode Imputer ->\nOneHotEncoder (16 cols)", 4.0, 1.4, "#fce7f3", "#be185d"),
    ("Feature Union\n(30 Transformed\nFeature Dimensions)", 7.0, 2.5, "#fef3c7", "#b45309"),
    ("Gradient Boosting\nClassifier\n(Decision Ensemble)", 9.6, 2.5, "#d1fae5", "#047857")
]

for title, x, y, bg, border in components:
    box = patches.FancyBboxPatch(
        (x - 1.0, y - 0.7), 2.0, 1.4,
        boxstyle="round,pad=0.1,rounding_size=0.12",
        facecolor=bg, edgecolor=border, linewidth=1.4
    )
    ax.add_patch(box)
    ax.text(x, y, title, ha='center', va='center', fontsize=7.8, fontweight='bold', color=border)

# Arrows
ax.annotate("", xy=(3.0, 3.6), xytext=(2.2, 2.8), arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.8))
ax.annotate("", xy=(3.0, 1.4), xytext=(2.2, 2.2), arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.8))
ax.annotate("", xy=(6.0, 2.8), xytext=(5.0, 3.6), arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.8))
ax.annotate("", xy=(6.0, 2.2), xytext=(5.0, 1.4), arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.8))
ax.annotate("", xy=(8.6, 2.5), xytext=(8.0, 2.5), arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.8))

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig3_pipeline_architecture.png'), bbox_inches='tight')
plt.close(fig)
print("Generated fig3_pipeline_architecture.png")

