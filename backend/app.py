"""
FastAPI Backend – Waterborne Disease Prediction System
Endpoints:  POST /predict   GET /analytics   GET /health
"""

import os, pickle, json, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# ── load model + artifacts ──────────────────────────────────────────────────
BASE  = os.path.dirname(os.path.abspath(__file__))
MDL   = os.path.join(BASE, "..", "models")
DATA  = os.path.join(BASE, "..", "dataset", "waterborne_disease_dataset.csv")
RPT   = os.path.join(BASE, "..", "reports", "accuracy_report.csv")

def load_artifact(path, label="artifact"):
    if not os.path.exists(path):
        raise RuntimeError(f"{label} not found at {path}. "
                           "Run train_model.py first.")
    with open(path, "rb") as f:
        return pickle.load(f)

scaler        = load_artifact(os.path.join(MDL, "scaler.pkl"),          "Scaler")
label_enc     = load_artifact(os.path.join(MDL, "label_encoder.pkl"),   "LabelEncoder")
feature_cols  = load_artifact(os.path.join(MDL, "feature_columns.pkl"), "FeatureCols")

import tensorflow as tf
MODEL_PATH = os.path.join(MDL, "waterborne_model.h5")
if not os.path.exists(MODEL_PATH):
    raise RuntimeError("Model not found. Run train_model.py first.")
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded.")

# ── FastAPI app ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Waterborne Disease Early Warning System",
    description="Deep Learning based water-borne disease risk prediction API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RECOMMENDATIONS = {
    "Low":    "Water quality is acceptable. Continue routine monitoring.",
    "Medium": "Elevated risk detected. Increase water testing frequency and "
              "inspect sanitation infrastructure.",
    "High":   "IMMEDIATE ACTION REQUIRED. Issue public advisory, halt "
              "unsafe water usage, and deploy emergency response teams.",
}

# ── request / response schemas ──────────────────────────────────────────────
class PredictRequest(BaseModel):
    ph:                 float = Field(7.0,   ge=0,   le=14)
    turbidity:          float = Field(5.0,   ge=0,   le=1000)
    dissolved_oxygen:   float = Field(6.5,   ge=0,   le=20)
    temperature:        float = Field(25.0,  ge=-10, le=60)
    rainfall:           float = Field(100.0, ge=0)
    humidity:           float = Field(65.0,  ge=0,   le=100)
    population_density: float = Field(1000,  ge=0)
    sanitation_index:   float = Field(60.0,  ge=0,   le=100)
    bacterial_count:    float = Field(300.0, ge=0)
    ecoli_count:        float = Field(30.0,  ge=0)
    chlorine_level:     float = Field(1.0,   ge=0)
    water_source:       str   = Field("River")
    region_type:        str   = Field("Urban")
    season:             str   = Field("Monsoon")
    previous_cases:     int   = Field(10,    ge=0)

class PredictResponse(BaseModel):
    risk:           str
    confidence:     str
    recommendation: str
    probabilities:  dict

# ── helpers ─────────────────────────────────────────────────────────────────
def build_feature_vector(req: PredictRequest) -> np.ndarray:
    """Convert request to one-hot encoded & scaled feature array."""
    base = {
        "ph":                 req.ph,
        "turbidity":          req.turbidity,
        "dissolved_oxygen":   req.dissolved_oxygen,
        "temperature":        req.temperature,
        "rainfall":           req.rainfall,
        "humidity":           req.humidity,
        "population_density": req.population_density,
        "sanitation_index":   req.sanitation_index,
        "bacterial_count":    req.bacterial_count,
        "ecoli_count":        req.ecoli_count,
        "chlorine_level":     req.chlorine_level,
        "previous_cases":     float(req.previous_cases),
    }
    # One-hot for water_source
    for ws in ["Groundwater", "Lake", "Pond", "River", "Tap", "Well"]:
        base[f"water_source_{ws}"] = 1.0 if req.water_source == ws else 0.0
    # One-hot for region_type
    for rt in ["Coastal", "Hilly", "Rural", "Semi-Urban", "Urban"]:
        base[f"region_type_{rt}"] = 1.0 if req.region_type == rt else 0.0
    # One-hot for season
    for se in ["Monsoon", "Spring", "Summer", "Winter"]:
        base[f"season_{se}"] = 1.0 if req.season == se else 0.0

    # Align with training feature_cols (fill missing with 0)
    row = [base.get(col, 0.0) for col in feature_cols]
    arr = np.array([row], dtype=np.float32)
    return scaler.transform(arr)

# ── routes ───────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "waterborne_model.h5"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        X  = build_feature_vector(req)
        p  = model.predict(X, verbose=0)[0]
        idx = int(np.argmax(p))
        risk = label_enc.classes_[idx]
        conf = float(p[idx]) * 100
        probs = {label_enc.classes_[i]: round(float(p[i]) * 100, 2)
                 for i in range(len(p))}
        return PredictResponse(
            risk=risk,
            confidence=f"{conf:.1f}%",
            recommendation=RECOMMENDATIONS[risk],
            probabilities=probs,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
def analytics():
    result = {
        "model_accuracy":    {},
        "dataset_stats":     {},
        "class_distribution":{},
        "feature_names":     feature_cols,
    }
    # accuracy report
    if os.path.exists(RPT):
        acc = pd.read_csv(RPT)
        result["model_accuracy"] = acc.set_index("Model")["Accuracy"].to_dict()

    # dataset stats
    if os.path.exists(DATA):
        df = pd.read_csv(DATA)
        num_cols = ["ph","turbidity","dissolved_oxygen","temperature",
                    "rainfall","humidity","population_density",
                    "sanitation_index","bacterial_count","ecoli_count",
                    "chlorine_level","previous_cases"]
        stats = df[num_cols].describe().round(2).to_dict()
        result["dataset_stats"]     = stats
        result["class_distribution"] = df["disease_risk"].value_counts().to_dict()
        result["total_records"]      = int(len(df))

    return result

@app.get("/")
def root():
    return {"message": "Waterborne Disease Early Warning System API",
            "docs": "/docs"}
