"""
LLM Service Module for AI Study Partner
Handles interactions with Large Language Models for Q&A, summarization, and content generation
"""

from openai import OpenAI
import os
import time
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import re

@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str
    usage: Dict[str, int]
    model: str
    processing_time: float
    citations: List[Dict[str, str]] = None

@dataclass
class LLMConfig:
    """LLM configuration"""
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class LLMService:
    """Service for interacting with Large Language Models"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.logger = logging.getLogger(__name__)
        
        # Override model from environment if set
        env_model = os.getenv("OPENAI_MODEL")
        if env_model:
            self.config.model = env_model
        
        # Initialize OpenAI client
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.warning("No OpenAI API key provided")
            self.client = None
        else:
            client_kwargs = {"api_key": api_key}
            if self.config.base_url:
                client_kwargs["base_url"] = self.config.base_url
            self.client = OpenAI(**client_kwargs)
            
    def generate_summary(self, content: str, max_length: int = 200) -> LLMResponse:
        """Generate a summary of the given content"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY.")
            
        start_time = time.time()
        
        prompt = f"""Please provide a concise summary of the following content in no more than {max_length} words. Focus on the key points and main ideas:

Content:
{content}

Summary:"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant that creates clear, concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content.strip()
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            raise
            
    def answer_question(self, question: str, context: List[str], 
                       include_citations: bool = True) -> LLMResponse:
        """Answer a question based on provided context"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY.")
            
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
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant. Answer questions based on the provided context and cite your sources."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content.strip()
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.config.model,
                processing_time=processing_time,
                citations=citations if include_citations else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to answer question: {e}")
            raise
            
    def generate_flashcards(self, content: str, num_cards: int = 5) -> LLMResponse:
        """Generate flashcards from content"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY.")
            
        start_time = time.time()
        
        prompt = f"""Create {num_cards} flashcards from the following content. Format each card as:
Front: [Question or term]
Back: [Answer or definition]

Content:
{content}

Flashcards:"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant that creates effective flashcards for learning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content.strip()
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate flashcards: {e}")
            raise
            
    def generate_quiz(self, content: str, num_questions: int = 5, 
                     question_types: List[str] = None) -> LLMResponse:
        """Generate quiz questions from content"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY.")
            
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
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant that creates effective quiz questions for learning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content.strip()
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate quiz: {e}")
            raise
            
    def extract_key_concepts(self, content: str, max_concepts: int = 10) -> LLMResponse:
        """Extract key concepts from content"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY.")
            
        start_time = time.time()
        
        prompt = f"""Extract the {max_concepts} most important concepts from the following content. For each concept, provide a brief definition.

Content:
{content}

Key Concepts:"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant that identifies key concepts and provides clear definitions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content.strip()
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract key concepts: {e}")
            raise
            
    def create_study_plan(self, topics: List[str], time_available: str = "1 week") -> LLMResponse:
        """Create a study plan for given topics"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY.")
            
        start_time = time.time()
        
        topics_text = "\n".join(f"- {topic}" for topic in topics)
        
        prompt = f"""Create a detailed study plan for the following topics with the time available: {time_available}

Topics:
{topics_text}

Study Plan:"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant that creates effective study plans with realistic timelines."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content.strip()
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.config.model,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create study plan: {e}")
            raise
            
    def parse_flashcards(self, flashcard_text: str) -> List[Dict[str, str]]:
        """Parse flashcard text into structured format"""
        cards = []
        
        # Split by "Front:" or "Q:" patterns
        parts = re.split(r'(?:Front:|Q:)', flashcard_text)
        
        for part in parts[1:]:  # Skip first empty part
            lines = part.strip().split('\n')
            if len(lines) < 2:
                continue
                
            front = lines[0].strip()
            back_lines = []
            
            for line in lines[1:]:
                if line.strip().startswith(('Back:', 'A:')):
                    back_lines.append(line.strip()[4:].strip())
                elif line.strip() and not line.strip().startswith('Front:'):
                    back_lines.append(line.strip())
                    
            if front and back_lines:
                cards.append({
                    "front": front,
                    "back": " ".join(back_lines)
                })
                
        return cards
        
    def parse_quiz_questions(self, quiz_text: str) -> List[Dict[str, Any]]:
        """Parse quiz text into structured format"""
        questions = []
        
        # Split by "Q:" pattern
        parts = re.split(r'Q:', quiz_text)
        
        for part in parts[1:]:  # Skip first empty part
            lines = part.strip().split('\n')
            if len(lines) < 2:
                continue
                
            question_text = lines[0].strip()
            options = []
            correct_answer = None
            
            for line in lines[1:]:
                line = line.strip()
                if re.match(r'^[A-D]\)', line):
                    options.append(line[2:].strip())
                elif line.startswith('Correct Answer:'):
                    correct_answer = line[15:].strip()
                elif line.startswith('A:'):
                    # Short answer question
                    questions.append({
                        "type": "short_answer",
                        "question": question_text,
                        "answer": line[2:].strip()
                    })
                    break
                    
            if options and correct_answer:
                questions.append({
                    "type": "multiple_choice",
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_answer
                })
                
        return questions
