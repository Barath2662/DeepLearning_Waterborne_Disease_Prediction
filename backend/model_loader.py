"""
Centralised model and artifact loader for the FastAPI backend.
"""

import json
import os
import pickle
from typing import Any, Dict, Tuple

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
MDL = os.path.join(BASE, "..", "models")


def load_pickle(filename: str, label: str):
    path = os.path.join(MDL, filename)
    if not os.path.exists(path):
        raise RuntimeError(f"{label} not found at {path}. Run train_model.py first.")
    with open(path, "rb") as f:
        return pickle.load(f)


def load_json(filename: str, label: str) -> Dict[str, Any]:
    path = os.path.join(MDL, filename)
    if not os.path.exists(path):
        raise RuntimeError(f"{label} not found at {path}. Run train_model.py first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all() -> Tuple[Any, Any, list, Dict[str, Any]]:
    label_enc = load_pickle("label_encoder.pkl", "LabelEncoder")
    feature_cols = load_pickle("feature_columns.pkl", "FeatureColumns")
    best_model = load_pickle("best_model.pkl", "BestModel")
    metadata = load_json("training_metadata.json", "TrainingMetadata")
    return best_model, label_enc, feature_cols, metadata


def build_feature_vector(req_dict: dict, feature_cols: list) -> np.ndarray:
    """Convert a prediction request dict to a one-hot encoded feature array."""
    base = {
        "ph": float(req_dict.get("ph", 7.0)),
        "turbidity": float(req_dict.get("turbidity", 5.0)),
        "dissolved_oxygen": float(req_dict.get("dissolved_oxygen", 6.5)),
        "temperature": float(req_dict.get("temperature", 25.0)),
        "rainfall": float(req_dict.get("rainfall", 100.0)),
        "humidity": float(req_dict.get("humidity", 65.0)),
        "population_density": float(req_dict.get("population_density", 1000.0)),
        "sanitation_index": float(req_dict.get("sanitation_index", 60.0)),
        "bacterial_count": float(req_dict.get("bacterial_count", 300.0)),
        "ecoli_count": float(req_dict.get("ecoli_count", 30.0)),
        "chlorine_level": float(req_dict.get("chlorine_level", 1.0)),
        "previous_cases": float(req_dict.get("previous_cases", 10)),
    }

    water_sources = ["Groundwater", "Lake", "Pond", "River", "Tap", "Well"]
    region_types = ["Coastal", "Hilly", "Rural", "Semi-Urban", "Urban"]
    seasons = ["Monsoon", "Spring", "Summer", "Winter"]

    ws = req_dict.get("water_source", "River")
    for source in water_sources:
        base[f"water_source_{source}"] = 1.0 if ws == source else 0.0

    rt = req_dict.get("region_type", "Urban")
    for region in region_types:
        base[f"region_type_{region}"] = 1.0 if rt == region else 0.0

    se = req_dict.get("season", "Monsoon")
    for season in seasons:
        base[f"season_{season}"] = 1.0 if se == season else 0.0

    row = [base.get(col, 0.0) for col in feature_cols]
    return np.array([row], dtype=np.float32)
