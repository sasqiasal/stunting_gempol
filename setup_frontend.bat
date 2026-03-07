@echo off
REM Quick Start Script untuk Frontend
REM Jalankan: setup_frontend.bat

echo ================================================
echo    Setup Frontend - Sistem Stunting Gempol
echo ================================================
echo.

REM Check Node.js
echo [1/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js tidak ditemukan!
    echo Silakan install Node.js 18+ dari https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js sudah terinstall
node --version
echo.

REM Check npm
echo [2/4] Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm tidak ditemukan!
    pause
    exit /b 1
)
echo [OK] npm sudah terinstall
npm --version
echo.

REM Install dependencies
echo [3/4] Installing dependencies...
echo This may take a few minutes...
if not exist "node_modules" (
    npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] node_modules already exists
    echo Run 'npm install' if you need to update dependencies
)
echo.

REM Check .env
echo [4/4] Checking environment configuration...
if not exist ".env" (
    echo [WARNING] File .env tidak ditemukan!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo ================================================
    echo [INFO] Silakan edit file .env jika perlu
    echo Default configuration:
    echo   VITE_API_BASE_URL=http://localhost:8000/api/v1
    echo   Map center: Gempol, Pasuruan
    echo ================================================
    echo.
) else (
    echo [OK] File .env found
)
echo.

echo ================================================
echo    Frontend Setup Complete!
echo ================================================
echo.
echo To start the development server, run:
echo   npm run dev
echo.
echo App will be available at:
echo   http://localhost:5173
echo.
echo Make sure backend is running at:
echo   http://localhost:8000
echo.
pause
