@echo off
setlocal
cd /d "%~dp0"

if exist "C:\Users\Pc\anaconda3\python.exe" (
    set "PYTHON_EXE=C:\Users\Pc\anaconda3\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Starting Bank Churn Prediction app...
echo Local URL: http://127.0.0.1:8501
"%PYTHON_EXE%" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
pause
