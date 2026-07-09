"""
Train Waterborne Disease Prediction models.
Saves: Random Forest, XGBoost, best_model, label_encoder, feature_columns,
accuracy_report.csv, feature_importance.csv/png, final_report.pdf, confusion matrix.
"""

import json
import os
import pickle
import sys
import warnings

warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("XGBoost not installed; training will continue with Random Forest only.")

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    print("SHAP not installed; feature importance plot will use model importances.")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image as RLImage,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    HAS_RL = True
except ImportError:
    HAS_RL = False
    print("ReportLab not installed; skipping PDF generation.")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "dataset", "waterborne_disease_dataset.csv")
MDL = os.path.join(BASE, "models")
RPT = os.path.join(BASE, "reports")
os.makedirs(MDL, exist_ok=True)
os.makedirs(RPT, exist_ok=True)

if not os.path.exists(DATA):
    print("Dataset not found - generating ...")
    sys.path.insert(0, BASE)
    from dataset.generate_dataset import generate_dataset

    df = generate_dataset()
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    df.to_csv(DATA, index=False)
    print(f"Dataset saved: {DATA}")

raw_df = pd.read_csv(DATA)
print(f"Loaded dataset: {raw_df.shape}")

TARGET = "disease_risk"
CAT_COLS = ["water_source", "region_type", "season"]
NUM_COLS = [c for c in raw_df.columns if c not in CAT_COLS + [TARGET]]

num_imp = SimpleImputer(strategy="median")
cat_imp = SimpleImputer(strategy="most_frequent")

work_df = raw_df.copy()
work_df[NUM_COLS] = num_imp.fit_transform(work_df[NUM_COLS])
work_df[CAT_COLS] = cat_imp.fit_transform(work_df[CAT_COLS])
work_df = pd.get_dummies(work_df, columns=CAT_COLS)
FEATURE_COLS = [c for c in work_df.columns if c != TARGET]

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(work_df[TARGET])
X = work_df[FEATURE_COLS].to_numpy(dtype=np.float32)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
)

print(f"Train:{X_train.shape}  Val:{X_val.shape}  Test:{X_test.shape}")

pickle.dump(label_encoder, open(os.path.join(MDL, "label_encoder.pkl"), "wb"))
pickle.dump(FEATURE_COLS, open(os.path.join(MDL, "feature_columns.pkl"), "wb"))
pickle.dump(num_imp, open(os.path.join(MDL, "num_imputer.pkl"), "wb"))
pickle.dump(cat_imp, open(os.path.join(MDL, "cat_imputer.pkl"), "wb"))
print("Preprocessing artifacts saved.")

print("\nTraining Random Forest ...")
random_forest = RandomForestClassifier(
    n_estimators=400,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt",
    n_jobs=-1,
    random_state=42,
)
random_forest.fit(X_train, y_train)
rf_val_acc = accuracy_score(y_val, random_forest.predict(X_val))
rf_test_acc = accuracy_score(y_test, random_forest.predict(X_test))
print(f"Random Forest validation accuracy: {rf_val_acc:.4f}")
print(f"Random Forest test accuracy: {rf_test_acc:.4f}")

xgb_model = None
xgb_val_acc = None
xgb_test_acc = None
if HAS_XGB:
    print("\nTraining XGBoost ...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        objective="multi:softprob",
        eval_metric="mlogloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
    )
    xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    xgb_val_acc = accuracy_score(y_val, xgb_model.predict(X_val))
    xgb_test_acc = accuracy_score(y_test, xgb_model.predict(X_test))
    print(f"XGBoost validation accuracy: {xgb_val_acc:.4f}")
    print(f"XGBoost test accuracy: {xgb_test_acc:.4f}")

model_rows = [
    {"Model": "Random Forest", "Validation Accuracy": round(rf_val_acc, 4), "Test Accuracy": round(rf_test_acc, 4)},
]
if HAS_XGB and xgb_val_acc is not None and xgb_test_acc is not None:
    model_rows.append(
        {"Model": "XGBoost", "Validation Accuracy": round(xgb_val_acc, 4), "Test Accuracy": round(xgb_test_acc, 4)}
    )

acc_df = pd.DataFrame(model_rows)
acc_df.to_csv(os.path.join(RPT, "accuracy_report.csv"), index=False)
print("\nAccuracy Report:")
print(acc_df.to_string(index=False))

best_model_name = "Random Forest"
best_model = random_forest
best_val_acc = rf_val_acc
best_test_acc = rf_test_acc
if HAS_XGB and xgb_model is not None and xgb_val_acc is not None and xgb_val_acc >= best_val_acc:
    best_model_name = "XGBoost"
    best_model = xgb_model
    best_val_acc = xgb_val_acc
    best_test_acc = xgb_test_acc

print(f"\nBest model: {best_model_name} (val={best_val_acc:.4f}, test={best_test_acc:.4f})")

pickle.dump(random_forest, open(os.path.join(MDL, "random_forest_model.pkl"), "wb"))
if xgb_model is not None:
    pickle.dump(xgb_model, open(os.path.join(MDL, "xgboost_model.pkl"), "wb"))
pickle.dump(best_model, open(os.path.join(MDL, "best_model.pkl"), "wb"))
with open(os.path.join(MDL, "best_model_name.txt"), "w", encoding="utf-8") as f:
    f.write(best_model_name)
with open(os.path.join(MDL, "training_metadata.json"), "w", encoding="utf-8") as f:
    json.dump(
        {
            "best_model": best_model_name,
            "validation_accuracy": float(best_val_acc),
            "test_accuracy": float(best_test_acc),
            "classes": label_encoder.classes_.tolist(),
            "feature_count": len(FEATURE_COLS),
        },
        f,
        indent=2,
    )

if best_model_name == "XGBoost" and xgb_model is not None:
    y_pred = xgb_model.predict(X_test)
else:
    y_pred = random_forest.predict(X_test)

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title(f"Confusion Matrix - {best_model_name}")
plt.ylabel("True")
plt.xlabel("Predicted")
plt.tight_layout()
cm_path = os.path.join(RPT, "confusion_matrix.png")
plt.savefig(cm_path, dpi=150)
plt.close()

if hasattr(best_model, "feature_importances_"):
    importance = pd.Series(best_model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
elif HAS_SHAP:
    try:
        explainer = shap.TreeExplainer(best_model)
        shap_vals = explainer.shap_values(X_test[:500])
        if isinstance(shap_vals, list):
            importance = pd.Series(np.abs(shap_vals[2]).mean(axis=0), index=FEATURE_COLS).sort_values(ascending=False)
        else:
            importance = pd.Series(np.abs(shap_vals).mean(axis=0), index=FEATURE_COLS).sort_values(ascending=False)
    except Exception:
        importance = pd.Series(random_forest.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
else:
    importance = pd.Series(random_forest.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)

feature_importance = importance.head(15)
feature_importance_df = feature_importance.reset_index()
feature_importance_df.columns = ["feature", "importance"]
feature_importance_df.to_csv(os.path.join(RPT, "feature_importance.csv"), index=False)
plt.figure(figsize=(10, 7))
feature_importance.sort_values().plot(kind="barh", color="#2196F3")
plt.title(f"Feature Importance - {best_model_name}")
plt.tight_layout()
fi_path = os.path.join(RPT, "feature_importance.png")
plt.savefig(fi_path, dpi=150)
plt.close()
print(f"Feature importance plot saved -> {fi_path}")

shap_path = os.path.join(RPT, "shap_analysis.png")
if HAS_SHAP:
    try:
        explainer = shap.TreeExplainer(best_model)
        shap_vals = explainer.shap_values(X_test[:500])
        values = shap_vals[2] if isinstance(shap_vals, list) else shap_vals
        plt.figure(figsize=(10, 8))
        shap.summary_plot(values, X_test[:500], feature_names=FEATURE_COLS, show=False, plot_type="bar")
        plt.title(f"SHAP Feature Importance - {best_model_name}")
        plt.tight_layout()
        plt.savefig(shap_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"SHAP saved -> {shap_path}")
    except Exception as exc:
        print(f"SHAP failed: {exc}")
        if os.path.exists(fi_path):
            plt.figure(figsize=(10, 7))
            feature_importance.sort_values().plot(kind="barh", color="#2196F3")
            plt.title(f"Feature Importance - {best_model_name}")
            plt.tight_layout()
            plt.savefig(shap_path, dpi=150)
            plt.close()
else:
    if os.path.exists(fi_path):
        plt.figure(figsize=(10, 7))
        feature_importance.sort_values().plot(kind="barh", color="#2196F3")
        plt.title(f"Feature Importance - {best_model_name}")
        plt.tight_layout()
        plt.savefig(shap_path, dpi=150)
        plt.close()

if HAS_RL:
    print("\nGenerating PDF report ...")
    pdf_path = os.path.join(RPT, "final_report.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    h1 = styles["h1"]
    h2 = styles["h2"]
    normal = styles["Normal"]
    story = []

    def heading(text, style=h1):
        story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.1 * inch))

    def body(text):
        story.append(Paragraph(text, normal))
        story.append(Spacer(1, 0.05 * inch))

    heading("Machine Learning Based Early Warning System for Water-Borne Disease Prediction")
    body("Generated automatically by the training pipeline.")
    story.append(Spacer(1, 0.2 * inch))

    heading("1. Dataset Overview", h2)
    body(f"Total Records: {len(raw_df)}")
    body(f"Feature Count: {len(FEATURE_COLS)}")
    dist = raw_df[TARGET].value_counts()
    for cls, cnt in dist.items():
        body(f"{cls}: {cnt} ({cnt / len(raw_df) * 100:.1f}%)")

    heading("2. Model Accuracy", h2)
    tbl_data = [["Model", "Validation Accuracy", "Test Accuracy"]]
    for _, row in acc_df.iterrows():
        tbl_data.append([
            row["Model"],
            f"{row['Validation Accuracy'] * 100:.2f}%",
            f"{row['Test Accuracy'] * 100:.2f}%",
        ])
    tbl = Table(tbl_data, hAlign="LEFT")
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#E3F2FD")]),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 0.2 * inch))

    heading(f"3. Classification Report ({best_model_name})", h2)
    cr = classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
    cr_rows = [["Class", "Precision", "Recall", "F1", "Support"]]
    for cls in label_encoder.classes_:
        row = cr[cls]
        cr_rows.append([
            cls,
            f"{row['precision']:.3f}",
            f"{row['recall']:.3f}",
            f"{row['f1-score']:.3f}",
            str(int(row['support'])),
        ])
    cr_tbl = Table(cr_rows, hAlign="LEFT")
    cr_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#E8F5E9")]),
            ]
        )
    )
    story.append(cr_tbl)
    story.append(Spacer(1, 0.2 * inch))

    heading("4. Confusion Matrix", h2)
    if os.path.exists(cm_path):
        story.append(RLImage(cm_path, width=3.5 * inch, height=3 * inch))
    story.append(PageBreak())

    heading("5. Feature Importance", h2)
    if os.path.exists(fi_path):
        story.append(RLImage(fi_path, width=6 * inch, height=4 * inch))
    story.append(Spacer(1, 0.2 * inch))

    heading("6. Conclusion", h2)
    body(
        f"The {best_model_name} model achieved {best_test_acc * 100:.2f}% test accuracy and is used by the API for predictions."
    )

    doc.build(story)
    print(f"PDF report saved -> {pdf_path}")

print("\nTraining pipeline complete.")
