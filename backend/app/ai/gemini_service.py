"""
Gemini Service Module for AI Study Partner
Handles interactions with Google's Gemini AI for Q&A, summarization, and content generation
"""

import google.generativeai as genai
import os
import time
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class GeminiResponse:
    """Gemini response structure"""
    content: str
    usage: Dict[str, int]
    model: str
    processing_time: float
    citations: List[Dict[str, str]] = None

@dataclass
class GeminiConfig:
    """Gemini configuration"""
    model: str = "gemini-1.5-flash"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000

class GeminiService:
    """Service for interacting with Google's Gemini AI"""
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or GeminiConfig()
        self.logger = logging.getLogger(__name__)
        
        # Get API key from config or environment
        api_key = self.config.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.logger.warning("No Gemini API key provided")
            self.model = None
        else:
            # Configure Gemini
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.config.model)
            self.logger.info(f"Gemini service initialized with model: {self.config.model}")
    
    def generate_summary(self, content: str, max_length: int = 200) -> GeminiResponse:
        """Generate a summary of the given content"""
        if not self.model:
            raise Exception("Gemini model not initialized. Please set GEMINI_API_KEY.")
            
        start_time = time.time()
        
        prompt = f"""Please provide a concise summary of the following content in no more than {max_length} words. Focus on the key points and main ideas:

Content:
{content}

Summary:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.text.strip()
            processing_time = time.time() - start_time
            
            return GeminiResponse(
                content=content,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},  # Gemini doesn't provide detailed usage
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            raise
            
    def answer_question(self, question: str, context: List[str], 
                       include_citations: bool = True) -> GeminiResponse:
        """Answer a question based on provided context"""
        if not self.model:
            raise Exception("Gemini model not initialized. Please set GEMINI_API_KEY.")
            
        start_time = time.time()
        
        # Format context with citations
        context_text = ""
        citations = []
        
        for i, ctx in enumerate(context, 1):
            context_text += f"[{i}] {ctx}\n"
            if include_citations:
                citations.append({
                    "id": str(i),
                    "content": ctx[:100] + "..." if len(ctx) > 100 else ctx
                })
        
        prompt = f"""Based on the following context, please answer the question. If you reference information from the context, cite it using [1], [2], etc.

Context:
{context_text}

Question: {question}

Answer:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.text.strip()
            processing_time = time.time() - start_time
            
            return GeminiResponse(
                content=content,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                model=self.config.model,
                processing_time=processing_time,
                citations=citations if include_citations else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to answer question: {e}")
            raise
            
    def generate_flashcards(self, content: str, num_cards: int = 5) -> GeminiResponse:
        """Generate flashcards from content"""
        if not self.model:
            raise Exception("Gemini model not initialized. Please set GEMINI_API_KEY.")
            
        start_time = time.time()
        
        prompt = f"""Create {num_cards} flashcards from the following content. Format each card as:
Front: [Question or term]
Back: [Answer or definition]

Content:
{content}

Flashcards:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.text.strip()
            processing_time = time.time() - start_time
            
            return GeminiResponse(
                content=content,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate flashcards: {e}")
            raise
            
    def generate_quiz(self, content: str, num_questions: int = 5, 
                     question_types: List[str] = None) -> GeminiResponse:
        """Generate quiz questions from content"""
        if not self.model:
            raise Exception("Gemini model not initialized. Please set GEMINI_API_KEY.")
            
        if question_types is None:
            question_types = ["multiple_choice", "short_answer"]
            
        start_time = time.time()
        
        prompt = f"""Create {num_questions} quiz questions from the following content. Include a mix of question types: {', '.join(question_types)}.

For multiple choice questions, format as:
Q: [Question]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
Correct Answer: [Letter]

For short answer questions, format as:
Q: [Question]
A: [Answer]

Content:
{content}

Quiz Questions:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.text.strip()
            processing_time = time.time() - start_time
            
            return GeminiResponse(
                content=content,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate quiz: {e}")
            raise
            
    def extract_key_concepts(self, content: str, max_concepts: int = 10) -> GeminiResponse:
        """Extract key concepts from content"""
        if not self.model:
            raise Exception("Gemini model not initialized. Please set GEMINI_API_KEY.")
            
        start_time = time.time()
        
        prompt = f"""Extract the {max_concepts} most important concepts from the following content. For each concept, provide a brief definition.

Content:
{content}

Key Concepts:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.text.strip()
            processing_time = time.time() - start_time
            
            return GeminiResponse(
                content=content,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract key concepts: {e}")
            raise
            
    def create_study_plan(self, topics: List[str], time_available: str = "1 week") -> GeminiResponse:
        """Create a study plan for given topics"""
        if not self.model:
            raise Exception("Gemini model not initialized. Please set GEMINI_API_KEY.")
            
        start_time = time.time()
        
        topics_text = "\n".join(f"- {topic}" for topic in topics)
        
        prompt = f"""Create a detailed study plan for the following topics with the time available: {time_available}

Topics:
{topics_text}

Study Plan:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.text.strip()
            processing_time = time.time() - start_time
            
            return GeminiResponse(
                content=content,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create study plan: {e}")
            raise
