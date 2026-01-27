from http.server import BaseHTTPRequestHandler
import json
import os
import cv2
import numpy as np
import requests
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vercel_function")

class TikTokVideoAnalyzer:
    """
    Lite version of TikTokVideoAnalyzer for Vercel (Size constrained).
    Uses ONLY opencv-python-headless and numpy.
    """
    def __init__(self, video_path):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
             raise ValueError(f"Could not open video file: {video_path}")
             
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def analyze_duration(self):
        """Check if duration is between 15s-45s."""
        is_valid = 15 <= self.duration <= 45
        return {
            "duration_seconds": round(self.duration, 2),
            "is_valid_duration": is_valid
        }

    def analyze_scenes(self):
        """Estimate scenes using Histogram difference (Lightweight)."""
        try:
            scene_cuts = []
            prev_hist = None
            
            # Optimization: Check every 5th frame
            step = 5
            
            for i in range(0, self.frame_count, step):
                # Fast forward logic handled by reading loop if not seeking
                # Ideally we set pos, but it's slow. 
                # For this simple implementation, we might just grab() to skip
                if i > 0:
                    for _ in range(step - 1): self.cap.grab()
                
                ret, frame = self.cap.retrieve()
                if not ret: break
                
                # Resize for faster processing
                small_frame = cv2.resize(frame, (64, 64))
                
                # Convert to HSV
                hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
                hist = cv2.calcHist([hsv], [0], None, [256], [0, 256])
                cv2.normalize(hist, hist)
                
                if prev_hist is not None:
                    score = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    if score < 0.7: 
                        timestamp = i / self.fps
                        scene_cuts.append(timestamp)
                
                prev_hist = hist

            num_scenes = len(scene_cuts) + 1
            pacing_rate = self.duration / num_scenes if num_scenes > 0 else self.duration

            # Benchmark Scoring logic matched with JS
            if 1.5 <= pacing_rate <= 2.5:
                pacing_score = 100
            elif pacing_rate > 4.0:
                pacing_score = 40
            elif pacing_rate > 2.5:
                pacing_score = 100 - 40 * (pacing_rate - 2.5)
                pacing_score = max(40, pacing_score)
            else:
                pacing_score = 80 
                
            return {
                "scene_cuts_timestamp": scene_cuts,
                "number_of_scenes": num_scenes,
                "pacing_rate_sec_per_scene": round(pacing_rate, 2),
                "pacing_score": int(pacing_score)
            }
        except Exception as e:
            logger.error(f"Lite Scene analysis failed: {e}")
            return {
                "scene_cuts_timestamp": [],
                "number_of_scenes": 1,
                "pacing_rate_sec_per_scene": self.duration,
                "pacing_score": 50
            }

    def analyze_hook(self, scene_cuts):
        """Analyze first 3 seconds for Hook Score (Lite)."""
        hook_score = 30 # Baseline
        hook_factors = { "has_text": False, "has_fast_cut": False, "has_human": False }
        
        # 1. Check fast cuts in first 3s
        if any(cut <= 3.0 for cut in scene_cuts):
            hook_score += 40
            hook_factors["has_fast_cut"] = True

        # Placeholder for other checks (requires heavier models)
            
        return { "hook_score": min(hook_score, 100), "hook_factors": hook_factors }
    
    def run_full_analysis(self):
        try:
            duration_result = self.analyze_duration()
            scene_result = self.analyze_scenes()
            hook_result = self.analyze_hook(scene_result["scene_cuts_timestamp"])
            
            return {
                "creative": {
                    "hook": hook_result["hook_score"],
                    "pacing": scene_result["pacing_score"],
                    "safe_zone": True, # Placeholder
                    "duration": duration_result["duration_seconds"],
                    "details": {
                        "hook_factors": hook_result["hook_factors"],
                        "pacing_data": scene_result
                    }
                }
            }
        finally:
            self.cap.release()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            video_url = body.get('video_url')
            if not video_url:
                self.send_error(400, "Missing video_url")
                return

            # Download Video to /tmp
            logger.info(f"Downloading video from {video_url}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir='/tmp') as tmp_file:
                response = requests.get(video_url, stream=True)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name

            # Configure Analysis
            analyzer = TikTokVideoAnalyzer(tmp_path)
            result = analyzer.run_full_analysis()
            
            # Cleanup
            os.remove(tmp_path)
            
            # Response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
