"""
Vector store utilities for semantic search
"""
import os
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document as LangChainDocument

from ..config.settings import config
from ..models import DocumentChunk, QueryResult


class VectorStore:
    """Vector store for document embeddings and semantic search"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config.OPENAI_API_KEY,
            model=config.EMBEDDING_MODEL
        )
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection_name = "document_chunks"
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except:
            self.collection = self.client.create_collection(self.collection_name)
        
        # Initialize LangChain vector store
        self.vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Add document chunks to vector store"""
        if not chunks:
            return
        
        # Prepare documents for LangChain
        documents = []
        for chunk in chunks:
            doc = LangChainDocument(
                page_content=chunk.content,
                metadata={
                    **chunk.metadata,
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id
                }
            )
            documents.append(doc)
        
        # Add to vector store
        self.vector_store.add_documents(documents)
    
    def search(self, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Tuple[LangChainDocument, float]]:
        """Search for similar chunks"""
        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        return results
    
    def search_by_document(self, query: str, document_id: str, k: int = 3) -> List[Tuple[LangChainDocument, float]]:
        """Search within a specific document"""
        filter_dict = {"document_id": document_id}
        return self.search(query, k=k, filter_dict=filter_dict)
    
    def get_relevant_context(self, query: str, max_chunks: int = 5, min_score: float = 0.7) -> str:
        """Get relevant context for a query"""
        results = self.search(query, k=max_chunks)
        
        # Filter by minimum score and prepare context
        relevant_chunks = []
        for doc, score in results:
            # ChromaDB returns distance (lower is better), so we convert to similarity
            similarity = 1 - score
            if similarity >= min_score:
                relevant_chunks.append(doc.page_content)
        
        if not relevant_chunks:
            return "No relevant context found in the documents."
        
        # Combine chunks with separators
        context = "\n\n--- Document Section ---\n\n".join(relevant_chunks)
        return context
    
    def remove_document(self, document_id: str) -> None:
        """Remove all chunks for a specific document"""
        # Get all chunk IDs for the document
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if results and results['ids']:
            # Delete chunks
            self.collection.delete(ids=results['ids'])
    
    def clear_all(self) -> None:
        """Clear all vectors from the store"""
        # Delete the collection and recreate it
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        self.collection = self.client.create_collection(self.collection_name)
        self.vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection_name,
                "embedding_model": config.EMBEDDING_MODEL
            }
        except:
            return {
                "total_chunks": 0,
                "collection_name": self.collection_name,
                "embedding_model": config.EMBEDDING_MODEL
            }


class SemanticSearchEngine:
    """High-level semantic search interface"""
    
    def __init__(self):
        self.vector_store = VectorStore()
    
    def index_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Index document chunks for search"""
        self.vector_store.add_chunks(chunks)
    
    def search_documents(self, query: str, document_ids: Optional[List[str]] = None, max_results: int = 5) -> QueryResult:
        """Search across documents with advanced filtering"""
        import time
        start_time = time.time()
        
        # Prepare filter if document IDs specified
        filter_dict = None
        if document_ids:
            filter_dict = {"document_id": {"$in": document_ids}}
        
        # Perform search
        results = self.vector_store.search(query, k=max_results, filter_dict=filter_dict)
        
        # Convert results to DocumentChunk objects
        source_chunks = []
        for doc, score in results:
            chunk = DocumentChunk(
                id=doc.metadata.get("chunk_id", ""),
                document_id=doc.metadata.get("document_id", ""),
                content=doc.page_content,
                metadata=doc.metadata
            )
            source_chunks.append(chunk)
        
        # Calculate confidence (average similarity)
        if results:
            avg_distance = sum(score for _, score in results) / len(results)
            confidence = max(0, 1 - avg_distance)  # Convert distance to similarity
        else:
            confidence = 0.0
        
        # Prepare answer (combine relevant chunks)
        answer = self.vector_store.get_relevant_context(query, max_chunks=max_results)
        
        processing_time = time.time() - start_time
        
        return QueryResult(
            answer=answer,
            sources=source_chunks,
            confidence=confidence,
            processing_time=processing_time
        )
    
    def remove_document_index(self, document_id: str) -> None:
        """Remove document from search index"""
        self.vector_store.remove_document(document_id)
    
    def clear_index(self) -> None:
        """Clear the entire search index"""
        self.vector_store.clear_all()
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get search index statistics"""
        return self.vector_store.get_stats()
