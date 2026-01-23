import httpx
import sys

# Test against Production because local env is broken (fastapi import hang)
BASE_URL = "https://pre-flight-check-kohl.vercel.app"

def test_partial_inputs():
    print(f"🚀 Testing Partial Inputs against {BASE_URL}\n")

    # Common payload data
    base_data = {
        "industry_id": "ECOMM",
        "target_cpa": "50.0",
        "country": "US",
        "budget": "1000.0",
        "audience_age": "25-34",
    }

    # 1. Video Only - Should Pass (200)
    print("Test 1: Video Only... ", end="")
    data_video = base_data.copy()
    data_video["video_url_input"] = "https://example.com/video.mp4"
    # landing_page_url OMITTED

    try:
        r = httpx.post(f"{BASE_URL}/api/analyze", data=data_video, timeout=30.0)
        if r.status_code == 200:
            print("✅ PASSED")
        else:
            print(f"❌ FAILED (Status {r.status_code}: {r.text[:100]})")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    # 2. LP Only - Should Pass (200)
    print("Test 2: LP Only...    ", end="")
    data_lp = base_data.copy()
    data_lp["landing_page_url"] = "https://example.com/product"
    # video inputs OMITTED

    try:
        r = httpx.post(f"{BASE_URL}/api/analyze", data=data_lp, timeout=30.0)
        if r.status_code == 200:
            print("✅ PASSED")
        else:
            print(f"❌ FAILED (Status {r.status_code}: {r.text[:100]})")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    # 3. Both Missing - Should Fail (400)
    print("Test 3: Both Missing... ", end="")
    data_missing = base_data.copy()
    # Both video and LP OMITTED

    try:
        r = httpx.post(f"{BASE_URL}/api/analyze", data=data_missing, timeout=30.0)
        if r.status_code == 400:
            print("✅ PASSED")
        else:
            print(f"❌ FAILED (Expected 400, got {r.status_code}: {r.text[:100]})")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_partial_inputs()
