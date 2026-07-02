"""
Simple Content Processor for AI Study Partner
A lightweight version that stores content in memory without heavy dependencies
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import json
import os

@dataclass
class SimpleDocument:
    """Simple document structure"""
    id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: float
    source_type: str
    session_id: str

class SimpleContentProcessor:
    """Simple content processor that stores content in memory and files"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        
        # In-memory storage
        self.documents: List[SimpleDocument] = []
        
        # File storage path
        self.storage_path = f"./data/sessions/{session_id}"
        os.makedirs(self.storage_path, exist_ok=True)
        
    async def start_processing(self):
        """Start the content processing"""
        self.is_processing = True
        self.logger.info(f"Simple content processing started for session {self.session_id}")
        
    async def stop_processing(self):
        """Stop the content processing"""
        self.is_processing = False
        # Save documents to file
        await self._save_documents()
        self.logger.info(f"Simple content processing stopped for session {self.session_id}")
        
    async def add_content(self, content: str, content_type: str = "manual", metadata: Dict[str, Any] = None):
        """Add content to the session"""
        if not content.strip():
            return
            
        timestamp = time.time()
        doc_id = f"{content_type}_{timestamp}_{hash(content) % 10000}"
        
        document = SimpleDocument(
            id=doc_id,
            content=content,
            metadata=metadata or {"type": content_type},
            timestamp=timestamp,
            source_type=content_type,
            session_id=self.session_id
        )
        
        self.documents.append(document)
        self.logger.info(f"Added content: {len(content)} characters")
        
    async def search_content(self, query: str, top_k: int = 5) -> List[SimpleDocument]:
        """Simple text search in stored content"""
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents:
            content_lower = doc.content.lower()
            # Simple scoring based on word matches
            score = 0
            query_words = query_lower.split()
            content_words = content_lower.split()
            
            for word in query_words:
                if word in content_words:
                    score += 1
                    
            if score > 0:
                scored_docs.append((score, doc))
                
        # Sort by score and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]
        
    async def get_session_content(self) -> List[SimpleDocument]:
        """Get all content for this session"""
        return self.documents.copy()
        
    async def _save_documents(self):
        """Save documents to file"""
        try:
            file_path = os.path.join(self.storage_path, "documents.json")
            data = []
            for doc in self.documents:
                data.append({
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "timestamp": doc.timestamp,
                    "source_type": doc.source_type,
                    "session_id": doc.session_id
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving documents: {e}")

# Global simple processors for active sessions
simple_processors: Dict[str, SimpleContentProcessor] = {}

async def start_simple_session_processing(session_id: str):
    """Start simple content processing for a session"""
    if session_id in simple_processors:
        return
        
    processor = SimpleContentProcessor(session_id)
    simple_processors[session_id] = processor
    await processor.start_processing()
    
async def stop_simple_session_processing(session_id: str):
    """Stop simple content processing for a session"""
    if session_id in simple_processors:
        processor = simple_processors[session_id]
        await processor.stop_processing()
        del simple_processors[session_id]
        
def get_simple_session_processor(session_id: str) -> Optional[SimpleContentProcessor]:
    """Get the simple processor for a session"""
    return simple_processors.get(session_id)
