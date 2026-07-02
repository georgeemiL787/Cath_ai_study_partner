#!/usr/bin/env python3
"""
Simple test script to verify AI service works
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.ai.llm_service import LLMService, LLMConfig

def test_ai_service():
    """Test the AI service"""
    print("Testing AI service...")
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key.startswith('your_'):
        print("❌ OpenAI API key not set properly")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Initialize the service
        config = LLMConfig()
        service = LLMService(config)
        
        if not service.client:
            print("❌ OpenAI client not initialized")
            return False
        
        print("✅ OpenAI client initialized")
        
        # Test a simple question
        print("Testing question answering...")
        response = service.answer_question(
            question="What is 2+2?",
            context=[],
            include_citations=False
        )
        
        print(f"✅ AI Response: {response.content}")
        print(f"✅ Model: {response.model}")
        print(f"✅ Processing time: {response.processing_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_service()
    if success:
        print("\n🎉 AI service test passed!")
    else:
        print("\n💥 AI service test failed!")
        sys.exit(1)
