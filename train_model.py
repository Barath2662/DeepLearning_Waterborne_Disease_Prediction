"""
Train Waterborne Disease Prediction models.
Saves: DNN, scaler, label_encoder, feature_columns, accuracy_report.csv,
       shap_analysis.png, final_report.pdf, confusion matrix.
"""

import os, sys, warnings, pickle, io
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score)
from sklearn.impute import SimpleImputer

# ── optional deps ──────────────────────────────────────────────────────────
try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("XGBoost not installed; skipping XGBoost model.")

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    print("SHAP not installed; skipping SHAP analysis.")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, Image as RLImage,
                                    PageBreak)
    HAS_RL = True
except ImportError:
    HAS_RL = False
    print("ReportLab not installed; skipping PDF generation.")

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, callbacks

# ── paths ──────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
DATA   = os.path.join(BASE, "dataset", "waterborne_disease_dataset.csv")
MDL    = os.path.join(BASE, "models")
RPT    = os.path.join(BASE, "reports")
NB     = os.path.join(BASE, "notebooks")
os.makedirs(MDL, exist_ok=True)
os.makedirs(RPT, exist_ok=True)
os.makedirs(NB,  exist_ok=True)

# ── 1. generate dataset if missing ────────────────────────────────────────
if not os.path.exists(DATA):
    print("Dataset not found – generating …")
    sys.path.insert(0, os.path.join(BASE, "dataset"))
    from generate_dataset import generate_dataset
    df = generate_dataset()
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    df.to_csv(DATA, index=False)
    print(f"Dataset saved: {DATA}")

df = pd.read_csv(DATA)
print(f"Loaded dataset: {df.shape}")

# ── 2. preprocessing ───────────────────────────────────────────────────────
CAT_COLS = ["water_source", "region_type", "season"]
NUM_COLS = [c for c in df.columns if c not in CAT_COLS + ["disease_risk"]]

# Missing values
num_imp = SimpleImputer(strategy="median")
df[NUM_COLS] = num_imp.fit_transform(df[NUM_COLS])

cat_imp = SimpleImputer(strategy="most_frequent")
df[CAT_COLS] = cat_imp.fit_transform(df[CAT_COLS])

# One-hot encode categoricals
df = pd.get_dummies(df, columns=CAT_COLS)
FEATURE_COLS = [c for c in df.columns if c != "disease_risk"]

# Label encode target
le = LabelEncoder()
y  = le.fit_transform(df["disease_risk"])       # Low=0, Medium=1, High=2
X  = df[FEATURE_COLS].values

# Outlier clipping (IQR)
for i in range(len(NUM_COLS)):
    col = df.columns.get_loc(NUM_COLS[i]) if NUM_COLS[i] in df.columns else None
    if col is not None:
        q1, q3 = np.percentile(X[:, i], [1, 99])
        X[:, i] = np.clip(X[:, i], q1, q3)

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train / val / test split
X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y, test_size=0.15,
                                            random_state=42, stratify=y)
X_tr, X_val, y_tr, y_val = train_test_split(X_tr, y_tr, test_size=0.15,
                                              random_state=42, stratify=y_tr)

print(f"Train:{X_tr.shape}  Val:{X_val.shape}  Test:{X_te.shape}")

# ── 3. save preprocessing artifacts ───────────────────────────────────────
pickle.dump(scaler,       open(os.path.join(MDL, "scaler.pkl"),          "wb"))
pickle.dump(le,           open(os.path.join(MDL, "label_encoder.pkl"),   "wb"))
pickle.dump(FEATURE_COLS, open(os.path.join(MDL, "feature_columns.pkl"), "wb"))
print("Preprocessing artifacts saved.")

# ── 4. DNN ─────────────────────────────────────────────────────────────────
def build_model(input_dim, num_classes, lr=1e-3):
    inp = keras.Input(shape=(input_dim,))
    x   = layers.Dense(256, activation="relu")(inp)
    x   = layers.BatchNormalization()(x)
    x   = layers.Dropout(0.3)(x)
    x   = layers.Dense(128, activation="relu")(x)
    x   = layers.BatchNormalization()(x)
    x   = layers.Dropout(0.3)(x)
    x   = layers.Dense(64,  activation="relu")(x)
    x   = layers.BatchNormalization()(x)
    x   = layers.Dropout(0.2)(x)
    x   = layers.Dense(32,  activation="relu")(x)
    out = layers.Dense(num_classes, activation="softmax")(x)
    mdl = keras.Model(inp, out)
    mdl.compile(optimizer=keras.optimizers.Adam(lr),
                loss="sparse_categorical_crossentropy",
                metrics=["accuracy"])
    return mdl

NUM_CLASSES = len(le.classes_)
model = build_model(X_tr.shape[1], NUM_CLASSES)
model.summary()

cb = [
    callbacks.EarlyStopping(patience=10, restore_best_weights=True,
                            monitor="val_accuracy"),
    callbacks.ModelCheckpoint(os.path.join(MDL, "waterborne_model.h5"),
                              save_best_only=True, monitor="val_accuracy"),
    callbacks.ReduceLROnPlateau(patience=5, factor=0.5, min_lr=1e-6,
                                monitor="val_loss"),
]

history = model.fit(X_tr, y_tr,
                    validation_data=(X_val, y_val),
                    epochs=150, batch_size=64,
                    callbacks=cb, verbose=1)

dnn_acc = model.evaluate(X_te, y_te, verbose=0)[1]
print(f"\nDNN Test Accuracy: {dnn_acc:.4f}")

# ── 5. Random Forest ────────────────────────────────────────────────────────
print("\nTraining Random Forest …")
rf = RandomForestClassifier(n_estimators=200, max_depth=None,
                             n_jobs=-1, random_state=42)
rf.fit(X_tr, y_tr)
rf_acc = accuracy_score(y_te, rf.predict(X_te))
print(f"RF Test Accuracy: {rf_acc:.4f}")

# ── 6. XGBoost ──────────────────────────────────────────────────────────────
xgb_acc = 0.0
xgb_model = None
if HAS_XGB:
    print("\nTraining XGBoost …")
    xgb_model = xgb.XGBClassifier(n_estimators=200, max_depth=6,
                                    learning_rate=0.1, use_label_encoder=False,
                                    eval_metric="mlogloss", random_state=42,
                                    n_jobs=-1)
    xgb_model.fit(X_tr, y_tr,
                  eval_set=[(X_val, y_val)], verbose=False)
    xgb_acc = accuracy_score(y_te, xgb_model.predict(X_te))
    print(f"XGB Test Accuracy: {xgb_acc:.4f}")

# ── 7. accuracy report CSV ─────────────────────────────────────────────────
acc_df = pd.DataFrame({
    "Model":    ["Deep Neural Network", "Random Forest",
                 "XGBoost" if HAS_XGB else "N/A"],
    "Accuracy": [round(dnn_acc, 4), round(rf_acc, 4),
                 round(xgb_acc, 4)],
})
acc_df.to_csv(os.path.join(RPT, "accuracy_report.csv"), index=False)
print("\nAccuracy Report:")
print(acc_df.to_string(index=False))

# ── 8. best model flag ──────────────────────────────────────────────────────
accs = {"DNN": dnn_acc, "RF": rf_acc}
if HAS_XGB:
    accs["XGB"] = xgb_acc
best_name = max(accs, key=accs.get)
print(f"\nBest model: {best_name} ({accs[best_name]:.4f})")

# ── 9. confusion matrix ─────────────────────────────────────────────────────
y_pred = np.argmax(model.predict(X_te), axis=1)
cm = confusion_matrix(y_te, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.title("Confusion Matrix – DNN")
plt.ylabel("True"); plt.xlabel("Predicted")
plt.tight_layout()
cm_path = os.path.join(RPT, "confusion_matrix.png")
plt.savefig(cm_path, dpi=150); plt.close()

# training history plot
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history["accuracy"],     label="Train")
plt.plot(history.history["val_accuracy"], label="Val")
plt.title("Accuracy"); plt.legend()
plt.subplot(1, 2, 2)
plt.plot(history.history["loss"],     label="Train")
plt.plot(history.history["val_loss"], label="Val")
plt.title("Loss"); plt.legend()
plt.tight_layout()
hist_path = os.path.join(RPT, "training_history.png")
plt.savefig(hist_path, dpi=150); plt.close()

# ── 10. SHAP ────────────────────────────────────────────────────────────────
shap_path = os.path.join(RPT, "shap_analysis.png")
if HAS_SHAP:
    print("\nRunning SHAP …")
    try:
        explainer = shap.TreeExplainer(rf)
        shap_vals = explainer.shap_values(X_te[:500])
        # For multiclass take class 2 (High Risk)
        sv = shap_vals[2] if isinstance(shap_vals, list) else shap_vals
        plt.figure(figsize=(10, 8))
        shap.summary_plot(sv, X_te[:500],
                          feature_names=FEATURE_COLS,
                          show=False, plot_type="bar")
        plt.title("SHAP Feature Importance (High Risk class)")
        plt.tight_layout()
        plt.savefig(shap_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"SHAP saved → {shap_path}")
    except Exception as e:
        print(f"SHAP failed: {e}")
        HAS_SHAP = False

if not HAS_SHAP or not os.path.exists(shap_path):
    # Fallback: RF feature importance
    fi = pd.Series(rf.feature_importances_, index=FEATURE_COLS).nlargest(15)
    plt.figure(figsize=(10, 7))
    fi.sort_values().plot(kind="barh", color="#2196F3")
    plt.title("Feature Importance (Random Forest)")
    plt.tight_layout()
    plt.savefig(shap_path, dpi=150); plt.close()
    print(f"Feature importance plot saved → {shap_path}")

# ── 11. PDF report ──────────────────────────────────────────────────────────
if HAS_RL:
    print("\nGenerating PDF report …")
    pdf_path = os.path.join(RPT, "final_report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch,  bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    H1  = styles["h1"]
    H2  = styles["h2"]
    NRM = styles["Normal"]
    story = []

    def heading(text, style=H1):
        story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.1*inch))

    def body(text):
        story.append(Paragraph(text, NRM))
        story.append(Spacer(1, 0.05*inch))

    heading("Deep Learning Based Early Warning System for Water-Borne Disease Prediction")
    body("Generated automatically by the training pipeline.")
    story.append(Spacer(1, 0.2*inch))

    heading("1. Dataset Overview", H2)
    body(f"Total Records: {len(df)}")
    body(f"Features: {len(FEATURE_COLS)}")
    dist = pd.read_csv(DATA)["disease_risk"].value_counts()
    for cls, cnt in dist.items():
        body(f"  • {cls}: {cnt} ({cnt/len(df)*100:.1f}%)")

    heading("2. Model Accuracy", H2)
    tbl_data = [["Model", "Test Accuracy"]] + \
               [[r["Model"], f"{r['Accuracy']*100:.2f}%"]
                for _, r in acc_df.iterrows()]
    tbl = Table(tbl_data, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1565C0")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#E3F2FD")]),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.2*inch))

    heading("3. Classification Report (DNN)", H2)
    cr = classification_report(y_te, y_pred,
                                target_names=le.classes_, output_dict=True)
    cr_rows = [["Class", "Precision", "Recall", "F1", "Support"]]
    for cls in le.classes_:
        r = cr[cls]
        cr_rows.append([cls, f"{r['precision']:.3f}",
                        f"{r['recall']:.3f}", f"{r['f1-score']:.3f}",
                        str(int(r['support']))])
    cr_tbl = Table(cr_rows, hAlign="LEFT")
    cr_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2E7D32")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#E8F5E9")]),
    ]))
    story.append(cr_tbl)
    story.append(Spacer(1, 0.2*inch))

    heading("4. Confusion Matrix", H2)
    if os.path.exists(cm_path):
        story.append(RLImage(cm_path, width=3.5*inch, height=3*inch))
    story.append(PageBreak())

    heading("5. Training History", H2)
    if os.path.exists(hist_path):
        story.append(RLImage(hist_path, width=6*inch, height=2.5*inch))
    story.append(Spacer(1, 0.2*inch))

    heading("6. SHAP / Feature Importance Analysis", H2)
    if os.path.exists(shap_path):
        story.append(RLImage(shap_path, width=6*inch, height=4*inch))
    story.append(Spacer(1, 0.2*inch))

    heading("7. Conclusion", H2)
    body(f"The Deep Neural Network achieved {dnn_acc*100:.2f}% accuracy on the test set, "
         f"outperformed by {best_name} ({accs[best_name]*100:.2f}%). "
         "The system is capable of early warning detection for water-borne diseases "
         "using environmental and water quality parameters with high confidence.")

    doc.build(story)
    print(f"PDF report saved → {pdf_path}")

print("\n✅ Training pipeline complete.")
