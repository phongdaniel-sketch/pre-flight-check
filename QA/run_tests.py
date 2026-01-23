import argparse
import httpx
import sys
import time
from typing import Dict, Any

def run_test(name: str, func) -> bool:
    print(f"Testing {name}...", end=" ")
    try:
        func()
        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_health(base_url: str):
    response = httpx.get(f"{base_url}/api/health", timeout=10.0)
    if response.status_code != 200:
        raise Exception(f"Status {response.status_code} != 200")
    data = response.json()
    if data.get("status") != "ok":
        raise Exception("Status field is not 'ok'")

def test_analyze_flow(base_url: str):
    # Prepare form data
    data = {
        "industry_id": "ECOMM",
        "target_cpa": "50.0",
        "country": "US",
        "budget": "1000.0",
        "landing_page_url": "https://example.com/product",
        "audience_age": "25-34",
        "audience_gender": "ALL"
    }
    
    # We won't send a file, relying on video_url from N8N mock or just LP analysis
    # Since backend requires either video_file, video_url_input OR landing_page_url, we have LP.
    
    response = httpx.post(f"{base_url}/api/analyze", data=data, timeout=30.0)
    
    if response.status_code != 200:
        raise Exception(f"Status {response.status_code}: {response.text}")
    
    result = response.json()
    
    required_keys = ["benchmark_score", "policy_check", "creative_metrics", "final_rating"]
    for key in required_keys:
        if key not in result:
            raise Exception(f"Missing key in response: {key}")
            
    print(f"  [Info] Rating: {result.get('final_rating')}, Score: {result.get('predictive_score')}")

def test_validation_error(base_url: str):
    # Send empty data
    response = httpx.post(f"{base_url}/api/analyze", data={}, timeout=10.0)
    if response.status_code != 422:
        raise Exception(f"Expected 422 for empty payload, got {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description="Run QA Integration Tests")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    args = parser.parse_args()
    
    base_url = args.url.rstrip("/")
    print(f"🚀 Starting QA Tests against: {base_url}\n")
    
    tests = [
        ("Health Check", lambda: test_health(base_url)),
        ("Input Validation", lambda: test_validation_error(base_url)),
        ("Analyze Flow (Happy Path)", lambda: test_analyze_flow(base_url)),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, func in tests:
        if run_test(name, func):
            passed += 1
            
    print(f"\nSummary: {passed}/{total} tests passed.")
    
    if passed < total:
        sys.exit(1)

if __name__ == "__main__":
    main()
