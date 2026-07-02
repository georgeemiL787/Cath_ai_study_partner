#!/usr/bin/env python3
"""
Check available OpenAI models
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def check_available_models():
    """Check what models are available"""
    print("Checking available OpenAI models...")
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key.startswith('your_'):
        print("❌ OpenAI API key not set properly")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # List available models
        print("Fetching available models...")
        models = client.models.list()
        
        print("\n📋 Available models:")
        for model in models.data:
            print(f"  - {model.id}")
        
        # Test with a simple model
        print("\nTesting with gpt-3.5-turbo...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say hello"}
            ],
            max_tokens=10
        )
        
        print(f"✅ Test successful! Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = check_available_models()
    if success:
        print("\n🎉 Model check completed!")
    else:
        print("\n💥 Model check failed!")
        sys.exit(1)

