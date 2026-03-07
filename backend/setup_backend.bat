@echo off
REM Quick Start Script untuk Backend
REM Jalankan: setup_backend.bat

echo ================================================
echo    Setup Backend - Sistem Stunting Gempol
echo ================================================
echo.

REM Check Python
echo [1/7] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python 3.10+ dari https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python sudah terinstall
echo.

REM Check if venv exists
echo [2/7] Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate venv
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [4/7] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Check .env
echo [5/7] Checking environment configuration...
if not exist ".env" (
    echo [WARNING] File .env tidak ditemukan!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo ================================================
    echo [IMPORTANT] Silakan edit file .env dengan:
    echo 1. SUPABASE_URL dari Supabase dashboard
    echo 2. SUPABASE_KEY (anon key)
    echo 3. SUPABASE_SERVICE_KEY (service_role key)
    echo 4. DATABASE_URL (connection string)
    echo 5. SECRET_KEY (generate dengan: python generate_secret_key.py)
    echo.
    echo Panduan lengkap: SETUP_SUPABASE.md
    echo ================================================
    echo.
    pause
) else (
    echo [OK] File .env found
)
echo.

REM Test connection
echo [6/7] Testing Supabase connection...
python test_connection.py
if errorlevel 1 (
    echo [ERROR] Koneksi ke Supabase gagal!
    echo Silakan cek file .env dan pastikan credentials benar
    echo Panduan: SETUP_SUPABASE.md
    pause
    exit /b 1
)
echo.

REM Train model
echo [7/7] Training KNN model...
if not exist "app\ml\models\knn_stunting_model.pkl" (
    echo Training model for the first time...
    python train_model.py
    if errorlevel 1 (
        echo [ERROR] Model training failed
        pause
        exit /b 1
    )
    echo [OK] Model trained successfully
) else (
    echo [OK] Model already exists
)
echo.

echo ================================================
echo    Backend Setup Complete!
echo ================================================
echo.
echo To start the server, run:
echo   uvicorn main:app --reload
echo.
echo API will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/docs (Swagger UI)
echo.
pause
