#!/bin/bash

echo "🚀 Iniciando CatchAI Document Copilot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo " Archivo .env no encontrado"
    echo " Ejecuta primero: python setup.py"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d venv ]; then
    echo " Entorno virtual no encontrado"
    echo " Ejecuta primero: python setup.py"
    exit 1
fi

# Activate virtual environment and run app
echo " Activando entorno virtual..."
source venv/bin/activate

echo " Iniciando aplicación Streamlit..."
echo " La aplicación estará disponible en: http://localhost:8501"
echo " Presiona Ctrl+C para detener la aplicación"

streamlit run src/frontend/app.py
