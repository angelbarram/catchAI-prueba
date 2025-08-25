"""
Test configuration and utilities
"""
import pytest
import tempfile
import os
from pathlib import Path

# Add src to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def sample_text():
    """Sample text content for testing"""
    return """
    Este es un documento de prueba para CatchAI.
    
    Contiene información sobre inteligencia artificial y procesamiento de lenguaje natural.
    
    Los temas principales incluyen:
    - Machine Learning
    - Deep Learning  
    - Procesamiento de texto
    - Análisis de documentos
    
    Este documento sirve para validar que el sistema puede extraer y procesar
    contenido de manera efectiva.
    """

@pytest.fixture
def sample_pdf_path(temp_dir, sample_text):
    """Create a sample PDF file for testing"""
    # This would require reportlab or similar to create actual PDF
    # For now, we'll create a text file with .pdf extension for basic testing
    pdf_path = os.path.join(temp_dir, "sample.pdf")
    with open(pdf_path, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    return pdf_path
