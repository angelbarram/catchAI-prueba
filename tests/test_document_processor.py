"""
Tests for document processing functionality
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from shared.models import Document, DocumentType
from shared.utils.document_processor import DocumentProcessor, DocumentManager


class TestDocumentProcessor:
    """Test document processing functionality"""
    
    def test_process_txt(self, temp_dir, sample_text):
        """Test TXT file processing"""
        processor = DocumentProcessor()
        
        # Create test file
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        # Process file
        content = processor.process_txt(txt_path)
        
        assert content == sample_text
        assert "CatchAI" in content
        assert "inteligencia artificial" in content
    
    def test_create_document(self, temp_dir, sample_text):
        """Test document creation"""
        processor = DocumentProcessor()
        
        # Create test file
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        # Create document
        document = processor.create_document(txt_path, "test.txt")
        
        assert isinstance(document, Document)
        assert document.filename == "test.txt"
        assert document.file_type == DocumentType.TXT
        assert document.content == sample_text
        assert document.size_bytes > 0
    
    def test_create_chunks(self, temp_dir, sample_text):
        """Test document chunking"""
        processor = DocumentProcessor()
        
        # Create test document
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(sample_text * 10)  # Make it longer to ensure chunking
        
        document = processor.create_document(txt_path, "test.txt")
        chunks = processor.create_chunks(document)
        
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.document_id == document.id
            assert len(chunk.content) > 0
            assert "chunk_index" in chunk.metadata
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        processor = DocumentProcessor()
        
        text = """
        Inteligencia artificial machine learning deep learning
        procesamiento de lenguaje natural análisis de datos
        """
        
        keywords = processor.extract_keywords(text, max_keywords=5)
        
        assert len(keywords) <= 5
        assert "inteligencia" in keywords or "artificial" in keywords


class TestDocumentManager:
    """Test document management functionality"""
    
    def test_add_document(self, temp_dir, sample_text):
        """Test adding documents"""
        manager = DocumentManager()
        
        # Create test file
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        # Add document
        document = manager.add_document(txt_path, "test.txt")
        
        assert len(manager.documents) == 1
        assert document in manager.documents
        assert document.topics is not None
    
    def test_max_files_limit(self, temp_dir, sample_text):
        """Test maximum files limit"""
        manager = DocumentManager()
        
        # Mock the config to have a low limit
        with patch('shared.utils.document_processor.config.MAX_FILES', 2):
            # Add files up to limit
            for i in range(2):
                txt_path = os.path.join(temp_dir, f"test{i}.txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(sample_text)
                manager.add_document(txt_path, f"test{i}.txt")
            
            # Try to add one more (should fail)
            txt_path = os.path.join(temp_dir, "test_extra.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(sample_text)
            
            with pytest.raises(ValueError):
                manager.add_document(txt_path, "test_extra.txt")
    
    def test_remove_document(self, temp_dir, sample_text):
        """Test removing documents"""
        manager = DocumentManager()
        
        # Add document
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        document = manager.add_document(txt_path, "test.txt")
        doc_id = document.id
        
        # Remove document
        removed = manager.remove_document(doc_id)
        
        assert removed is True
        assert len(manager.documents) == 0
        assert manager.get_document(doc_id) is None
    
    def test_clear_documents(self, temp_dir, sample_text):
        """Test clearing all documents"""
        manager = DocumentManager()
        
        # Add multiple documents
        for i in range(3):
            txt_path = os.path.join(temp_dir, f"test{i}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(sample_text)
            manager.add_document(txt_path, f"test{i}.txt")
        
        assert len(manager.documents) == 3
        
        # Clear all
        manager.clear_documents()
        
        assert len(manager.documents) == 0
