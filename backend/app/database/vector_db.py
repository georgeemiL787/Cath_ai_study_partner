"""
Vector Database Module for AI Study Partner
Handles content indexing, embeddings, and retrieval
"""

import numpy as np
import faiss
import json
import os
import time
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import pickle
import hashlib

# Try to import sentence transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

@dataclass
class Document:
    """Document structure for vector database"""
    id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: float
    embedding: Optional[np.ndarray] = None
    source_type: str = "unknown"  # screen, audio, manual
    session_id: str = "default"

@dataclass
class SearchResult:
    """Search result from vector database"""
    document: Document
    score: float
    rank: int

class VectorDB:
    """Vector database for semantic search and retrieval"""
    
    def __init__(self, db_path: str = "./data/vector_db", embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.logger = logging.getLogger(__name__)
        
        # Initialize embedding model
        self.embedding_model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        # FAISS index
        self.index = None
        self.documents: List[Document] = []
        self.document_map: Dict[str, Document] = {}
        
        # Statistics
        self.total_documents = 0
        self.last_index_time = None
        
        # Create database directory
        os.makedirs(db_path, exist_ok=True)
        
    async def initialize(self):
        """Initialize the vector database"""
        try:
            # Load embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                self.logger.info(f"Embedding model loaded: {self.embedding_model_name}")
            else:
                raise RuntimeError("sentence-transformers not available")
                
            # Initialize FAISS index
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            
            # Load existing data
            await self._load_database()
            
            self.logger.info(f"Vector database initialized with {self.total_documents} documents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector database: {e}")
            raise
            
    def _generate_document_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique document ID"""
        # Create hash from content and metadata
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = str(int(time.time() * 1000))[-8:]  # Last 8 digits of timestamp
        return f"doc_{content_hash}_{timestamp}"
        
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
            
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
                        
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
                
            start = end - overlap
            
        return chunks
        
    async def add_document(self, content: str, metadata: Dict[str, Any], 
                          source_type: str = "unknown", session_id: str = "default") -> str:
        """Add document to vector database"""
        if not content.strip():
            return None
            
        # Generate document ID
        doc_id = self._generate_document_id(content, metadata)
        
        # Create document
        document = Document(
            id=doc_id,
            content=content,
            metadata=metadata,
            timestamp=time.time(),
            source_type=source_type,
            session_id=session_id
        )
        
        # Generate embedding
        embedding = self.embedding_model.encode(content)
        document.embedding = embedding
        
        # Add to FAISS index
        self.index.add(embedding.reshape(1, -1))
        
        # Store document
        self.documents.append(document)
        self.document_map[doc_id] = document
        self.total_documents += 1
        
        self.logger.debug(f"Added document {doc_id} to vector database")
        return doc_id
        
    async def add_text_chunks(self, text: str, metadata: Dict[str, Any], 
                             source_type: str = "unknown", session_id: str = "default") -> List[str]:
        """Add text as multiple chunks to vector database"""
        chunks = self._chunk_text(text)
        doc_ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_text": chunk[:100] + "..." if len(chunk) > 100 else chunk
            })
            
            doc_id = await self.add_document(chunk, chunk_metadata, source_type, session_id)
            if doc_id:
                doc_ids.append(doc_id)
                
        return doc_ids
        
    async def search(self, query: str, top_k: int = 5, 
                    session_id: Optional[str] = None,
                    source_type: Optional[str] = None) -> List[SearchResult]:
        """Search for similar documents"""
        if not query.strip():
            return []
            
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Search FAISS index
        scores, indices = self.index.search(query_embedding.reshape(1, -1), min(top_k, self.total_documents))
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:  # No more results
                break
                
            document = self.documents[idx]
            
            # Filter by session_id if specified
            if session_id and document.session_id != session_id:
                continue
                
            # Filter by source_type if specified
            if source_type and document.source_type != source_type:
                continue
                
            results.append(SearchResult(
                document=document,
                score=float(score),
                rank=i + 1
            ))
            
        return results
        
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID"""
        return self.document_map.get(doc_id)
        
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from database"""
        if doc_id not in self.document_map:
            return False
            
        document = self.document_map[doc_id]
        
        # Remove from FAISS index (this is complex, so we'll rebuild)
        await self._rebuild_index()
        
        # Remove from storage
        self.documents = [doc for doc in self.documents if doc.id != doc_id]
        del self.document_map[doc_id]
        self.total_documents -= 1
        
        self.logger.debug(f"Deleted document {doc_id}")
        return True
        
    async def get_session_documents(self, session_id: str) -> List[Document]:
        """Get all documents for a session"""
        return [doc for doc in self.documents if doc.session_id == session_id]
        
    async def clear_session(self, session_id: str) -> int:
        """Clear all documents for a session"""
        session_docs = [doc for doc in self.documents if doc.session_id == session_id]
        
        for doc in session_docs:
            del self.document_map[doc.id]
            
        self.documents = [doc for doc in self.documents if doc.session_id != session_id]
        self.total_documents = len(self.documents)
        
        # Rebuild index
        await self._rebuild_index()
        
        self.logger.info(f"Cleared {len(session_docs)} documents for session {session_id}")
        return len(session_docs)
        
    async def _rebuild_index(self):
        """Rebuild FAISS index from current documents"""
        if not self.documents:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            return
            
        # Create new index
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        # Add all embeddings
        embeddings = np.array([doc.embedding for doc in self.documents])
        self.index.add(embeddings)
        
    async def _load_database(self):
        """Load existing database from disk"""
        try:
            # Load documents
            docs_file = os.path.join(self.db_path, "documents.pkl")
            if os.path.exists(docs_file):
                with open(docs_file, 'rb') as f:
                    self.documents = pickle.load(f)
                    
                # Rebuild document map
                self.document_map = {doc.id: doc for doc in self.documents}
                self.total_documents = len(self.documents)
                
                # Rebuild FAISS index
                if self.documents:
                    await self._rebuild_index()
                    
                self.logger.info(f"Loaded {self.total_documents} documents from disk")
                
        except Exception as e:
            self.logger.warning(f"Failed to load existing database: {e}")
            
    async def _save_database(self):
        """Save database to disk"""
        try:
            # Save documents
            docs_file = os.path.join(self.db_path, "documents.pkl")
            with open(docs_file, 'wb') as f:
                pickle.dump(self.documents, f)
                
            # Save metadata
            metadata = {
                "total_documents": self.total_documents,
                "last_save": time.time(),
                "embedding_model": self.embedding_model_name,
                "embedding_dim": self.embedding_dim
            }
            
            metadata_file = os.path.join(self.db_path, "metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            self.last_index_time = time.time()
            
        except Exception as e:
            self.logger.error(f"Failed to save database: {e}")
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "total_documents": self.total_documents,
            "embedding_model": self.embedding_model_name,
            "embedding_dim": self.embedding_dim,
            "last_index_time": self.last_index_time,
            "sessions": len(set(doc.session_id for doc in self.documents)),
            "source_types": list(set(doc.source_type for doc in self.documents))
        }
        
    async def close(self):
        """Close database and save data"""
        await self._save_database()
        self.logger.info("Vector database closed and saved")

