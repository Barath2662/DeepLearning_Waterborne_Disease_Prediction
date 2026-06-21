"""
model_loader.py – Centralised model and artifact loader for the FastAPI backend.
"""

import os, pickle
import numpy as np
import tensorflow as tf

BASE = os.path.dirname(os.path.abspath(__file__))
MDL  = os.path.join(BASE, "..", "models")


def load_pickle(filename, label):
    path = os.path.join(MDL, filename)
    if not os.path.exists(path):
        raise RuntimeError(f"{label} not found at {path}. Run train_model.py first.")
    with open(path, "rb") as f:
        return pickle.load(f)


def load_all():
    scaler       = load_pickle("scaler.pkl",          "Scaler")
    label_enc    = load_pickle("label_encoder.pkl",   "LabelEncoder")
    feature_cols = load_pickle("feature_columns.pkl", "FeatureColumns")

    model_path = os.path.join(MDL, "waterborne_model.h5")
    if not os.path.exists(model_path):
        raise RuntimeError(f"Model not found at {model_path}. Run train_model.py first.")
    model = tf.keras.models.load_model(model_path)

    return model, scaler, label_enc, feature_cols


def build_feature_vector(req_dict: dict, feature_cols: list, scaler) -> np.ndarray:
    """Convert a prediction request dict to a scaled feature array."""
    water_sources = ["Groundwater", "Lake", "Pond", "River", "Tap", "Well"]
    region_types  = ["Coastal", "Hilly", "Rural", "Semi-Urban", "Urban"]
    seasons       = ["Monsoon", "Spring", "Summer", "Winter"]

    base = {
        "ph":                 float(req_dict.get("ph", 7.0)),
        "turbidity":          float(req_dict.get("turbidity", 5.0)),
        "dissolved_oxygen":   float(req_dict.get("dissolved_oxygen", 6.5)),
        "temperature":        float(req_dict.get("temperature", 25.0)),
        "rainfall":           float(req_dict.get("rainfall", 100.0)),
        "humidity":           float(req_dict.get("humidity", 65.0)),
        "population_density": float(req_dict.get("population_density", 1000.0)),
        "sanitation_index":   float(req_dict.get("sanitation_index", 60.0)),
        "bacterial_count":    float(req_dict.get("bacterial_count", 300.0)),
        "ecoli_count":        float(req_dict.get("ecoli_count", 30.0)),
        "chlorine_level":     float(req_dict.get("chlorine_level", 1.0)),
        "previous_cases":     float(req_dict.get("previous_cases", 10)),
    }

    ws = req_dict.get("water_source", "River")
    for s in water_sources:
        base[f"water_source_{s}"] = 1.0 if ws == s else 0.0

    rt = req_dict.get("region_type", "Urban")
    for r in region_types:
        base[f"region_type_{r}"] = 1.0 if rt == r else 0.0

    se = req_dict.get("season", "Monsoon")
    for s in seasons:
        base[f"season_{s}"] = 1.0 if se == s else 0.0

    row = [base.get(col, 0.0) for col in feature_cols]
    arr = np.array([row], dtype=np.float32)
    return scaler.transform(arr)
