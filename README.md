# Machine Learning Based Early Warning System for Water-Borne Disease Prediction

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![XGBoost](https://img.shields.io/badge/XGBoost-2.x-orange)
![Random%20Forest](https://img.shields.io/badge/Random%20Forest-scikit--learn-4caf50)

**A local, open-source early warning system that predicts water-borne disease outbreak risk using classic machine learning models.**

</div>

---

## Overview

This project predicts water-borne disease risk as **Low**, **Medium**, or **High** from 15 environmental and water-quality parameters. The system now uses **Random Forest** and **XGBoost** instead of the earlier neural-network implementation, and the backend serves the best-performing trained model.

The full stack runs locally with:
- Synthetic dataset generation
- Model training and evaluation
- FastAPI prediction API
- React dashboard with analytics charts
- PDF report generation

## Models Used

- Random Forest Classifier
- XGBoost Classifier

The training script evaluates both models, writes the comparison report, stores the best model in `models/best_model.pkl`, and exports feature importance artifacts for the dashboard.

## Project Structure

```text
DeepLearning_Waterborne_Disease_Prediction/
├── dataset/
│   ├── generate_dataset.py
│   └── waterborne_disease_dataset.csv
├── backend/
│   ├── app.py
│   ├── model_loader.py
│   └── requirements.txt
├── frontend/
│   └── src/
├── models/
│   ├── best_model.pkl
│   ├── random_forest_model.pkl
│   ├── xgboost_model.pkl
│   ├── label_encoder.pkl
│   ├── feature_columns.pkl
│   └── training_metadata.json
├── reports/
│   ├── accuracy_report.csv
│   ├── confusion_matrix.png
│   ├── feature_importance.csv
│   ├── feature_importance.png
│   ├── shap_analysis.png
│   └── final_report.pdf
├── train_model.py
├── run_project.sh
└── run_project.bat
```

## Setup

### Python dependencies

```bash
pip install -r backend/requirements.txt
```

### Train the models

```bash
python train_model.py
```

### Start the API

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Start the frontend

```bash
cd frontend
npm install
npm run dev
```

### One-command launcher

- Linux/macOS: `./run_project.sh`
- Windows: `run_project.bat`

## API Endpoints

- `GET /health` - backend and model status
- `POST /predict` - returns risk class, confidence, and recommendation
- `GET /analytics` - dataset stats, model accuracy, and feature importance

## Outputs

The training pipeline generates:
- `reports/accuracy_report.csv`
- `reports/confusion_matrix.png`
- `reports/feature_importance.csv`
- `reports/feature_importance.png`
- `reports/shap_analysis.png`
- `reports/final_report.pdf`

## Notes

- The frontend chart data is populated from the backend analytics endpoint.
- The project keeps the same input form and dashboard layout, but the model stack is now machine learning instead of the older neural-network approach.
- If you retrain the models, restart the backend so it reloads `models/best_model.pkl`.
