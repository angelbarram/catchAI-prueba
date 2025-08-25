#!/usr/bin/env python3
"""
Setup script for CatchAI Document Copilot
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e.stderr}")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print("❌ Se requiere Python 3.8 o superior")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def setup_environment():
    """Setup Python environment"""
    print("🚀 Configurando entorno de CatchAI Document Copilot...\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creando entorno virtual"):
            return False
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
        python_command = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"
        python_command = "venv/bin/python"
    
    # Upgrade pip
    if not run_command(f"{pip_command} install --upgrade pip", "Actualizando pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_command} install -r requirements.txt", "Instalando dependencias"):
        return False
    
    # Create .env file if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            run_command("copy .env.example .env" if os.name == 'nt' else "cp .env.example .env", 
                       "Creando archivo .env")
            print("\n⚠️  IMPORTANTE: Edita el archivo .env y añade tu OPENAI_API_KEY")
        else:
            print("❌ Archivo .env.example no encontrado")
            return False
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    print("✅ Directorio de datos creado")
    
    print(f"""
🎉 ¡Configuración completada!

📋 Próximos pasos:
1. Edita el archivo .env y añade tu OPENAI_API_KEY
2. Activa el entorno virtual:
   - Windows: {activate_script}
   - Unix/Linux/MacOS: {activate_script}
3. Ejecuta la aplicación:
   - streamlit run src/frontend/app.py
   - O usa Docker: docker-compose up

🌐 La aplicación estará disponible en: http://localhost:8501
""")
    
    return True

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--docker":
        print("🐳 Configuración para Docker...")
        
        # Check if Docker is installed
        if not run_command("docker --version", "Verificando Docker"):
            print("❌ Docker no está instalado. Por favor instala Docker y Docker Compose.")
            return False
        
        if not run_command("docker-compose --version", "Verificando Docker Compose"):
            print("❌ Docker Compose no está instalado.")
            return False
        
        # Create .env file
        if not Path(".env").exists():
            run_command("copy .env.example .env" if os.name == 'nt' else "cp .env.example .env", 
                       "Creando archivo .env")
        
        print("""
🐳 Configuración de Docker completada!

📋 Para ejecutar con Docker:
1. Edita el archivo .env y añade tu OPENAI_API_KEY
2. Ejecuta: docker-compose up -d
3. Accede a: http://localhost:8501

Para ver logs: docker-compose logs -f
Para detener: docker-compose down
""")
    else:
        setup_environment()

if __name__ == "__main__":
    main()
