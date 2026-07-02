"""
Unified LLM Service Module for AI Study Partner
Handles interactions with Gemini, OpenAI, and OpenAI-compatible providers (e.g., DeepSeek)
"""

import os
import time
import logging
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass

from .llm_service import LLMService, LLMResponse, LLMConfig
from .gemini_service import GeminiService, GeminiResponse, GeminiConfig

@dataclass
class UnifiedLLMResponse:
    """Unified LLM response structure"""
    content: str
    usage: Dict[str, int]
    model: str
    processing_time: float
    citations: List[Dict[str, str]] = None
    provider: str = "unknown"  # "openai" or "gemini"

class UnifiedLLMService:
    """Unified service for interacting with multiple LLM providers"""
    
    def __init__(self, provider: str = "gemini"):
        self.provider = provider.lower()
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.openai_service = None  # Used for OpenAI and OpenAI-compatible providers
        self.gemini_service = None
        
        # Initialize based on provider preference
        if self.provider in ["gemini", "auto"]:
            try:
                gemini_config = GeminiConfig()
                self.gemini_service = GeminiService(gemini_config)
                if self.gemini_service.model:
                    self.logger.info("✅ Gemini service initialized")
                else:
                    self.logger.warning("⚠️ Gemini service not available")
            except Exception as e:
                self.logger.warning(f"⚠️ Gemini service failed to initialize: {e}")
        
        # OpenAI (native)
        if self.provider in ["openai", "auto"]:
            try:
                openai_config = LLMConfig()
                self.openai_service = LLMService(openai_config)
                if self.openai_service.client:
                    self.logger.info("✅ OpenAI service initialized")
                else:
                    self.logger.warning("⚠️ OpenAI service not available")
            except Exception as e:
                self.logger.warning(f"⚠️ OpenAI service failed to initialize: {e}")

        # DeepSeek (OpenAI-compatible)
        if self.provider in ["deepseek", "auto"] and self.openai_service is None:
            try:
                deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
                deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
                deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
                config = LLMConfig(
                    model=deepseek_model,
                    api_key=deepseek_api_key,
                    base_url=deepseek_base_url
                )
                self.openai_service = LLMService(config)
                if self.openai_service.client:
                    self.logger.info("✅ DeepSeek (OpenAI-compatible) service initialized")
                else:
                    self.logger.warning("⚠️ DeepSeek service not available")
            except Exception as e:
                self.logger.warning(f"⚠️ DeepSeek service failed to initialize: {e}")
        
        # Determine which service to use
        self.active_service = self._get_active_service()
        if self.active_service:
            self.logger.info(f"🎯 Using {self.active_service['provider']} as primary service")
        else:
            self.logger.error("❌ No LLM services available")
    
    def _get_active_service(self) -> Optional[Dict[str, Any]]:
        """Get the active service based on provider preference"""
        if self.provider == "gemini" and self.gemini_service and self.gemini_service.model:
            return {"service": self.gemini_service, "provider": "gemini"}
        elif self.provider == "openai" and self.openai_service and self.openai_service.client:
            return {"service": self.openai_service, "provider": "openai"}
        elif self.provider == "deepseek" and self.openai_service and self.openai_service.client:
            return {"service": self.openai_service, "provider": "deepseek"}
        elif self.provider == "auto":
            # Try Gemini first, then OpenAI
            if self.gemini_service and self.gemini_service.model:
                return {"service": self.gemini_service, "provider": "gemini"}
            elif self.openai_service and self.openai_service.client:
                # Could be OpenAI or DeepSeek via LLMService
                # Detect based on environment; prefer deepseek when DEEPSEEK_API_KEY is present
                provider = "deepseek" if os.getenv("DEEPSEEK_API_KEY") else "openai"
                return {"service": self.openai_service, "provider": provider}
        return None
    
    def _convert_response(self, response: Union[LLMResponse, GeminiResponse], provider: str) -> UnifiedLLMResponse:
        """Convert provider-specific response to unified format"""
        return UnifiedLLMResponse(
            content=response.content,
            usage=response.usage,
            model=response.model,
            processing_time=response.processing_time,
            citations=response.citations,
            provider=provider
        )
    
    def generate_summary(self, content: str, max_length: int = 200) -> UnifiedLLMResponse:
        """Generate a summary of the given content"""
        if not self.active_service:
            raise Exception("No LLM service available")
        
        response = self.active_service["service"].generate_summary(content, max_length)
        return self._convert_response(response, self.active_service["provider"])
    
    def answer_question(self, question: str, context: List[str], 
                       include_citations: bool = True) -> UnifiedLLMResponse:
        """Answer a question based on provided context"""
        if not self.active_service:
            raise Exception("No LLM service available")
        
        # Prepend assistant persona to the question for consistent branding
        assistant_name = os.getenv("ASSISTANT_NAME", "AI Study Partner")
        branded_question = f"You are {assistant_name}. " + question
        response = self.active_service["service"].answer_question(branded_question, context, include_citations)
        return self._convert_response(response, self.active_service["provider"])
    
    def generate_flashcards(self, content: str, num_cards: int = 5) -> UnifiedLLMResponse:
        """Generate flashcards from content"""
        if not self.active_service:
            raise Exception("No LLM service available")
        
        response = self.active_service["service"].generate_flashcards(content, num_cards)
        return self._convert_response(response, self.active_service["provider"])
    
    def generate_quiz(self, content: str, num_questions: int = 5, 
                     question_types: List[str] = None) -> UnifiedLLMResponse:
        """Generate quiz questions from content"""
        if not self.active_service:
            raise Exception("No LLM service available")
        
        response = self.active_service["service"].generate_quiz(content, num_questions, question_types)
        return self._convert_response(response, self.active_service["provider"])
    
    def extract_key_concepts(self, content: str, max_concepts: int = 10) -> UnifiedLLMResponse:
        """Extract key concepts from content"""
        if not self.active_service:
            raise Exception("No LLM service available")
        
        response = self.active_service["service"].extract_key_concepts(content, max_concepts)
        return self._convert_response(response, self.active_service["provider"])
    
    def create_study_plan(self, topics: List[str], time_available: str = "1 week") -> UnifiedLLMResponse:
        """Create a study plan for given topics"""
        if not self.active_service:
            raise Exception("No LLM service available")
        
        response = self.active_service["service"].create_study_plan(topics, time_available)
        return self._convert_response(response, self.active_service["provider"])
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        return {
            "provider": self.provider,
            "active_service": self.active_service["provider"] if self.active_service else None,
            "gemini_available": self.gemini_service is not None and self.gemini_service.model is not None,
            "openai_available": self.openai_service is not None and self.openai_service.client is not None and self.active_service and self.active_service["provider"] == "openai",
            "deepseek_available": self.openai_service is not None and self.openai_service.client is not None and (self.provider == "deepseek" or (self.provider == "auto" and os.getenv("DEEPSEEK_API_KEY")) ),
            "gemini_model": self.gemini_service.config.model if self.gemini_service else None,
            "openai_model": self.openai_service.config.model if (self.openai_service and (self.provider == "openai")) else None,
            "deepseek_model": self.openai_service.config.model if (self.openai_service and (self.provider == "deepseek" or (self.provider == "auto" and os.getenv("DEEPSEEK_API_KEY")))) else None
        }
