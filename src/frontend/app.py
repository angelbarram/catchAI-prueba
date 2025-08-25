"""
CatchAI Document Copilot - Streamlit Frontend
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional
import streamlit as st
from datetime import datetime

# Add src to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from shared.config import config
    from shared.models import Document, ChatMessage
    from shared.utils import DocumentManager, ConversationEngine
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="CatchAI Document Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.chat-message {
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
}

.user-message {
    background-color: #f0f2f6;
    border-left-color: #667eea;
}

.assistant-message {
    background-color: #e8f4f8;
    border-left-color: #764ba2;
}

.document-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e1e1e1;
    margin-bottom: 0.5rem;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'document_manager' not in st.session_state:
        st.session_state.document_manager = DocumentManager()
    
    if 'conversation_engine' not in st.session_state:
        st.session_state.conversation_engine = ConversationEngine()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'documents_processed' not in st.session_state:
        st.session_state.documents_processed = False

# Validation functions
def validate_api_key():
    """Validate OpenAI API key"""
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        st.error("⚠️ Por favor configura tu OPENAI_API_KEY en el archivo .env")
        st.info("1. Copia .env.example a .env\n2. Añade tu API key de OpenAI\n3. Reinicia la aplicación")
        return False
    return True

def validate_file(uploaded_file) -> bool:
    """Validate uploaded file"""
    if uploaded_file is None:
        return False
    
    # Check file extension
    file_ext = Path(uploaded_file.name).suffix.lower()
    if file_ext not in ['.pdf', '.txt']:
        st.error(f"Tipo de archivo no soportado: {file_ext}. Solo se permiten PDF y TXT.")
        return False
    
    # Check file size (10MB limit)
    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("El archivo es demasiado grande. Máximo 10MB permitido.")
        return False
    
    return True

# Main interface functions
def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 CatchAI Document Copilot</h1>
        <p>Copiloto conversacional para análisis inteligente de documentos</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with document management"""
    with st.sidebar:
        st.header("📁 Gestión de Documentos")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Sube tus documentos (máx. 5)",
            type=['pdf', 'txt'],
            accept_multiple_files=True,
            help="Sube hasta 5 archivos PDF o TXT para análisis"
        )
        
        # Process uploaded files
        if uploaded_files and st.button("📤 Procesar Documentos", type="primary"):
            process_uploaded_files(uploaded_files)
        
        # Display current documents
        st.subheader("📋 Documentos Cargados")
        documents = st.session_state.document_manager.list_documents()
        
        if documents:
            for i, doc in enumerate(documents):
                with st.expander(f"📄 {doc.filename}"):
                    st.write(f"**Tipo:** {doc.file_type.value.upper()}")
                    st.write(f"**Tamaño:** {doc.size_bytes / 1024:.1f} KB")
                    st.write(f"**Subido:** {doc.uploaded_at.strftime('%H:%M:%S')}")
                    
                    if doc.topics:
                        st.write("**Temas identificados:**")
                        for topic in doc.topics[:5]:
                            st.write(f"• {topic}")
                    
                    if st.button(f"🗑️ Eliminar", key=f"delete_{doc.id}"):
                        remove_document(doc.id)
        else:
            st.info("No hay documentos cargados")
        
        # Clear all documents
        if documents and st.button("🗑️ Limpiar Todo", type="secondary"):
            clear_all_documents()
        
        # Statistics
        st.subheader("📊 Estadísticas")
        if documents:
            total_size = sum(doc.size_bytes for doc in documents)
            st.metric("Documentos", len(documents))
            st.metric("Tamaño Total", f"{total_size / 1024:.1f} KB")
            
            # Conversation stats
            conv_stats = st.session_state.conversation_engine.get_conversation_summary()
            st.metric("Mensajes", conv_stats['total_messages'])

def process_uploaded_files(uploaded_files):
    """Process uploaded files"""
    if len(uploaded_files) > config.MAX_FILES:
        st.error(f"Máximo {config.MAX_FILES} archivos permitidos")
        return
    
    # Clear existing documents
    st.session_state.document_manager.clear_documents()
    st.session_state.conversation_engine.clear_conversation()
    
    with st.spinner("Procesando documentos..."):
        documents = []
        
        for uploaded_file in uploaded_files:
            if not validate_file(uploaded_file):
                continue
            
            try:
                # Save file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_path = tmp_file.name
                
                # Process document
                document = st.session_state.document_manager.add_document(tmp_path, uploaded_file.name)
                documents.append(document)
                
                # Clean up temp file
                os.unlink(tmp_path)
                
            except Exception as e:
                st.error(f"Error procesando {uploaded_file.name}: {str(e)}")
        
        if documents:
            # Add documents to conversation engine
            st.session_state.conversation_engine.add_documents(documents)
            st.session_state.documents_processed = True
            
            st.success(f"✅ {len(documents)} documento(s) procesado(s) exitosamente")
            st.rerun()

def remove_document(doc_id: str):
    """Remove a specific document"""
    if st.session_state.document_manager.remove_document(doc_id):
        # Update conversation engine
        remaining_docs = st.session_state.document_manager.list_documents()
        st.session_state.conversation_engine.clear_conversation()
        if remaining_docs:
            st.session_state.conversation_engine.add_documents(remaining_docs)
        else:
            st.session_state.documents_processed = False
        
        st.success("Documento eliminado")
        st.rerun()

def clear_all_documents():
    """Clear all documents"""
    st.session_state.document_manager.clear_documents()
    st.session_state.conversation_engine.clear_conversation()
    st.session_state.documents_processed = False
    st.session_state.chat_history = []
    st.success("Todos los documentos eliminados")
    st.rerun()

def render_chat_interface():
    """Render main chat interface"""
    st.header("💬 Chat con tus Documentos")
    
    if not st.session_state.documents_processed:
        st.info("📄 Sube algunos documentos para comenzar a chatear")
        return
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Resumen General"):
            process_quick_action("Genera un resumen ejecutivo de todos los documentos cargados")
    
    with col2:
        if st.button("🔍 Temas Principales"):
            process_quick_action("Identifica y lista los temas principales de todos los documentos")
    
    with col3:
        if st.button("⚖️ Comparar Documentos"):
            process_quick_action("Compara los documentos y encuentra similitudes y diferencias clave")
    
    with col4:
        if st.button("📊 Análisis Detallado"):
            process_quick_action("Realiza un análisis detallado de todos los documentos, incluyendo conclusiones y recomendaciones")
    
    # Chat history
    st.subheader("Historial de Conversación")
    
    # Display chat messages
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 Tú:</strong><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            sources_text = ""
            if message.get('sources'):
                sources_text = f"<br><small><strong>Fuentes:</strong> {', '.join(message['sources'])}</small>"
            
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 CatchAI:</strong><br>
                {message['content']}{sources_text}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Pregunta algo sobre tus documentos...")
    
    if user_input:
        process_user_message(user_input)

def process_quick_action(action_prompt: str):
    """Process quick action button"""
    process_user_message(action_prompt)

def process_user_message(user_message: str):
    """Process user message and generate response"""
    # Add user message to history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_message
    })
    
    with st.spinner("Generando respuesta..."):
        try:
            # Generate response using conversation engine
            response, sources = st.session_state.conversation_engine.chat(user_message)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'sources': sources
            })
            
        except Exception as e:
            st.error(f"Error generando respuesta: {str(e)}")
    
    st.rerun()

def render_analytics():
    """Render analytics and insights"""
    st.header("📈 Análisis y Métricas")
    
    documents = st.session_state.document_manager.list_documents()
    
    if not documents:
        st.info("No hay documentos para analizar")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Documentos</h3>
            <h2>{}</h2>
        </div>
        """.format(len(documents)), unsafe_allow_html=True)
    
    with col2:
        total_words = sum(len(doc.content.split()) if doc.content else 0 for doc in documents)
        st.markdown("""
        <div class="metric-card">
            <h3>Palabras Totales</h3>
            <h2>{:,}</h2>
        </div>
        """.format(total_words), unsafe_allow_html=True)
    
    with col3:
        chat_messages = len(st.session_state.chat_history)
        st.markdown("""
        <div class="metric-card">
            <h3>Mensajes</h3>
            <h2>{}</h2>
        </div>
        """.format(chat_messages), unsafe_allow_html=True)
    
    # Topics analysis
    st.subheader("🏷️ Análisis de Temas")
    
    all_topics = []
    for doc in documents:
        if doc.topics:
            all_topics.extend(doc.topics)
    
    if all_topics:
        from collections import Counter
        topic_counts = Counter(all_topics)
        
        # Display top topics
        st.write("**Temas más frecuentes:**")
        for topic, count in topic_counts.most_common(10):
            st.write(f"• {topic} ({count} documento(s))")

def main():
    """Main application"""
    # Initialize
    initialize_session_state()
    
    # Validate API key
    if not validate_api_key():
        return
    
    # Render interface
    render_header()
    render_sidebar()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["💬 Chat", "📈 Análisis"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_analytics()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🤖 CatchAI Document Copilot | Desarrollado para el desafío técnico de CatchAI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
