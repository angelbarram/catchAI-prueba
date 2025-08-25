# 🚀 Inicio Rápido - CatchAI Document Copilot

## ⚡ Configuración Express (5 minutos)

### 1. 🔑 Configurar API Key
Edita el archivo `.env` y añade tu clave de OpenAI:
```
OPENAI_API_KEY=tu_clave_aqui
```

### 2. 🏃‍♂️ Ejecutar la aplicación

#### Opción A: Script automático (Recomendado)
```bash
# Windows
run.bat

# Linux/Mac
chmod +x run.sh
./run.sh
```

#### Opción B: Manual
```bash
# Activar entorno virtual
venv_catchai\Scripts\activate  # Windows
# source venv_catchai/bin/activate  # Linux/Mac

# Ejecutar aplicación
streamlit run src/frontend/app.py
```

#### Opción C: Docker
```bash
docker-compose up -d
```

### 3. 🌐 Acceder
Abre tu navegador en: http://localhost:8501

## 📋 Checklist de Verificación

- [ ] ✅ Python 3.8+ instalado
- [ ] ✅ Dependencias instaladas (requirements.txt)
- [ ] ✅ Archivo .env configurado con OPENAI_API_KEY
- [ ] ✅ Aplicación ejecutándose en puerto 8501

## 🎯 Primera Prueba

1. **Sube documentos**: Arrastra hasta 5 PDFs en la barra lateral
2. **Procesa**: Haz clic en "📤 Procesar Documentos"
3. **Pregunta**: "¿Cuáles son los temas principales de estos documentos?"
4. **Explora**: Usa los botones de acción rápida

## 🔧 Solución de Problemas

### Error: "OpenAI API key not found"
- Verifica que el archivo `.env` existe
- Confirma que `OPENAI_API_KEY=tu_clave_real` esté configurado
- Reinicia la aplicación

### Error: "Import could not be resolved"
- Ejecuta: `venv_catchai\Scripts\pip install -r requirements.txt`
- Verifica que el entorno virtual esté activado

### Puerto ocupado
- Cambia el puerto: `streamlit run src/frontend/app.py --server.port 8502`

## 🎮 Casos de Uso Sugeridos

### 📊 Análisis de Reportes
- Sube reportes financieros/técnicos
- Pregunta: "Compara los resultados entre documentos"

### 📚 Investigación Académica
- Sube papers de investigación
- Pregunta: "¿Qué metodologías se utilizan?"

### 📋 Documentación Técnica
- Sube manuales y especificaciones
- Pregunta: "Extrae los requisitos principales"

## 🚀 ¡Listo para usar!

Tu copiloto conversacional está preparado para analizar documentos con IA de última generación.

**¿Preguntas?** Consulta el README.md completo para documentación detallada.
