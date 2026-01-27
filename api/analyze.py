from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import tempfile
import logging
import imageio.v3 as iio
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vercel_function")

class TikTokVideoAnalyzer:
    """
    Ultra-Lite version of TikTokVideoAnalyzer for Vercel (Size constrained).
    Uses ONLY Pillow and imageio (No OpenCV/Numpy).
    """
    def __init__(self, video_path):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")
        self.video_path = video_path
        
        try:
            # excessive metadata reading can be slow, just use basic props
            props = iio.imread(video_path, index=None, plugin="pyav") # plugin="pyav" is lighter usually if ffmpeg backend
            # Note: imageio.v3 doesn't give easy metadata without reading.
            # actually let's use a cleaner approach with 'imageio' metadata
            meta = iio.immeta(video_path, plugin="pyav")
            self.duration = meta.get("duration", 0)
            self.fps = meta.get("fps", 30)
            self.video_path = video_path
        except Exception as e:
            logger.warning(f"Metadata read failed: {e}. Using defaults.")
            self.duration = 0
            self.fps = 30

    def analyze_duration(self):
        """Check if duration is between 15s-45s."""
        is_valid = 15 <= self.duration <= 45
        return {
            "duration_seconds": round(self.duration, 2),
            "is_valid_duration": is_valid
        }

    def analyze_scenes(self):
        """Estimate scenes using Histogram difference (Lightweight PIL version)."""
        try:
            scene_cuts = []
            prev_hist = None
            
            # Optimization: Check 1 frame per second (approx)
            # Iterating via imageio is efficient
            
            frame_indices = []
            # We want to sample frames. Reading all is too slow.
            # imageio allows seeking/iterating.
            
            # Simple approach: Read every Nth frame?
            # With pyav plugin, we can iterate. 
            
            step = 10 # Check every 10th frame (approx 3 checks per sec at 30fps)
            
            count = 0
            num_scenes = 1
            
            # Using iio.imap for generator efficiency
            for frame in iio.imap(self.video_path, plugin="pyav"):
                count += 1
                if count % step != 0:
                    continue
                    
                # Resize for speed (Analysis Resolution)
                # Ensure it's a PIL Image
                img = Image.fromarray(frame)
                img = img.resize((64, 64))
                
                # Histogram
                hist = img.histogram()
                
                if prev_hist is not None:
                    # Manually calculate correlation/diff
                    # Simple Manhattan distance or similar
                    # Check difference sum
                    diff = sum(abs(a - b) for a, b in zip(hist, prev_hist))
                    
                    # Threshold for 64x64 image (4096 pixels * 3 channels = 12288 check)
                    # Sensitivity needs calibration. 
                    # Let's say if > 25% change?
                    # Total limit: 4096 * 255 * 3 (approx) is max diff.
                    # Heuristic: 
                    threshold = 300000 # Experimental
                    
                    if diff > threshold:
                        timestamp = count / self.fps
                        scene_cuts.append(timestamp)
                        num_scenes += 1
                
                prev_hist = hist
                
                # Limit to first 10 seconds to save processing time on Vercel
                if (count / self.fps) > 10:
                    break

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
            pass # nothing to release for iio

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
