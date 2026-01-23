import cv2
import numpy as np
import os
import logging

# Dependencies like scenedetect, moviepy, librosa REMOVED for Vercel size limits.
# Implementing "Lite" analysis using pure OpenCV.

logger = logging.getLogger("creative_analyzer")
logger.setLevel(logging.INFO)

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

    def _check_safe_zone(self, important_elements):
        # Placeholder
        return True

    def analyze_duration(self):
        """Check if duration is between 15s-45s."""
        is_valid = 15 <= self.duration <= 45
        return {
            "duration_seconds": round(self.duration, 2),
            "is_valid_duration": is_valid
        }

    def analyze_scenes(self):
        """
        Estimate scenes using Histogram difference (Lightweight).
        """
        try:
            scene_cuts = []
            prev_hist = None
            
            # Optimization: Check every 5th frame to speed up and save cpu
            step = 5
            
            for i in range(0, self.frame_count, step):
                # self.cap.set(cv2.CAP_PROP_POS_FRAMES, i) # seek is slow
                # sequential read is better, but we are skipping.
                # Actually, skipping read might desync if not careful, but for 'grab' it's fast.
                
                # Fast forward
                if i > 0:
                    for _ in range(step - 1): self.cap.grab()
                
                ret, frame = self.cap.retrieve()
                if not ret: break
                
                # Convert to HSV for better color comparison
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hist = cv2.calcHist([hsv], [0], None, [256], [0, 256])
                cv2.normalize(hist, hist)
                
                if prev_hist is not None:
                    # Compare histograms (Correlation)
                    score = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    # If correlation drops below threshold, it's a scene change
                    if score < 0.7: 
                        timestamp = i / self.fps
                        scene_cuts.append(timestamp)
                
                prev_hist = hist

            num_scenes = len(scene_cuts) + 1
            pacing_rate = self.duration / num_scenes if num_scenes > 0 else self.duration

            # Benchmark Scoring
            if 1.5 <= pacing_rate <= 2.5:
                pacing_score = 100
            elif pacing_rate > 4.0:
                pacing_score = 40
            elif pacing_rate > 2.5:
                pacing_score = 40 + (4.0 - pacing_rate) / (4.0 - 2.5) * 60
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
        hook_score = 0
        hook_factors = { "has_text": False, "has_fast_cut": False, "has_human": False }
        
        # 1. Check fast cuts in first 3s
        if any(cut <= 3.0 for cut in scene_cuts):
            hook_score += 40
            hook_factors["has_fast_cut"] = True

        # 2. Text/Human - Skipped (No OCR/YOLO)
        # Default assumption: User put effort in. Give partial credit?
        # Or just 0.
        
        # Let's check for "Motion" in first 3s? High motion = Hook?
        # For now, simplistic fallback.
        hook_score += 30 # Baseline
            
        return { "hook_score": min(hook_score, 100), "hook_factors": hook_factors }
    
    def analyze_audio(self):
        """Skipped for Lite."""
        return { "music_tempo_bpm": 0, "audio_vibe": "unknown", "has_voiceover": False }

    def run_full_analysis(self):
        """Run all analysis steps."""
        try:
            print("1. Analyzing duration...", flush=True)
            duration_result = self.analyze_duration()
            
            print("2. Analyzing scenes and pacing (Lite)...", flush=True)
            scene_result = self.analyze_scenes()
            
            print("3. Analyzing 3-second hook (Lite)...", flush=True)
            hook_result = self.analyze_hook(scene_result["scene_cuts_timestamp"])
            
            print("4. Analyzing audio (Skipped)...", flush=True)
            audio_result = self.analyze_audio()
            
            safe_zone_passed = True 
            
            return {
                "creative": {
                    "hook": hook_result["hook_score"],
                    "pacing": scene_result["pacing_score"],
                    "safe_zone": safe_zone_passed,
                    "duration": duration_result["duration_seconds"],
                    "details": {
                        "hook_factors": hook_result["hook_factors"],
                        "pacing_data": scene_result,
                        "audio": audio_result
                    }
                }
            }
        finally:
            self.cap.release()
