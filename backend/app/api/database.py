"""
Database API endpoints for AI Study Partner
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time

from ..database.vector_db import VectorDB, Document
from ..services import service_manager

router = APIRouter()

class DocumentRequest(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}
    source_type: str = "manual"
    session_id: str = "default"

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    session_id: Optional[str] = None
    source_type: Optional[str] = None

class DatabaseResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

# Dependency to get vector database
async def get_vector_db() -> VectorDB:
    if not service_manager.vector_db:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    return service_manager.vector_db

@router.post("/documents", response_model=DatabaseResponse)
async def add_document(request: DocumentRequest, db: VectorDB = Depends(get_vector_db)):
    """Add a document to the vector database"""
    try:
        doc_id = await db.add_document(
            content=request.content,
            metadata=request.metadata,
            source_type=request.source_type,
            session_id=request.session_id
        )
        
        return DatabaseResponse(
            success=True,
            data={
                "document_id": doc_id,
                "content_length": len(request.content),
                "session_id": request.session_id
            }
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.post("/documents/chunks", response_model=DatabaseResponse)
async def add_text_chunks(request: DocumentRequest, db: VectorDB = Depends(get_vector_db)):
    """Add text as multiple chunks to the vector database"""
    try:
        doc_ids = await db.add_text_chunks(
            text=request.content,
            metadata=request.metadata,
            source_type=request.source_type,
            session_id=request.session_id
        )
        
        return DatabaseResponse(
            success=True,
            data={
                "document_ids": doc_ids,
                "chunk_count": len(doc_ids),
                "session_id": request.session_id
            }
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.post("/search", response_model=DatabaseResponse)
async def search_documents(request: SearchRequest, db: VectorDB = Depends(get_vector_db)):
    """Search for similar documents"""
    try:
        results = await db.search(
            query=request.query,
            top_k=request.top_k,
            session_id=request.session_id,
            source_type=request.source_type
        )
        
        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "document_id": result.document.id,
                "content": result.document.content,
                "score": result.score,
                "rank": result.rank,
                "metadata": result.document.metadata,
                "timestamp": result.document.timestamp,
                "source_type": result.document.source_type,
                "session_id": result.document.session_id
            })
        
        return DatabaseResponse(
            success=True,
            data={
                "results": formatted_results,
                "query": request.query,
                "total_results": len(formatted_results)
            }
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.get("/documents/{document_id}", response_model=DatabaseResponse)
async def get_document(document_id: str, db: VectorDB = Depends(get_vector_db)):
    """Get a specific document by ID"""
    try:
        document = await db.get_document(document_id)
        
        if not document:
            return DatabaseResponse(
                success=False,
                data={},
                error="Document not found"
            )
        
        return DatabaseResponse(
            success=True,
            data={
                "document_id": document.id,
                "content": document.content,
                "metadata": document.metadata,
                "timestamp": document.timestamp,
                "source_type": document.source_type,
                "session_id": document.session_id
            }
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.delete("/documents/{document_id}", response_model=DatabaseResponse)
async def delete_document(document_id: str, db: VectorDB = Depends(get_vector_db)):
    """Delete a document from the database"""
    try:
        success = await db.delete_document(document_id)
        
        if not success:
            return DatabaseResponse(
                success=False,
                data={},
                error="Document not found"
            )
        
        return DatabaseResponse(
            success=True,
            data={
                "document_id": document_id,
                "deleted": True
            }
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.get("/sessions/{session_id}/documents", response_model=DatabaseResponse)
async def get_session_documents(session_id: str, db: VectorDB = Depends(get_vector_db)):
    """Get all documents for a specific session"""
    try:
        documents = await db.get_session_documents(session_id)
        
        formatted_documents = []
        for doc in documents:
            formatted_documents.append({
                "document_id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata,
                "timestamp": doc.timestamp,
                "source_type": doc.source_type
            })
        
        return DatabaseResponse(
            success=True,
            data={
                "session_id": session_id,
                "documents": formatted_documents,
                "count": len(formatted_documents)
            }
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.delete("/sessions/{session_id}", response_model=DatabaseResponse)
async def clear_session(session_id: str, db: VectorDB = Depends(get_vector_db)):
    """Clear all documents for a specific session"""
    try:
        deleted_count = await db.clear_session(session_id)
        
        return DatabaseResponse(
            success=True,
            data={
                "session_id": session_id,
                "deleted_count": deleted_count
            }
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.get("/stats", response_model=DatabaseResponse)
async def get_database_stats(db: VectorDB = Depends(get_vector_db)):
    """Get database statistics"""
    try:
        stats = await db.get_stats()
        
        return DatabaseResponse(
            success=True,
            data=stats
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.get("/sessions", response_model=DatabaseResponse)
async def list_sessions(db: VectorDB = Depends(get_vector_db)):
    """List all sessions in the database"""
    try:
        stats = await db.get_stats()
        
        # Get unique sessions from documents
        sessions = set()
        for doc in db.documents:
            sessions.add(doc.session_id)
        
        return DatabaseResponse(
            success=True,
            data={
                "sessions": list(sessions),
                "total_sessions": len(sessions)
            }
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

@router.post("/export/session/{session_id}")
async def export_session(session_id: str, format: str = "json", db: VectorDB = Depends(get_vector_db)):
    """Export session data in various formats"""
    try:
        documents = await db.get_session_documents(session_id)
        
        if format == "json":
            export_data = {
                "session_id": session_id,
                "export_timestamp": time.time(),
                "documents": [
                    {
                        "id": doc.id,
                        "content": doc.content,
                        "metadata": doc.metadata,
                        "timestamp": doc.timestamp,
                        "source_type": doc.source_type
                    }
                    for doc in documents
                ]
            }
            
        elif format == "text":
            export_data = {
                "session_id": session_id,
                "export_timestamp": time.time(),
                "content": "\n\n".join([doc.content for doc in documents])
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
        
        return DatabaseResponse(
            success=True,
            data=export_data
        )
        
    except Exception as e:
        return DatabaseResponse(
            success=False,
            data={},
            error=str(e)
        )

