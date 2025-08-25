"""
LLM conversation engine for document Q&A
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from ..config.settings import config
from ..models import ChatMessage, Document, QueryResult
from .vector_store import SemanticSearchEngine


class ConversationEngine:
    """Manage conversations with LLM using document context"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            model_name=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )
        
        self.search_engine = SemanticSearchEngine()
        self.conversation_history: List[ChatMessage] = []
        self.documents: List[Document] = []
        
        # System prompt template
        self.system_prompt = """Eres un asistente de IA especializado en análisis de documentos llamado CatchAI Document Copilot. 

Tu objetivo es ayudar a los usuarios a entender, analizar y extraer información de los documentos que han subido.

INSTRUCCIONES:
1. Responde SIEMPRE en español de manera clara y estructurada
2. Basa tus respuestas únicamente en la información contenida en los documentos proporcionados
3. Si no encuentras información relevante en los documentos, indícalo claramente
4. Proporciona citas específicas cuando sea posible (nombre del documento, sección, etc.)
5. Si te piden comparar documentos, hazlo de manera organizada y clara
6. Para resúmenes, incluye los puntos más importantes de manera jerárquica
7. Si detectas información contradictoria entre documentos, menciona esta discrepancia

CAPACIDADES ESPECIALES:
- Análisis de contenido y extracción de información clave
- Comparación entre múltiples documentos
- Generación de resúmenes estructurados
- Identificación de temas y patrones
- Respuesta a preguntas específicas sobre el contenido

Mantén un tono profesional pero amigable. Si no estás seguro de algo, admítelo abiertamente."""

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the conversation context"""
        self.documents = documents
        
        # Index documents for search
        from .document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        for doc in documents:
            chunks = processor.create_chunks(doc)
            self.search_engine.index_chunks(chunks)
    
    def add_message(self, role: str, content: str, sources: List[str] = None) -> None:
        """Add a message to conversation history"""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            sources=sources or []
        )
        self.conversation_history.append(message)
    
    def get_relevant_context(self, query: str, max_chunks: int = 5) -> tuple[str, List[str]]:
        """Get relevant context from documents"""
        search_result = self.search_engine.search_documents(query, max_results=max_chunks)
        
        # Extract source information
        sources = []
        for chunk in search_result.sources:
            doc_name = chunk.metadata.get("filename", "Unknown Document")
            chunk_idx = chunk.metadata.get("chunk_index", 0)
            sources.append(f"{doc_name} (Sección {chunk_idx + 1})")
        
        return search_result.answer, sources
    
    def generate_response(self, user_query: str) -> tuple[str, List[str]]:
        """Generate response to user query using document context"""
        # Get relevant context from documents
        context, sources = self.get_relevant_context(user_query)
        
        # Prepare conversation context
        recent_history = self.conversation_history[-6:]  # Last 3 exchanges
        
        # Build messages for LLM
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add conversation history
        for msg in recent_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
        
        # Prepare the current query with context
        if context and context != "No relevant context found in the documents.":
            query_with_context = f"""
CONTEXTO RELEVANTE DE LOS DOCUMENTOS:
{context}

PREGUNTA DEL USUARIO:
{user_query}

Por favor, responde a la pregunta basándote en la información del contexto proporcionado."""
        else:
            query_with_context = f"""
No se encontró contexto relevante en los documentos cargados para responder a esta pregunta.

PREGUNTA DEL USUARIO:
{user_query}

Por favor, indica que no hay información suficiente en los documentos para responder esta pregunta."""
        
        messages.append(HumanMessage(content=query_with_context))
        
        # Generate response
        try:
            response = self.llm(messages)
            return response.content, sources
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}", []
    
    def chat(self, user_message: str) -> tuple[str, List[str]]:
        """Main chat interface"""
        # Add user message to history
        self.add_message("user", user_message)
        
        # Generate response
        response, sources = self.generate_response(user_message)
        
        # Add assistant response to history
        self.add_message("assistant", response, sources)
        
        return response, sources
    
    def generate_document_summary(self, document_id: Optional[str] = None) -> str:
        """Generate summary of documents"""
        if document_id:
            # Summary for specific document
            doc = next((d for d in self.documents if d.id == document_id), None)
            if not doc:
                return "Documento no encontrado."
            
            query = f"Resume el contenido del documento {doc.filename}"
            summary, _ = self.generate_response(query)
            return summary
        else:
            # Summary for all documents
            doc_names = [doc.filename for doc in self.documents]
            query = f"Genera un resumen ejecutivo de todos los documentos cargados: {', '.join(doc_names)}"
            summary, _ = self.generate_response(query)
            return summary
    
    def compare_documents(self, doc_ids: List[str]) -> str:
        """Compare multiple documents"""
        if len(doc_ids) < 2:
            return "Se necesitan al menos 2 documentos para comparar."
        
        doc_names = []
        for doc_id in doc_ids:
            doc = next((d for d in self.documents if d.id == doc_id), None)
            if doc:
                doc_names.append(doc.filename)
        
        if len(doc_names) < 2:
            return "No se encontraron suficientes documentos válidos para comparar."
        
        query = f"Compara los siguientes documentos e identifica similitudes y diferencias clave: {', '.join(doc_names)}"
        comparison, _ = self.generate_response(query)
        return comparison
    
    def extract_topics(self) -> str:
        """Extract main topics from all documents"""
        query = "Identifica y lista los temas principales tratados en todos los documentos cargados, organizándolos por relevancia."
        topics, _ = self.generate_response(query)
        return topics
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history.clear()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m.role == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m.role == "assistant"]),
            "documents_loaded": len(self.documents),
            "document_names": [doc.filename for doc in self.documents]
        }


class PromptTemplates:
    """Collection of specialized prompt templates"""
    
    @staticmethod
    def get_analysis_prompt() -> str:
        """Get prompt for document analysis"""
        return """Analiza el siguiente documento y proporciona:
1. Resumen ejecutivo (3-5 puntos clave)
2. Temas principales identificados
3. Información relevante destacada
4. Conclusiones o recomendaciones (si aplica)

Documento: {document_content}"""
    
    @staticmethod
    def get_comparison_prompt() -> str:
        """Get prompt for document comparison"""
        return """Compara los siguientes documentos y proporciona:
1. Similitudes principales
2. Diferencias clave
3. Análisis de perspectivas distintas
4. Síntesis de información complementaria

Documentos: {documents_content}"""
    
    @staticmethod
    def get_extraction_prompt() -> str:
        """Get prompt for information extraction"""
        return """Extrae la siguiente información específica del documento:
{extraction_criteria}

Si no encuentras alguna información, indícalo claramente.

Documento: {document_content}"""
