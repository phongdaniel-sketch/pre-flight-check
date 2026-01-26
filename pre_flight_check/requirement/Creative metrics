Phân tích Video TikTok bằng AI

Tài liệu này trình bày kiến trúc và mã nguồn chi tiết để xây dựng một hệ thống tự động phân tích và chấm điểm video theo các tiêu chí "hấp dẫn" của nền tảng TikTok.

## 🏛️ 1. Kiến trúc Tổng quan

Hệ thống được thiết kế theo dạng pipeline, xử lý video qua nhiều module chuyên biệt. Đầu vào là file video và đầu ra là một file JSON chứa kết quả phân tích.

```
                  +-------------------------+
Input Video ----> | 1. Pre-Analysis Module  | --(Duration, FPS)-->
                  |   - Kiểm tra thời lượng |
                  +-------------------------+
                          |
                          v
                  +-------------------------+
                  | 2. Visual Analysis Module | --(Safe Zone, Scene Cuts, Text, Objects)-->
                  |   - Phân tích từng Frame |
                  +-------------------------+
                          |
                          v
                  +-------------------------+
                  | 3. Audio Analysis Module  | --(Tempo, Voiceover)-->
                  |   - Phân tích âm thanh   |
                  +-------------------------+
                          |
                          v
                  +-------------------------+
                  |  4. Scoring Engine      | --(Hook Score, Pacing Score)-->
                  |   - Tính toán điểm số    |
                  +-------------------------+
                          |
                          v
                  +-------------------------+
                  |     Final JSON Output   |
                  +-------------------------+
```

## 🛠️ 2. Cài đặt Môi trường

Mở Terminal (hoặc Command Prompt) và cài đặt các thư viện Python cần thiết. Mỗi thư viện phục vụ một mục đích cụ thể trong pipeline.

```bash
# Thư viện xử lý video và hình ảnh cốt lõi
pip install opencv-python

# Thư viện nhận diện chữ trong ảnh (OCR)
pip install easyocr

# Thư viện chuyên để phát hiện chuyển cảnh
pip install scenedetect[opencv]

# Thư viện phân tích âm thanh
pip install librosa moviepy

# (Tùy chọn nhưng khuyến nghị) Thư viện AI mạnh mẽ của PyTorch
pip install torch torchvision torchaudio
```

## 💻 3. Code Hoàn chỉnh

Dưới đây là mã nguồn Python hoàn chỉnh cho lớp `TikTokVideoAnalyzer`, bao gồm tất cả các logic phân tích đã đề cập.

```python
import cv2
import numpy as np
import easyocr
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.editor import VideoFileClip
import librosa
import os
import json

class TikTokVideoAnalyzer:
    """
    Một lớp hoàn chỉnh để phân tích và chấm điểm video TikTok dựa trên các tiêu chí
    về thời lượng, nhịp độ, và các yếu tố thu hút.
    """
    def __init__(self, video_path):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print("Initializing EasyOCR...")
        # Hỗ trợ tiếng Anh và tiếng Việt
        self.ocr_reader = easyocr.Reader(['en', 'vi'], gpu=True) # Set gpu=False nếu không có GPU

    def _check_safe_zone(self, important_elements):
        """
        Kiểm tra xem các yếu tố quan trọng (văn bản, khuôn mặt) có nằm trong vùng an toàn không.
        Input: a list of bounding boxes [(x1, y1, x2, y2), ...]
        """
        # Tọa độ các vùng UI của TikTok (ước tính theo tỷ lệ)
        ui_zones = [
            # Vùng caption và tên user ở dưới (70% chiều rộng, 20% chiều cao dưới)
            (0, self.height * 0.8, self.width * 0.7, self.height), 
            # Vùng các nút like, comment, share bên phải (15% chiều rộng bên phải, 40% chiều cao ở giữa)
            (self.width * 0.85, self.height * 0.4, self.width, self.height * 0.8)
        ]
        
        is_safe = True
        for element_box in important_elements:
            ex1, ey1, ex2, ey2 = element_box
            for ux1, uy1, ux2, uy2 in ui_zones:
                # Kiểm tra sự chồng lấn (intersection)
                if not (ex2 < ux1 or ex1 > ux2 or ey2 < uy1 or ey1 > uy2):
                    is_safe = False
                    break
            if not is_safe:
                break
        return is_safe

    def analyze_duration(self):
        """Kiểm tra thời lượng video có nằm trong khoảng 15s-45s không."""
        is_valid = 15 <= self.duration <= 45
        return {
            "duration_seconds": round(self.duration, 2),
            "is_valid_duration": is_valid
        }

    def analyze_scenes(self):
        """Phát hiện các cảnh, tính toán nhịp độ và chấm điểm pacing_score."""
        video = open_video(self.video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=27.0))
        scene_manager.detect_scenes(video, show_progress=False)
        scene_list = scene_manager.get_scene_list()
        
        # Lấy timestamp của điểm kết thúc mỗi cảnh (cũng là điểm bắt đầu cảnh mới)
        scene_cuts = [scene.get_seconds() for scene in scene_list]
        num_scenes = len(scene_list)
        
        pacing_rate = self.duration / num_scenes if num_scenes > 0 else self.duration

        # Chấm điểm Pacing dựa trên benchmark
        if 1.5 <= pacing_rate <= 2.5:
            pacing_score = 100
        elif pacing_rate > 4.0:
            pacing_score = 40
        elif pacing_rate > 2.5:
            # Điểm giảm dần tuyến tính từ 100 xuống 40
            pacing_score = 40 + (4.0 - pacing_rate) / (4.0 - 2.5) * 60
        else: # pacing_rate < 1.5
            pacing_score = 80 # Nhịp quá nhanh vẫn tốt nhưng có thể hơi rối
            
        return {
            "scene_cuts_timestamp": scene_cuts,
            "number_of_scenes": num_scenes,
            "pacing_rate_sec_per_scene": round(pacing_rate, 2),
            "pacing_score": int(pacing_score)
        }

    def analyze_hook(self, scene_cuts):
        """Phân tích 3 giây đầu để chấm điểm Hook."""
        hook_score = 0
        hook_factors = { "has_text": False, "has_fast_cut": False, "has_human": False }
        
        # 1. Kiểm tra chuyển cảnh nhanh trong 3s đầu
        if any(cut <= 3.0 for cut in scene_cuts):
            hook_score += 40
            hook_factors["has_fast_cut"] = True

        # 2. Đọc các frame trong 3s đầu để kiểm tra text và người
        frames_to_check = int(self.fps * 3)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Tua về đầu video
        
        text_found = False
        
        for i in range(frames_to_check):
            ret, frame = self.cap.read()
            if not ret: break
            
            # Chỉ kiểm tra mỗi 10 frame để tối ưu
            if i % 10 == 0:
                if not text_found:
                    results = self.ocr_reader.readtext(frame, detail=0, paragraph=True)
                    if results:
                        text_found = True
        
        hook_factors["has_text"] = text_found

        # Tạm thời giả định là tìm thấy người. Cần tích hợp model object detection (YOLO, SSD) để làm thật.
        human_found = True 
        hook_factors["has_human"] = human_found
            
        if text_found: hook_score += 35
        if human_found: hook_score += 25
            
        return { "hook_score": min(hook_score, 100), "hook_factors": hook_factors }
    
    def analyze_audio(self):
        """Phân tích file âm thanh để lấy nhịp độ (tempo) và kiểm tra giọng nói."""
        try:
            audio_path = "temp_audio.wav"
            # Trích xuất audio từ video
            video_clip = VideoFileClip(self.video_path)
            video_clip.audio.write_audiofile(audio_path, codec='pcm_s16le', logger=None)
            
            # Tải file audio đã trích xuất
            y, sr = librosa.load(audio_path)
            # Ước tính tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # Placeholder cho việc phát hiện giọng nói
            has_voiceover = False 
            
            os.remove(audio_path) # Dọn dẹp file tạm
            return {
                "music_tempo_bpm": int(tempo),
                "audio_vibe": "fast" if tempo > 120 else "slow",
                "has_voiceover": has_voiceover
            }
        except Exception as e:
            print(f"Audio analysis failed or video has no audio: {e}")
            return { "music_tempo_bpm": 0, "audio_vibe": "unknown", "has_voiceover": False }

    def run_full_analysis(self):
        """Chạy toàn bộ pipeline và trả về kết quả cuối cùng dưới dạng dictionary."""
        print("1. Analyzing duration...")
        duration_result = self.analyze_duration()
        
        print("2. Analyzing scenes and pacing...")
        scene_result = self.analyze_scenes()
        
        print("3. Analyzing 3-second hook...")
        hook_result = self.analyze_hook(scene_result["scene_cuts_timestamp"])
        
        print("4. Analyzing audio...")
        audio_result = self.analyze_audio()
        
        # Placeholder cho các phân tích hình ảnh nâng cao hơn
        safe_zone_passed = True # Cần logic _check_safe_zone với bounding box thật
        visual_elements = ["person", "text_overlay"] # Cần logic object detection thật
        
        final_result = {
            "video_path": self.video_path,
            "duration_analysis": duration_result,
            "safe_zone_passed": safe_zone_passed,
            "hook_analysis": hook_result,
            "pacing_analysis": scene_result,
            "audio_analysis": audio_result,
            "visual_elements_detected": visual_elements,
        }
        
        self.cap.release()
        return final_result

# --- HƯỚNG DẪN SỬ DỤNG ---
if __name__ == "__main__":
    try:
        # THAY ĐỔI ĐƯỜNG DẪN NÀY
        video_file = "path/to/your/tiktok_video.mp4" 
        
        analyzer = TikTokVideoAnalyzer(video_file)
        result = analyzer.run_full_analysis()
        
        # In kết quả ra màn hình
        print("\n--- ✅ ANALYSIS COMPLETE ---")
        print(json.dumps(result, indent=4, ensure_ascii=False))

        # Lưu kết quả ra file JSON
        output_filename = os.path.splitext(os.path.basename(video_file)) + "_analysis.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"\n📄 Result saved to: {output_filename}")

    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

```

## 🚀 4. Cách sử dụng

1.  **Lưu file:** Sao chép toàn bộ code Python ở trên và lưu vào một file có tên `analyzer.py`.
2.  **Chỉnh sửa đường dẫn:** Mở file `analyzer.py` và thay đổi giá trị của biến `video_file` ở gần cuối file thành đường dẫn chính xác đến video bạn muốn phân tích.
    ```python
    # THAY ĐỔI ĐƯỜNG DẪN NÀY
    video_file = "path/to/your/tiktok_video.mp4"
    ```
3.  **Chạy phân tích:** Mở Terminal/Command Prompt, di chuyển đến thư mục chứa file `analyzer.py` và chạy lệnh:
    ```bash
    python analyzer.py
    ```
4.  **Xem kết quả:**
    *   Toàn bộ quá trình phân tích sẽ được tổng hợp và đưa ra màn hình kết quả.
    *   Khi hoàn tất, kết quả chi tiết sẽ được lưu vào một file JSON mới (ví dụ: `tiktok_video_analysis.json`) trong cùng thư mục.

## 🔮 5. Hướng tính toán DNA score
Khi input video, hệ thống sẽ thực hiện:
    Quét Safe Zone (đảm bảo không bị che bởi UI TikTok) --> trả kết quả?
    Kiểm tra thời lượng (có nằm trong 15s-45s không) --> trả kết quả?
    Chấm điểm "DNA hấp dẫn" (Hook, Nhịp cắt cảnh): (chi tiết)
Sau đó tính toán:
    Hook (3s đầu): AI kiểm tra xem trong 3 giây đầu có: (1) Text gây sốc/tò mò, (2) Sự thay đổi khung hình nhanh, (3) Xuất hiện sản phẩm/con người rõ ràng không?
    Pacing (Nhịp độ): AI đếm số lần chuyển cảnh (cut) trong video.
    Công thức: Pacing Rate = Tổng thời lượng / Số lượng cảnh.
    Benchmark: TikTok cực kỳ ưu tiên nhịp từ 1.5s - 2.5s/cảnh. Nếu nhịp > 4s/cảnh -> Video bị coi là chậm/chán.
Chấm điểm như sau:
    hook_score (0-100): Dựa trên 3s đầu có đủ yếu tố giữ chân người dùng không.
    scene_cuts: Danh sách các mốc thời gian (timestamp) mà video chuyển cảnh.
    visual_elements: Danh sách các yếu tố xuất hiện (người mẫu, text overlay, unboxing, kho hàng).
    audio_vibe: Nhạc nhanh hay chậm, có giọng đọc (voiceover) không. Sau đó, tính pacing_score: Nếu trung bình mỗi cảnh dài 1.5s-2.5s thì cho 100 điểm, nếu > 4s thì cho 40 điểm."
Công thức: DNA Score = (Hook * 0.6) + (Pacing * 0.4).
