@echo off
chcp 65001 >nul
echo Activating conda py312...
call d:\dev\anaconda3\Scripts\activate.bat py312
set PYTHONPATH=%CD%
echo Starting FastAPI server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
