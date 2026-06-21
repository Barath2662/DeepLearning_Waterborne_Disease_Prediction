# Deep Learning Based Early Warning System for Water-Borne Disease Prediction

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?logo=tensorflow)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![License](https://img.shields.io/badge/License-Open%20Source-brightgreen)

**An AI-powered, open-source early warning system that predicts water-borne disease outbreak risk using deep learning.**

</div>

---

## 📌 Project Overview

This academic mini-project implements a complete, end-to-end **Deep Learning Based Early Warning System** for predicting water-borne disease risk. The system analyzes 15 environmental and water quality parameters and classifies the disease risk as **Low**, **Medium**, or **High** with confidence scores and actionable recommendations.

The entire system runs **100% locally** using open-source tools — no paid APIs, no cloud services.

---

## 🎯 Objectives

- Predict water-borne disease outbreak risk before it occurs
- Analyze 15 environmental and water quality parameters
- Achieve ≥ 90% classification accuracy using deep learning
- Provide explainable AI insights using SHAP
- Deliver a modern, responsive web dashboard
- Generate automated PDF reports with confusion matrix and classification results

---

## 🏗️ Technologies Used

### Machine Learning & AI
| Library | Version | Purpose |
|---------|---------|---------|
| TensorFlow / Keras | 2.x | Deep Neural Network |
| Scikit-learn | 1.x | Random Forest, preprocessing |
| XGBoost | Latest | Gradient Boosting model |
| SHAP | Latest | Explainable AI |
| NumPy / Pandas | Latest | Data manipulation |
| Matplotlib / Seaborn | Latest | Visualizations |

### Backend
| Tool | Purpose |
|------|---------|
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Pydantic | Data validation |

### Frontend
| Tool | Purpose |
|------|---------|
| React 18 | UI framework |
| Vite | Build tool |
| Tailwind CSS | Styling |
| Chart.js | Data visualizations |
| Axios | HTTP client |

### Reporting
| Tool | Purpose |
|------|---------|
| ReportLab | PDF generation |

---

## 📁 Project Structure

```
DeepLearning_Waterborne_Disease_Prediction/
│
├── dataset/
│   ├── generate_dataset.py          # Synthetic dataset generator
│   └── waterborne_disease_dataset.csv
│
├── backend/
│   ├── app.py                       # FastAPI application
│   ├── model_loader.py              # Model loading utilities
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/              # Chart.js visualizations
│   │   │   ├── Header.jsx
│   │   │   ├── StatCards.jsx
│   │   │   ├── InputPanel.jsx
│   │   │   └── PredictionResult.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── api.js
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── models/
│   ├── waterborne_model.h5          # Trained DNN model
│   ├── scaler.pkl                   # StandardScaler
│   ├── label_encoder.pkl            # LabelEncoder
│   └── feature_columns.pkl          # Feature column names
│
├── reports/
│   ├── final_report.pdf             # Auto-generated PDF report
│   ├── shap_analysis.png            # SHAP feature importance
│   ├── confusion_matrix.png         # Model evaluation
│   ├── training_history.png         # Training curves
│   └── accuracy_report.csv         # Model comparison table
│
├── notebooks/
│   └── training.ipynb               # Jupyter notebook
│
├── train_model.py                   # Full training pipeline
├── README.md
├── run_project.sh                   # Linux/macOS launcher
└── run_project.bat                  # Windows launcher
```

---

## 📊 Dataset Description

The system uses a synthetic dataset of **15,000 records** generated programmatically with realistic statistical distributions per risk class.

### Features

| Feature | Type | Description |
|---------|------|-------------|
| `ph` | Float | Water pH (0–14) |
| `turbidity` | Float | Turbidity in NTU |
| `dissolved_oxygen` | Float | DO in mg/L |
| `temperature` | Float | Water temperature °C |
| `rainfall` | Float | Rainfall in mm |
| `humidity` | Float | Relative humidity % |
| `population_density` | Float | People per km² |
| `sanitation_index` | Float | Sanitation score 0–100 |
| `bacterial_count` | Float | CFU per mL |
| `ecoli_count` | Float | E.coli CFU per 100mL |
| `chlorine_level` | Float | Chlorine in mg/L |
| `water_source` | Categorical | River/Lake/Groundwater/Tap/Well/Pond |
| `region_type` | Categorical | Urban/Rural/Semi-Urban/Coastal/Hilly |
| `season` | Categorical | Summer/Monsoon/Winter/Spring |
| `previous_cases` | Integer | Prior disease cases count |

### Target Classes
- **Low Risk** (40%) – Good water quality, safe conditions
- **Medium Risk** (30%) – Moderate concerns, monitoring needed
- **High Risk** (30%) – Poor quality, immediate action required

---

## 🧠 Model Architecture

### Deep Neural Network (DNN)
```
Input Layer  →  [N features]
Dense(256)   →  BatchNorm → Dropout(0.3)
Dense(128)   →  BatchNorm → Dropout(0.3)
Dense(64)    →  BatchNorm → Dropout(0.2)
Dense(32)    →  ReLU
Dense(3)     →  Softmax
```

**Training Strategy:**
- Optimizer: Adam (lr=0.001)
- Loss: Sparse Categorical Crossentropy
- EarlyStopping (patience=10, monitor=val_accuracy)
- ModelCheckpoint (save best)
- ReduceLROnPlateau (patience=5, factor=0.5)

### Model Comparison
| Model | Test Accuracy |
|-------|-------------|
| Deep Neural Network | ~100% |
| Random Forest | ~100% |
| XGBoost | ~100% |

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip

### Quick Start (Linux/macOS)

```bash
# Clone / navigate to project
cd DeepLearning_Waterborne_Disease_Prediction

# Run automated setup
chmod +x run_project.sh
./run_project.sh
```

### Manual Setup

#### 1. Create Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows
```

#### 2. Install Python dependencies
```bash
pip install -r backend/requirements.txt
```

#### 3. Train the model
```bash
python train_model.py
```

#### 4. Start the backend
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### 5. Set up and start the frontend
```bash
cd frontend
npm install
npm run dev
```

#### 6. Open browser
```
Frontend:  http://localhost:5173
API Docs:  http://localhost:8000/docs
```

---

## 🔌 API Documentation

### POST /predict

Predict disease risk for given water quality parameters.

**Request Body:**
```json
{
  "ph": 7.2,
  "turbidity": 5.0,
  "dissolved_oxygen": 6.5,
  "temperature": 28.0,
  "rainfall": 150.0,
  "humidity": 70.0,
  "population_density": 1200.0,
  "sanitation_index": 65.0,
  "bacterial_count": 350.0,
  "ecoli_count": 40.0,
  "chlorine_level": 1.2,
  "water_source": "River",
  "region_type": "Urban",
  "season": "Monsoon",
  "previous_cases": 20
}
```

**Response:**
```json
{
  "risk": "Medium",
  "confidence": "87.3%",
  "recommendation": "Elevated risk detected. Increase water testing frequency.",
  "probabilities": {
    "Low": 5.2,
    "Medium": 87.3,
    "High": 7.5
  }
}
```

### GET /analytics

Returns dataset statistics, class distribution, and model accuracy.

### GET /health

Returns backend health status.

---

## 📈 Dashboard Features

- **🔬 Input Panel** – 15 parameter inputs with quick scenario buttons
- **🎯 Prediction Result** – Risk level, confidence gauge, probability breakdown
- **🥧 Risk Distribution** – Doughnut chart of dataset class distribution
- **📈 Model Accuracy** – Bar chart comparing DNN, RF, XGBoost
- **🕸️ Water Quality Radar** – 6 quality indicators in radar chart
- **🔬 Feature Importance** – SHAP-based horizontal bar chart

---

## 🔍 Explainable AI (SHAP)

SHAP (SHapley Additive exPlanations) is used to explain model predictions:
- TreeExplainer on Random Forest
- Feature importance for "High Risk" class
- Saved as `reports/shap_analysis.png`
- Included in automated PDF report

---

## 📝 Reports Generated

| File | Description |
|------|-------------|
| `reports/final_report.pdf` | Complete academic PDF report |
| `reports/shap_analysis.png` | SHAP feature importance plot |
| `reports/confusion_matrix.png` | DNN confusion matrix |
| `reports/training_history.png` | Accuracy & loss curves |
| `reports/accuracy_report.csv` | Model accuracy comparison |

---

## 🖼️ Screenshots

Place screenshots here after running the project:
- Dashboard overview
- Prediction result panel
- Charts and visualizations

---

## 🔭 Future Scope

1. **Real-time data integration** – Connect with IoT water quality sensors
2. **Time-series prediction** – LSTM/GRU for temporal outbreak forecasting
3. **Geospatial mapping** – Disease risk heatmaps with Leaflet.js
4. **Mobile app** – React Native companion for field workers
5. **Alert system** – Email/SMS notifications for high-risk areas
6. **Multi-region support** – Geographic model specialization
7. **Federated learning** – Privacy-preserving training across regions
8. **Docker deployment** – Containerized one-command deployment

---

## 📄 License

This project is developed for academic purposes using 100% open-source software.
All libraries and frameworks used are under Apache 2.0, MIT, or BSD licenses.

---

<div align="center">
<strong>WaterGuard AI</strong> — Deep Learning Based Early Warning System for Water-Borne Disease Prediction<br/>
Built with ❤️ using Python · TensorFlow · FastAPI · React
</div>
