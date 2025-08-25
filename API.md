# API Documentation

## Endpoints

### Document Management

#### POST /api/documents/upload
Upload documents for processing.

**Request:**
```json
{
  "files": ["file1.pdf", "file2.txt"],
  "session_id": "optional"
}
```

**Response:**
```json
{
  "success": true,
  "documents": [
    {
      "id": "doc-123",
      "filename": "file1.pdf",
      "size_bytes": 12345,
      "topics": ["AI", "Machine Learning"]
    }
  ]
}
```

#### GET /api/documents
List all uploaded documents.

#### DELETE /api/documents/{document_id}
Remove a specific document.

### Chat Interface

#### POST /api/chat
Send a message to the copilot.

**Request:**
```json
{
  "message": "What are the main topics?",
  "session_id": "session-123"
}
```

**Response:**
```json
{
  "response": "The main topics include...",
  "sources": ["doc1.pdf", "doc2.txt"],
  "confidence": 0.85,
  "processing_time": 1.2
}
```

### Analysis

#### GET /api/analysis/summary
Get document summaries.

#### GET /api/analysis/comparison
Compare documents.

#### GET /api/analysis/insights
Get AI-generated insights.

## Models

### Document
```json
{
  "id": "string",
  "filename": "string",
  "file_type": "pdf|txt|docx",
  "size_bytes": "integer",
  "uploaded_at": "datetime",
  "content": "string",
  "summary": "string",
  "topics": ["string"]
}
```

### Chat Message
```json
{
  "role": "user|assistant",
  "content": "string",
  "timestamp": "datetime",
  "sources": ["string"]
}
```

### Query Result
```json
{
  "answer": "string",
  "sources": ["DocumentChunk"],
  "confidence": "float",
  "processing_time": "float"
}
```
