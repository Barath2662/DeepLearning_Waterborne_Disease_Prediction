@echo off
REM ============================================================
REM run_project.bat – One-click launcher for WaterGuard AI
REM Compatible with: Windows 10/11
REM ============================================================

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   WaterGuard AI – Early Warning System Launcher          ║
echo ║   Deep Learning Based Water-Borne Disease Prediction     ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

SET PROJECT_DIR=%~dp0
SET VENV_DIR=%PROJECT_DIR%venv
SET BACKEND_DIR=%PROJECT_DIR%backend
SET FRONTEND_DIR=%PROJECT_DIR%frontend

REM ── 1. Virtual environment ───────────────────────────────────
IF NOT EXIST "%VENV_DIR%" (
    echo [INFO] Creating Python virtual environment...
    python -m venv "%VENV_DIR%"
)
CALL "%VENV_DIR%\Scripts\activate.bat"

REM ── 2. Install Python dependencies ───────────────────────────
echo [INFO] Installing Python dependencies...
pip install -q -r "%BACKEND_DIR%\requirements.txt"

REM ── 3. Train model if needed ─────────────────────────────────
IF NOT EXIST "%PROJECT_DIR%models\waterborne_model.h5" (
    echo.
    echo [INFO] Training Deep Learning model (first run)...
    echo        This may take 2-5 minutes...
    cd "%PROJECT_DIR%"
    python train_model.py
    echo [OK] Model training complete!
) ELSE (
    echo [OK] Trained model found - skipping training.
)

REM ── 4. Install frontend dependencies ─────────────────────────
IF NOT EXIST "%FRONTEND_DIR%\node_modules" (
    echo.
    echo [INFO] Installing frontend dependencies...
    cd "%FRONTEND_DIR%"
    npm install
)

REM ── 5. Launch services ───────────────────────────────────────
echo.
echo [INFO] Starting FastAPI backend on http://localhost:8000 ...
cd "%BACKEND_DIR%"
CALL "%VENV_DIR%\Scripts\activate.bat"
start "WaterGuard-Backend" cmd /k "uvicorn app:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo [INFO] Starting React frontend on http://localhost:5173 ...
cd "%FRONTEND_DIR%"
start "WaterGuard-Frontend" cmd /k "npm run dev"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  ✅ WaterGuard AI is running!                            ║
echo ║                                                          ║
echo ║  Dashboard : http://localhost:5173                       ║
echo ║  API       : http://localhost:8000                       ║
echo ║  API Docs  : http://localhost:8000/docs                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
pause
