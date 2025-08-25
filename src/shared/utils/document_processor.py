"""
Document processing utilities for CatchAI Document Copilot
"""
import os
import uuid
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

import PyPDF2
import fitz  # pymupdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangChainDocument

from ..config.settings import config
from ..models import Document, DocumentType, DocumentChunk


class DocumentProcessor:
    """Process and extract content from various document types"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def process_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try with PyPDF2 first
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # If PyPDF2 fails to extract much text, try pymupdf
            if len(text.strip()) < 100:
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
            
            return text.strip()
        
        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    def process_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def create_document(self, file_path: str, filename: str) -> Document:
        """Create Document object from file"""
        file_ext = Path(filename).suffix.lower()
        
        # Determine document type
        if file_ext == '.pdf':
            doc_type = DocumentType.PDF
            content = self.process_pdf(file_path)
        elif file_ext == '.txt':
            doc_type = DocumentType.TXT
            content = self.process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Get file size
        size_bytes = os.path.getsize(file_path)
        
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        return Document(
            id=doc_id,
            filename=filename,
            file_type=doc_type,
            size_bytes=size_bytes,
            uploaded_at=datetime.now(),
            content=content
        )
    
    def create_chunks(self, document: Document) -> List[DocumentChunk]:
        """Split document into chunks for vector storage"""
        if not document.content:
            return []
        
        # Create LangChain document
        langchain_doc = LangChainDocument(
            page_content=document.content,
            metadata={
                "document_id": document.id,
                "filename": document.filename,
                "file_type": document.file_type.value
            }
        )
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([langchain_doc])
        
        # Convert to DocumentChunk objects
        doc_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document.id}_{i}"
            doc_chunk = DocumentChunk(
                id=chunk_id,
                document_id=document.id,
                content=chunk.page_content,
                metadata={
                    **chunk.metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )
            doc_chunks.append(doc_chunk)
        
        return doc_chunks
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text (simple implementation)"""
        # This is a simple keyword extraction
        # In production, you might want to use more sophisticated methods
        import re
        from collections import Counter
        
        # Remove special characters and convert to lowercase
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'this',
            'that', 'these', 'those', 'can', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'shall', 'have', 'has', 'had', 'been',
            'are', 'was', 'were', 'being', 'been'
        }
        
        # Count words and filter
        word_counts = Counter(word for word in words if word not in stop_words)
        
        return [word for word, _ in word_counts.most_common(max_keywords)]


class DocumentManager:
    """Manage document storage and retrieval"""
    
    def __init__(self):
        self.documents: List[Document] = []
        self.processor = DocumentProcessor()
    
    def add_document(self, file_path: str, filename: str) -> Document:
        """Add a new document"""
        if len(self.documents) >= config.MAX_FILES:
            raise ValueError(f"Maximum number of files ({config.MAX_FILES}) exceeded")
        
        document = self.processor.create_document(file_path, filename)
        document.topics = self.processor.extract_keywords(document.content)
        self.documents.append(document)
        
        return document
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID"""
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None
    
    def list_documents(self) -> List[Document]:
        """List all documents"""
        return self.documents.copy()
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove document by ID"""
        for i, doc in enumerate(self.documents):
            if doc.id == doc_id:
                del self.documents[i]
                return True
        return False
    
    def clear_documents(self):
        """Remove all documents"""
        self.documents.clear()
