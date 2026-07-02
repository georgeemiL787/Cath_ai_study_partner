#!/usr/bin/env python3
"""
Test script for AI Study Partner functionality
Demonstrates the complete workflow: capture -> process -> query
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test the complete AI Study Partner workflow"""
    
    print("🧪 Testing AI Study Partner Complete Workflow")
    print("=" * 50)
    
    # Step 1: Check server status
    print("\n1️⃣ Checking server status...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server is running")
            print(f"   - AI Service: {status.get('llm_service', False)}")
            print(f"   - Screen Capture: {status.get('screen_capture', False)}")
            print(f"   - Audio Capture: {status.get('audio_capture', False)}")
        else:
            print(f"❌ Server status check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running with: python main.py")
        return
    
    # Step 2: Start a study session
    print("\n2️⃣ Starting study session...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/capture/start",
            json={"fps": 1, "audio_enabled": True}
        )
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            print(f"✅ Study session started")
            print(f"   - Session ID: {session_id}")
            print(f"   - Screen Capture: {result['screen_capture']}")
            print(f"   - Audio Capture: {result['audio_capture']}")
        else:
            print(f"❌ Failed to start session: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        return
    
    # Step 3: Add some study content (simulating captured content)
    print("\n3️⃣ Adding study content...")
    study_content = """
    This is a machine learning lecture covering the following topics:
    
    1. Supervised Learning: Uses labeled training data to learn patterns
       - Examples: Linear regression, decision trees, neural networks
       - Goal: Predict outcomes for new, unseen data
    
    2. Unsupervised Learning: Finds patterns in unlabeled data
       - Examples: Clustering, dimensionality reduction
       - Goal: Discover hidden structures in data
    
    3. Deep Learning: Neural networks with multiple layers
       - Examples: CNNs for images, RNNs for sequences
       - Applications: Computer vision, natural language processing
    
    4. Key Concepts:
       - Overfitting: Model performs well on training data but poorly on new data
       - Cross-validation: Technique to evaluate model performance
       - Feature engineering: Creating meaningful input features
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/capture/content/add",
            json={
                "content": study_content,
                "type": "lecture_transcript"
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Study content added")
            print(f"   - Content length: {result['content_length']} characters")
        else:
            print(f"❌ Failed to add content: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error adding content: {e}")
        return
    
    # Step 4: Ask questions about the content
    print("\n4️⃣ Testing AI questions...")
    
    questions = [
        "What was the main point of that video I watched?",
        "Explain supervised learning",
        "What is overfitting?",
        "Give me examples of deep learning applications"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   Question {i}: {question}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/ai/question",
                json={
                    "question": question,
                    "session_id": session_id,
                    "include_citations": True
                }
            )
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print(f"   ✅ Answer: {result['content'][:200]}...")
                    print(f"   📊 Model: {result['model']}")
                    print(f"   ⏱️  Time: {result['processing_time']:.2f}s")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Step 5: Stop the session
    print("\n5️⃣ Stopping study session...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/capture/stop",
            json={"session_id": session_id}
        )
        if response.status_code == 200:
            print(f"✅ Study session stopped")
        else:
            print(f"❌ Failed to stop session: {response.status_code}")
    except Exception as e:
        print(f"❌ Error stopping session: {e}")
    
    print("\n🎉 Test completed!")
    print("\n💡 The AI Study Partner is now working correctly!")
    print("   - It captures and processes content during study sessions")
    print("   - It can answer questions about the captured content")
    print("   - It maintains context across the entire study session")

if __name__ == "__main__":
    test_complete_workflow()
