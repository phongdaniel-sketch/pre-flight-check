import sys
import os

# Create a dummy video file if curl failed (fallback) or verify it exists
video_path = "sample_video.mp4"

if not os.path.exists(video_path):
    print("Error: sample_video.mp4 not found. Cannot run test.")
    sys.exit(1)

# Add current dir to path to find api module
sys.path.append(os.getcwd())

try:
    from api.creative_analyzer import TikTokVideoAnalyzer
    
    print(f"Analyzing {video_path}...")
    analyzer = TikTokVideoAnalyzer(video_path)
    result = analyzer.run_full_analysis()
    
    import json
    print(json.dumps(result, indent=2))
    
    # Simple assertions
    creative = result.get("creative", {})
    if creative.get("duration", 0) > 0 and creative.get("pacing", 0) > 0:
        print("\n✅ Creative Analysis Passed (Duration & Pacing detected)")
    else:
        print("\n❌ Creative Analysis Failed (Zero values)")

except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure requirements are installed (opencv, etc).")
except Exception as e:
    print(f"Runtime Error: {e}")
