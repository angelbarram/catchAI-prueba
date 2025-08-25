"""
Data models for CatchAI Document Copilot
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(Enum):
    """Supported document types"""
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"

@dataclass
class Document:
    """Document metadata model"""
    id: str
    filename: str
    file_type: DocumentType
    size_bytes: int
    uploaded_at: datetime
    content: Optional[str] = None
    summary: Optional[str] = None
    topics: List[str] = None
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = []

@dataclass
class DocumentChunk:
    """Document chunk model for vector storage"""
    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

@dataclass
class ChatMessage:
    """Chat message model"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    sources: List[str] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []

@dataclass
class QueryResult:
    """Query result model"""
    answer: str
    sources: List[DocumentChunk]
    confidence: float
    processing_time: float

@dataclass
class ConversationContext:
    """Conversation context model"""
    session_id: str
    messages: List[ChatMessage]
    documents: List[Document]
    created_at: datetime
    updated_at: datetime
