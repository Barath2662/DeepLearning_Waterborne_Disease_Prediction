"""
FastAPI Backend - Waterborne Disease Prediction System
Endpoints:  POST /predict   GET /analytics   GET /health
"""

import os
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model_loader import build_feature_vector, load_all

BASE = os.path.dirname(os.path.abspath(__file__))
MDL = os.path.join(BASE, "..", "models")
DATA = os.path.join(BASE, "..", "dataset", "waterborne_disease_dataset.csv")
RPT = os.path.join(BASE, "..", "reports", "accuracy_report.csv")

best_model, label_enc, feature_cols, metadata = load_all()
print(f"Model loaded: {metadata.get('best_model', 'unknown')}")

app = FastAPI(
    title="Waterborne Disease Early Warning System",
    description="Machine learning based water-borne disease risk prediction API",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RECOMMENDATIONS = {
    "Low": "Water quality is acceptable. Continue routine monitoring.",
    "Medium": "Elevated risk detected. Increase water testing frequency and inspect sanitation infrastructure.",
    "High": "IMMEDIATE ACTION REQUIRED. Issue public advisory, halt unsafe water usage, and deploy emergency response teams.",
}

# Waterborne diseases mapping by risk level
DISEASE_MAPPING = {
    "Low": ["No Disease - Water is Safe", "Safe for Consumption"],
    "Medium": ["Typhoid", "Hepatitis A", "Diarrhea", "Giardiasis"],
    "High": ["Cholera", "Dysentery", "Cryptosporidiosis", "E. coli Infection", "Hepatitis E"]
}


class PredictRequest(BaseModel):
    ph: float = Field(7.0, ge=0, le=14)
    turbidity: float = Field(5.0, ge=0, le=1000)
    dissolved_oxygen: float = Field(6.5, ge=0, le=20)
    temperature: float = Field(25.0, ge=-10, le=60)
    rainfall: float = Field(100.0, ge=0)
    humidity: float = Field(65.0, ge=0, le=100)
    population_density: float = Field(1000, ge=0)
    sanitation_index: float = Field(60.0, ge=0, le=100)
    bacterial_count: float = Field(300.0, ge=0)
    ecoli_count: float = Field(30.0, ge=0)
    chlorine_level: float = Field(1.0, ge=0)
    water_source: str = Field("River")
    region_type: str = Field("Urban")
    season: str = Field("Monsoon")
    previous_cases: int = Field(10, ge=0)


class PredictResponse(BaseModel):
    risk: str
    confidence: str
    recommendation: str
    probabilities: dict
    diseases: list


def _predict_proba(model, X: np.ndarray) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    preds = model.predict(X)
    if preds.ndim == 1:
        probs = np.zeros((len(preds), len(label_enc.classes_)), dtype=np.float32)
        probs[np.arange(len(preds)), preds.astype(int)] = 1.0
        return probs
    return preds


@app.get("/health")
def health():
    return {
        "status": "ok",
        "best_model": metadata.get("best_model", "unknown"),
        "test_accuracy": metadata.get("test_accuracy"),
    }


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        X = build_feature_vector(req.model_dump(), feature_cols)
        p = _predict_proba(best_model, X)[0]
        idx = int(np.argmax(p))
        risk = label_enc.classes_[idx]
        conf = float(p[idx]) * 100
        probs = {label_enc.classes_[i]: round(float(p[i]) * 100, 2) for i in range(len(p))}
        return PredictResponse(
            risk=risk,
            confidence=f"{conf:.1f}%",
            recommendation=RECOMMENDATIONS[risk],
            probabilities=probs,
            diseases=DISEASE_MAPPING[risk],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/analytics")
def analytics():
    result = {
        "model_accuracy": {},
        "dataset_stats": {},
        "class_distribution": {},
        "feature_names": feature_cols,
        "best_model": metadata.get("best_model", "unknown"),
        "best_model_accuracy": metadata.get("test_accuracy"),
        "feature_importance": [],
    }

    if os.path.exists(RPT):
        acc = pd.read_csv(RPT)
        if {"Model", "Test Accuracy"}.issubset(acc.columns):
            result["model_accuracy"] = acc.set_index("Model")["Test Accuracy"].to_dict()
        elif {"Model", "Accuracy"}.issubset(acc.columns):
            result["model_accuracy"] = acc.set_index("Model")["Accuracy"].to_dict()

    if os.path.exists(DATA):
        df = pd.read_csv(DATA)
        num_cols = [
            "ph",
            "turbidity",
            "dissolved_oxygen",
            "temperature",
            "rainfall",
            "humidity",
            "population_density",
            "sanitation_index",
            "bacterial_count",
            "ecoli_count",
            "chlorine_level",
            "previous_cases",
        ]
        result["dataset_stats"] = df[num_cols].describe().round(2).to_dict()
        result["class_distribution"] = df["disease_risk"].value_counts().to_dict()
        result["total_records"] = int(len(df))

    importance_path = os.path.join(BASE, "..", "reports", "feature_importance.csv")
    if os.path.exists(importance_path):
        fi = pd.read_csv(importance_path)
        if {"feature", "importance"}.issubset(fi.columns):
            result["feature_importance"] = fi.to_dict(orient="records")
        else:
            feature_col = fi.columns[0]
            importance_col = fi.columns[-1]
            result["feature_importance"] = [
                {"feature": str(row[feature_col]), "importance": float(row[importance_col])}
                for _, row in fi.iterrows()
            ]

    return result


@app.get("/")
def root():
    return {"message": "Waterborne Disease Early Warning System API", "docs": "/docs"}
