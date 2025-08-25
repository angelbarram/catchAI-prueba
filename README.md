# CatchAI - Copiloto Conversacional sobre Documentos

## Descripción del Proyecto

Copiloto conversacional que permite subir hasta 5 archivos PDF y hacer preguntas en lenguaje natural sobre su contenido. Utiliza RAG (Retrieval Augmented Generation) con orquestación clara y extensible.

## Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   Vector Store  │
│   (Streamlit)   │◄──►│   (FastAPI)      │◄──►│    (Chroma)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   LLM Provider   │
                       │   (OpenAI GPT)   │
                       └──────────────────┘
```

### Componentes principales:

1. **Procesamiento de Documentos**: Extracción, chunking y vectorización de PDFs
2. **Vector Store**: Almacenamiento de embeddings para búsqueda semántica
3. **Motor de Conversación**: Orquestación de prompts y manejo del contexto
4. **Interfaz de Usuario**: Frontend interactivo con Streamlit
5. **API Backend**: FastAPI para endpoints RESTful

## Stack Tecnológico

- **Orquestación**: LangChain para RAG y chain management
- **LLM**: OpenAI GPT-4o-mini (cost-effective y potente)
- **Vector Store**: ChromaDB (fácil setup, persistent)
- **PDF Processing**: PyPDF2 + LangChain document loaders
- **Embeddings**: OpenAI text-embedding-3-small
- **Frontend**: Streamlit (rápido desarrollo, UX intuitiva)
- **Backend**: FastAPI (opcional, para arquitectura modular)
- **Containerización**: Docker + docker-compose

## Instrucciones de Instalación

### Opción 1: Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <repository-url>
cd catchai_prueba_tecnica

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# Levantar el entorno
docker-compose up -d

# Acceder a la aplicación
# Frontend: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

### Opción 2: Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# Ejecutar la aplicación
streamlit run src/frontend/app.py
```

## Flujo Conversacional

### 1. Carga de Documentos
- Usuario sube hasta 5 PDFs
- Extracción de texto con PyPDF2
- Chunking inteligente (1000 tokens, overlap 200)
- Generación de embeddings
- Almacenamiento en ChromaDB

### 2. Procesamiento de Consultas
```
Consulta Usuario → Embedding → Búsqueda Semántica → Contexto Relevante → LLM → Respuesta
```

### 3. Orquestación de Prompts
- **System Prompt**: Define el rol del asistente
- **Context Prompt**: Inyecta documentos relevantes
- **User Prompt**: Pregunta del usuario
- **Memory**: Mantiene historial conversacional

## Funcionalidades Implementadas

### Requisitos Mínimos
- [x] Subida de hasta 5 PDFs
- [x] Extracción y vectorización de contenido
- [x] Interfaz conversacional
- [x] Orquestación estructurada y extensible

### Funcionalidades Adicionales
- [x] Resumen automático de documentos
- [x] Comparaciones entre documentos
- [x] Clasificación por temas
- [x] Historial de conversación
- [x] Métricas de relevancia
- [x] Interfaz responsive

## Configuración

### Variables de Entorno (.env)
```
OPENAI_API_KEY=tu_api_key_aqui
CHROMA_PERSIST_DIR=./data/chroma_db
MAX_FILES=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Estructura del Proyecto

```
catchai_prueba_tecnica/
├── src/
│   ├── backend/
│   │   ├── api/
│   │   ├── core/
│   │   └── services/
│   ├── frontend/
│   │   └── app.py
│   └── shared/
│       ├── config/
│       ├── models/
│       └── utils/
├── data/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Casos de Uso

1. **Análisis de Documentos**: "Resume los puntos principales de todos los documentos"
2. **Búsqueda Específica**: "¿Qué dice sobre inteligencia artificial?"
3. **Comparaciones**: "¿Cuáles son las diferencias entre el documento 1 y 3?"
4. **Extracción de Datos**: "Lista todas las fechas mencionadas"

## Limitaciones Actuales

- Máximo 5 PDFs por sesión
- Solo texto (no imágenes ni tablas complejas)
- Contexto limitado por window del LLM
- Dependencia de OpenAI API

## Roadmap de Mejoras

### Corto Plazo
- [ ] Soporte para más formatos (DOCX, TXT)
- [ ] Procesamiento de imágenes y tablas (OCR)
- [ ] Cache de embeddings para optimización

### Mediano Plazo
- [ ] Múltiples LLM providers (Claude, Llama)
- [ ] Búsqueda híbrida (semántica + keyword)
- [ ] Exportación de conversaciones

### Largo Plazo
- [ ] Colaboración multi-usuario
- [ ] Integración con APIs externas
- [ ] Fine-tuning de modelos específicos

## Testing

```bash
# Ejecutar tests
python -m pytest tests/ -v

# Coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

## Métricas y Monitoreo

- Tiempo de respuesta de consultas
- Precisión de búsqueda semántica
- Uso de tokens y costos
- Satisfacción del usuario

---

**Desarrollado por**: [Tu Nombre]  
**Para**: CatchAI Technical Challenge  
**Fecha**: Agosto 2025
