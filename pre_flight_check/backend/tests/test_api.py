import requests
import os
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("[TEST] Checking Health...")
    try:
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        print("✅ Health Check Passed")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")

def test_analyze():
    print("\n[TEST] Testing Analysis Endpoint...")
    
    # Create dummy video
    with open("test_video.mp4", "wb") as f:
        f.write(b"dummy video content")
        
    files = {'video_file': ('test_video.mp4', open('test_video.mp4', 'rb'), 'video/mp4')}
    data = {
        'industry_id': 'FIN', # Avg CPA $750
        'target_cpa': 150,    # Score should be (150/750)*100 = 20
        'country': 'VN',
        'budget': 5000,
        'landing_page_url': 'https://example.com'
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze", files=files, data=data)
        if resp.status_code != 200:
            print(f"❌ Analysis Failed: {resp.text}")
            return
            
        json_data = resp.json()
        print(f"✅ Response Received: {json_data['final_rating']}")
        
        # Verify Benchmark
        expected_benchmark = (150 / 750) * 100 # 20.0
        actual_benchmark = json_data['benchmark_score']
        
        if abs(actual_benchmark - expected_benchmark) < 0.1:
            print(f"✅ Benchmark Calculation Correct: {actual_benchmark}")
        else:
            print(f"❌ Benchmark Mismatch: Expected {expected_benchmark}, Got {actual_benchmark}")
            
        print(f"ℹ️  Policy Result: {json_data['policy_check']}")
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
    finally:
        if os.path.exists("test_video.mp4"):
            os.remove("test_video.mp4")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2) 
    test_health()
    test_analyze()
