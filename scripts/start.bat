@echo off
chcp 65001 >nul

echo Activating conda py312 environment...
call d:\dev\anaconda3\Scripts\activate.bat py312

set PYTHONPATH=%CD%
set NO_COLOR=1

echo ============================================
echo  PythonWeb - Server Startup
echo  Python: %CONDA_PREFIX%
echo ============================================

echo [1/3] Running database migrations...
python -m alembic upgrade head

echo [2/3] Creating initial data...
python -m app.initial_data

echo [3/3] Starting FastAPI server...
echo ============================================
echo  API Docs: http://localhost:8000/docs
echo  Health:   http://localhost:8000/api/v1/utils/health-check/
echo ============================================
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
