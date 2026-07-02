"""
AI API endpoints for AI Study Partner
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time

from ..ai.unified_llm_service import UnifiedLLMService, UnifiedLLMResponse
# from ..database.vector_db import VectorDB
from ..services import service_manager
from ..capture.simple_content_processor import get_simple_session_processor

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    include_citations: bool = True
    top_k: int = 5

class SummaryRequest(BaseModel):
    content: str
    max_length: int = 200

class FlashcardRequest(BaseModel):
    content: str
    num_cards: int = 5

class QuizRequest(BaseModel):
    content: str
    num_questions: int = 5
    question_types: List[str] = ["multiple_choice", "short_answer"]

class StudyPlanRequest(BaseModel):
    topics: List[str]
    time_available: str = "1 week"

class AIResponse(BaseModel):
    success: bool
    content: str
    processing_time: float
    model: str
    usage: Optional[Dict[str, int]] = None
    citations: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None

# Dependency to get vector database
async def get_vector_db():
    return service_manager.vector_db

# Dependency to get LLM service
async def get_llm_service() -> UnifiedLLMService:
    return service_manager.llm_service

@router.post("/question", response_model=AIResponse)
async def answer_question(request: QuestionRequest, vector_db = Depends(get_vector_db), llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Answer a question based on session content"""
    if not llm_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")
        
    start_time = time.time()
    
    try:
        # Get relevant context from simple content processor
        context = []
        if request.session_id:
            try:
                processor = get_simple_session_processor(request.session_id)
                if processor:
                    search_results = await processor.search_content(request.question, request.top_k)
                    context = [doc.content for doc in search_results]
            except Exception as e:
                print(f"Error searching content: {e}")
                context = []
            
        # Generate answer using LLM
        response = llm_service.answer_question(
            request.question,
            context,
            include_citations=request.include_citations
        )
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            success=True,
            content=response.content,
            processing_time=processing_time,
            model=response.model,
            usage=response.usage,
            citations=response.citations
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return AIResponse(
            success=False,
            content="",
            processing_time=processing_time,
            model="",
            error=str(e)
        )

@router.post("/summarize", response_model=AIResponse)
async def generate_summary(request: SummaryRequest, llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Generate a summary of content"""
    if not llm_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")
        
    start_time = time.time()
    
    try:
        response = llm_service.generate_summary(request.content, request.max_length)
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            success=True,
            content=response.content,
            processing_time=processing_time,
            model=response.model,
            usage=response.usage
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return AIResponse(
            success=False,
            content="",
            processing_time=processing_time,
            model="",
            error=str(e)
        )

@router.post("/flashcards", response_model=AIResponse)
async def generate_flashcards(request: FlashcardRequest, llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Generate flashcards from content"""
    if not llm_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")
        
    start_time = time.time()
    
    try:
        response = llm_service.generate_flashcards(request.content, request.num_cards)
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            success=True,
            content=response.content,
            processing_time=processing_time,
            model=response.model,
            usage=response.usage
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return AIResponse(
            success=False,
            content="",
            processing_time=processing_time,
            model="",
            error=str(e)
        )

@router.post("/quiz", response_model=AIResponse)
async def generate_quiz(request: QuizRequest, llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Generate quiz questions from content"""
    if not llm_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")
        
    start_time = time.time()
    
    try:
        response = llm_service.generate_quiz(
            request.content, 
            request.num_questions, 
            request.question_types
        )
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            success=True,
            content=response.content,
            processing_time=processing_time,
            model=response.model,
            usage=response.usage
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return AIResponse(
            success=False,
            content="",
            processing_time=processing_time,
            model="",
            error=str(e)
        )

@router.post("/study-plan", response_model=AIResponse)
async def create_study_plan(request: StudyPlanRequest, llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Create a study plan for given topics"""
    if not llm_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")
        
    start_time = time.time()
    
    try:
        response = llm_service.create_study_plan(request.topics, request.time_available)
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            success=True,
            content=response.content,
            processing_time=processing_time,
            model=response.model,
            usage=response.usage
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return AIResponse(
            success=False,
            content="",
            processing_time=processing_time,
            model="",
            error=str(e)
        )

@router.post("/key-concepts", response_model=AIResponse)
async def extract_key_concepts(request: SummaryRequest, llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Extract key concepts from content"""
    if not llm_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")
        
    start_time = time.time()
    
    try:
        response = llm_service.extract_key_concepts(request.content, request.max_length)
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            success=True,
            content=response.content,
            processing_time=processing_time,
            model=response.model,
            usage=response.usage
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return AIResponse(
            success=False,
            content="",
            processing_time=processing_time,
            model="",
            error=str(e)
        )

@router.post("/parse/flashcards")
async def parse_flashcards(content: str, llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Parse flashcard text into structured format"""
    if not llm_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")
        
    try:
        cards = llm_service.parse_flashcards(content)
        
        return {
            "success": True,
            "cards": cards,
            "count": len(cards)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse flashcards: {str(e)}")

@router.post("/parse/quiz")
async def parse_quiz_questions(content: str, llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Parse quiz text into structured format"""
    if not llm_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")
        
    try:
        questions = llm_service.parse_quiz_questions(content)
        
        return {
            "success": True,
            "questions": questions,
            "count": len(questions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse quiz: {str(e)}")

@router.get("/models")
async def get_available_models(llm_service: UnifiedLLMService = Depends(get_llm_service)):
    """Get available AI models and their status"""
    if not llm_service:
        return {
            "status": "not_initialized",
            "models": []
        }
    
    # Get status from the unified service
    status = llm_service.get_status()
    
    # Get config from active service
    config = {}
    if llm_service.active_service:
        active_service = llm_service.active_service["service"]
        if hasattr(active_service, 'config'):
            config = {
                "max_tokens": getattr(active_service.config, 'max_tokens', 1000),
                "temperature": getattr(active_service.config, 'temperature', 0.7)
            }
    
    return {
        "status": "initialized",
        "current_model": status.get("gemini_model") or status.get("openai_model") or status.get("deepseek_model") or "unknown",
        "provider": status.get("active_service", "unknown"),
        "available_models": [
            "gemini-1.5-flash",
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "deepseek-chat"
        ],
        "config": config,
        "services": {
            "gemini_available": status.get("gemini_available", False),
            "openai_available": status.get("openai_available", False),
            "deepseek_available": status.get("deepseek_available", False)
        }
    }

