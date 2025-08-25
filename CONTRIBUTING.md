# Contributing to CatchAI Document Copilot

## Desarrollo

### Configuración del entorno de desarrollo

1. Clona el repositorio
2. Ejecuta `python setup.py` para configurar el entorno
3. Activa el entorno virtual
4. Ejecuta tests: `pytest`

### Estructura del código

- `src/shared/config/` - Configuración de la aplicación
- `src/shared/models/` - Modelos de datos
- `src/shared/utils/` - Utilidades y lógica de negocio
- `src/frontend/` - Interfaz de usuario con Streamlit
- `tests/` - Tests unitarios e integración

### Estándares de código

- Python 3.8+
- Seguir PEP 8
- Documentar funciones con docstrings
- Tests para nueva funcionalidad

### Flujo de desarrollo

1. Crear branch para nueva feature
2. Implementar funcionalidad
3. Escribir tests
4. Ejecutar tests y linting
5. Crear pull request

## Roadmap de mejoras

### Próximas funcionalidades

1. **Procesamiento de más formatos**
   - DOCX support
   - OCR para imágenes
   - Tablas y gráficos

2. **Mejores algoritmos de búsqueda**
   - Híbrida semántica + keyword
   - Re-ranking de resultados
   - Filtros avanzados

3. **Colaboración multi-usuario**
   - Sesiones compartidas
   - Comentarios en documentos
   - Historial de cambios

4. **Integración con APIs externas**
   - Múltiples LLM providers
   - Bases de datos empresariales
   - Sistemas de gestión documental

5. **Analytics avanzado**
   - Métricas de uso
   - Patrones de consulta
   - Optimización automática
