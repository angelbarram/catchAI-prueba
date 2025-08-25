@echo off
echo 🚀 Iniciando CatchAI Document Copilot...

REM Check if .env exists
if not exist .env (
    echo Archivo .env no encontrado
    echo Ejecuta primero: python setup.py
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Entorno virtual no encontrado
    echo Ejecuta primero: python setup.py
    pause
    exit /b 1
)

REM Activate virtual environment and run app
echo Activando entorno virtual...
call venv\Scripts\activate

echo Iniciando aplicación Streamlit...
echo La aplicación estará disponible en: http://localhost:8501
echo Presiona Ctrl+C para detener la aplicación

streamlit run src\frontend\app.py

pause
