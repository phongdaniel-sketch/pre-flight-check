from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from typing import Optional

from models import CampaignInput, IndustryConfig, AnalysisResult, PolicyResult, CreativeMetrics
from services import BenchmarkService, N8nClient, ScoringEngine

app = FastAPI(title="Pre-flight Check Tool API")

# Vercel Path Fix: Ensure current directory is in sys.path for local imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Mount (to serve uploaded videos and frontend)
# On Vercel, current working directory is usually the root.
BASE_DIR = os.getcwd() 
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Vercel Read-Only Fix: Use /tmp for uploads
UPLOAD_DIR = "/tmp/uploads" if os.getenv("VERCEL") else os.path.join(STATIC_DIR, "uploads")

try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception:
    pass 

# Only mount static if it exists (prevent crash)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found", "path": index_path}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Pre-flight Check Backend", "upload_dir": UPLOAD_DIR}

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_campaign(
    industry_id: IndustryConfig = Form(...),
    target_cpa: float = Form(...),
    country: str = Form(...),
    budget: float = Form(...),
    landing_page_url: str = Form(...),
    audience_age: Optional[str] = Form(None),
    audience_gender: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None),
    video_url_input: Optional[str] = Form(None)
):
    video_url = ""
    
    # Logic: Prioritize URL input if provided
    if video_url_input and video_url_input.strip():
        video_url = video_url_input.strip()
    elif video_file:
        # 1. Save Video File Locally (or to TMP)
        file_id = str(uuid.uuid4())
        file_extension = video_file.filename.split(".")[-1]
        
        # Use configurable upload path
        save_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_extension}")
        
        try:
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(video_file.file, buffer)
            
            # Construct "Public" URL
            # NOTE: On Vercel, /tmp is NOT publicly accessible via URL.
            # We must warn the user or use a cloud storage.
            # For MVP, we pass a fake URL if on Vercel, assuming n8n can't reach it anyway unless we upload.
            if os.getenv("VERCEL"):
                # Workaround: Ensure n8n client handles local file path if possible? No.
                # Warning: Vercel Uploads won't work with external n8n.
                video_url = f"file://{save_path}" 
            else:
                video_url = f"http://localhost:8000/static/uploads/{file_id}.{file_extension}"
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Please provide either a video file or a video URL.")

    # 2. Benchmark Calc
    benchmark_score = BenchmarkService.calculate_benchmark_score(target_cpa, industry_id)

    # 3. Call n8n for Analysis
    n8n_client = N8nClient()
    campaign_context = {
        "industry": industry_id,
        "country": country,
        "target_cpa": target_cpa,
        "budget": budget,
        "lp": landing_page_url,
        "audience_age": audience_age,
        "audience_gender": audience_gender
    }
    
    n8n_result = await n8n_client.analyze_creative(video_url, campaign_context)
    
    # 4. Parse n8n Results
    policy_data = n8n_result.get("policy", {})
    creative_data = n8n_result.get("creative", {})
    
    policy_res = PolicyResult(
        is_safe=policy_data.get("is_safe", False),
        reason=policy_data.get("reason", "Unknown Error")
    )
    
    creative_res = CreativeMetrics(
        hook_score=float(creative_data.get("hook", 0)),
        pacing_score=float(creative_data.get("pacing", 0)),
        safe_zone=bool(creative_data.get("safe_zone", False)),
        duration_seconds=float(creative_data.get("duration", 0))
    )

    # 5. Final Scoring
    dna_score = ScoringEngine.calculate_dna_score(creative_res)
    predictive_score = 0.0
    
    if policy_res.is_safe:
        # P = 1
        predictive_score = ScoringEngine.calculate_final_score(benchmark_score, dna_score)
    else:
        # P = 0, Score is 0 (or very low)
        predictive_score = 0.0

    final_rating = ScoringEngine.get_rating(predictive_score, policy_res.is_safe)
    
    return AnalysisResult(
        benchmark_score=benchmark_score,
        policy_check=policy_res,
        creative_metrics=creative_res,
        dna_score=dna_score,
        predictive_score=predictive_score,
        final_rating=final_rating,
        message=f"Campaign analyzed. Rating: {final_rating}"
    )

@app.post("/api/webhook/callback")
async def n8n_callback(data: dict):
    print("\n[CALLBACK RECEIVED] Data from n8n:")
    import json
    print(json.dumps(data, indent=2))
    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
