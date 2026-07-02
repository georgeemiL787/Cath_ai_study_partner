#!/usr/bin/env python3
"""
Test script for unified AI service with Gemini
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.ai.unified_llm_service import UnifiedLLMService

def test_unified_ai_service():
    """Test the unified AI service"""
    print("Testing Unified AI service...")
    
    # Check if API keys are set
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"Gemini API key: {'✅ Set' if gemini_key else '❌ Not set'}")
    print(f"OpenAI API key: {'✅ Set' if openai_key else '❌ Not set'}")
    
    try:
        # Initialize the service with Gemini as default
        service = UnifiedLLMService(provider="gemini")
        
        # Check status
        status = service.get_status()
        print(f"\n📊 Service Status:")
        print(f"  Provider: {status['provider']}")
        print(f"  Active Service: {status['active_service']}")
        print(f"  Gemini Available: {status['gemini_available']}")
        print(f"  OpenAI Available: {status['openai_available']}")
        print(f"  Gemini Model: {status['gemini_model']}")
        print(f"  OpenAI Model: {status['openai_model']}")
        
        if not service.active_service:
            print("❌ No active service available")
            return False
        
        # Test a simple question
        print(f"\nTesting question answering with {service.active_service['provider']}...")
        response = service.answer_question(
            question="What is 2+2?",
            context=[],
            include_citations=False
        )
        
        print(f"✅ AI Response: {response.content}")
        print(f"✅ Model: {response.model}")
        print(f"✅ Provider: {response.provider}")
        print(f"✅ Processing time: {response.processing_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_unified_ai_service()
    if success:
        print("\n🎉 Unified AI service test passed!")
    else:
        print("\n💥 Unified AI service test failed!")
        sys.exit(1)
