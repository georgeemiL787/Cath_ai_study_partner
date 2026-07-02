#!/usr/bin/env python3
"""
Test script for Real-Time Study functionality
Demonstrates the AI Study Partner's real-time screen recording and AI assistance
"""

import asyncio
import time
import requests
import json
import base64
from typing import Dict, Any

class RealTimeStudyTester:
    """Test the real-time study functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        
    async def test_start_session(self) -> bool:
        """Test starting a study session"""
        print("🚀 Starting Real-Time Study Session...")
        
        try:
            response = requests.post(f"{self.base_url}/api/realtime-study/start", json={
                "auto_ai_processing": True,
                "processing_interval": 10,
                "fps": 2,
                "audio_enabled": True
            })
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                print(f"✅ Session started successfully!")
                print(f"   Session ID: {self.session_id}")
                print(f"   Active: {data['is_active']}")
                print(f"   Key Points: {len(data['key_points'])}")
                return True
            else:
                print(f"❌ Failed to start session: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting session: {e}")
            return False
    
    async def test_add_content(self) -> bool:
        """Test adding content to the session"""
        if not self.session_id:
            print("❌ No active session")
            return False
            
        print("📝 Adding sample study content...")
        
        sample_content = """
        Machine Learning Fundamentals:
        
        1. Supervised Learning: Learning with labeled examples
           - Classification: Predicting categories
           - Regression: Predicting continuous values
           
        2. Unsupervised Learning: Finding patterns without labels
           - Clustering: Grouping similar data points
           - Dimensionality Reduction: Reducing feature space
           
        3. Neural Networks: Inspired by biological neurons
           - Perceptron: Single layer neural network
           - Deep Learning: Multiple hidden layers
           - Backpropagation: Training algorithm
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/realtime-study/{self.session_id}/content",
                json={
                    "content": sample_content,
                    "content_type": "manual"
                }
            )
            
            if response.status_code == 200:
                print("✅ Content added successfully!")
                return True
            else:
                print(f"❌ Failed to add content: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding content: {e}")
            return False
    
    async def test_ask_question(self) -> bool:
        """Test asking a question about the content"""
        if not self.session_id:
            print("❌ No active session")
            return False
            
        print("❓ Asking AI question about the content...")
        
        question = "What is the difference between supervised and unsupervised learning?"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/realtime-study/{self.session_id}/question",
                json={
                    "question": question,
                    "session_id": self.session_id,
                    "include_citations": True,
                    "top_k": 3
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Question answered successfully!")
                print(f"   Question: {question}")
                print(f"   Answer: {data['answer'][:200]}...")
                print(f"   Model: {data['model']}")
                print(f"   Relevant content: {data['relevant_content_count']} items")
                return True
            else:
                print(f"❌ Failed to ask question: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error asking question: {e}")
            return False
    
    async def test_get_summary(self) -> bool:
        """Test getting session summary"""
        if not self.session_id:
            print("❌ No active session")
            return False
            
        print("📊 Getting session summary...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/realtime-study/{self.session_id}/summary"
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Summary generated successfully!")
                print(f"   Summary: {data['summary'][:300]}...")
                print(f"   Content items: {data['content_items_count']}")
                print(f"   Session duration: {data['session_duration']:.1f}s")
                return True
            else:
                print(f"❌ Failed to get summary: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting summary: {e}")
            return False
    
    async def test_get_key_points(self) -> bool:
        """Test getting key points"""
        if not self.session_id:
            print("❌ No active session")
            return False
            
        print("🔑 Getting key points...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/realtime-study/{self.session_id}/key-points"
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Key points retrieved successfully!")
                print(f"   Key points count: {data['count']}")
                for i, point in enumerate(data['key_points'][:3], 1):
                    print(f"   {i}. {point}")
                return True
            else:
                print(f"❌ Failed to get key points: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting key points: {e}")
            return False
    
    async def test_session_status(self) -> bool:
        """Test getting session status"""
        if not self.session_id:
            print("❌ No active session")
            return False
            
        print("📈 Getting session status...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/realtime-study/{self.session_id}/status"
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Session status retrieved successfully!")
                print(f"   Session ID: {data['session_id']}")
                print(f"   Active: {data['is_active']}")
                print(f"   Duration: {data['stats']['duration']:.1f}s")
                print(f"   Content items: {data['stats']['total_content_items']}")
                print(f"   OCR items: {data['stats']['ocr_items']}")
                print(f"   Speech items: {data['stats']['speech_items']}")
                print(f"   Manual items: {data['stats']['manual_items']}")
                print(f"   Key points: {data['stats']['key_points_count']}")
                print(f"   Questions: {data['stats']['questions_count']}")
                return True
            else:
                print(f"❌ Failed to get session status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting session status: {e}")
            return False
    
    async def test_export_session(self) -> bool:
        """Test exporting session data"""
        if not self.session_id:
            print("❌ No active session")
            return False
            
        print("💾 Exporting session data...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/realtime-study/{self.session_id}/export?format=json"
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Session exported successfully!")
                print(f"   Format: {data['format']}")
                print(f"   Content items: {len(data['data']['content_items'])}")
                print(f"   Key points: {len(data['data']['key_points'])}")
                print(f"   Questions: {len(data['data']['questions'])}")
                
                # Save to file
                filename = f"test_session_export_{int(time.time())}.json"
                with open(filename, 'w') as f:
                    json.dump(data['data'], f, indent=2)
                print(f"   Saved to: {filename}")
                return True
            else:
                print(f"❌ Failed to export session: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error exporting session: {e}")
            return False
    
    async def test_stop_session(self) -> bool:
        """Test stopping the session"""
        if not self.session_id:
            print("❌ No active session")
            return False
            
        print("🛑 Stopping study session...")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/realtime-study/stop",
                json={"session_id": self.session_id}
            )
            
            if response.status_code == 200:
                print("✅ Session stopped successfully!")
                self.session_id = None
                return True
            else:
                print(f"❌ Failed to stop session: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error stopping session: {e}")
            return False
    
    async def run_full_test(self):
        """Run the complete test suite"""
        print("🧪 AI Study Partner - Real-Time Study Test Suite")
        print("=" * 60)
        
        tests = [
            ("Start Session", self.test_start_session),
            ("Add Content", self.test_add_content),
            ("Ask Question", self.test_ask_question),
            ("Get Summary", self.test_get_summary),
            ("Get Key Points", self.test_get_key_points),
            ("Session Status", self.test_session_status),
            ("Export Session", self.test_export_session),
            ("Stop Session", self.test_stop_session),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            print("-" * 40)
            
            try:
                success = await test_func()
                if success:
                    passed += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {e}")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        print("\n" + "=" * 60)
        print(f"🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Real-time study functionality is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

async def main():
    """Main test function"""
    tester = RealTimeStudyTester()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/api/status")
        if response.status_code != 200:
            print("❌ Server is not running or not responding")
            print("   Please start the server with: python backend/main.py")
            return
    except Exception as e:
        print("❌ Cannot connect to server")
        print("   Please start the server with: python backend/main.py")
        print(f"   Error: {e}")
        return
    
    # Run tests
    await tester.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())
