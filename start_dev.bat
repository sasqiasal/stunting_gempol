@echo off
REM Quick Start untuk Development
REM Menjalankan Backend dan Frontend sekaligus

echo ================================================
echo   Starting Sistem Stunting Desa Gempol
echo ================================================
echo.

echo Starting Backend Server...
start cmd /k "cd backend && call venv\Scripts\activate.bat && uvicorn main:app --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend Dev Server...
start cmd /k "cd frontend && npm run dev"

echo.
echo ================================================
echo   Servers are starting...
echo ================================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo Login Credentials:
echo   Admin: admin@gempol.id / admin123
echo   Kader: kader@gempol.id / admin123
echo.
echo Press any key to close this window...
pause >nul
