from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import sys
import traceback
from typing import Optional

# Ensure current directory is in sys.path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Define app
app = FastAPI(title="Pre-flight Check Tool API (Local)")

try:
    # Attempt Imports
    from models import CampaignInput, IndustryConfig, AnalysisResult, PolicyResult, CreativeMetrics
    from services import BenchmarkService, N8nClient, ScoringEngine
    # Import Local Analyzer (copied from api/creative_analyzer.py)
    from creative_analyzer import TikTokVideoAnalyzer

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static Mount Logic
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Assuming static is sibling to backend folder or in root?
    # In Vercel api/index.py: BASE_DIR = parent of api.
    # Here: pre_flight_check/backend/main.py. Parent is pre_flight_check. 
    # User root has 'static'. 
    # Let's try to find 'static' in root: ../../static
    ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR)) # ../../
    STATIC_DIR = os.path.join(ROOT_DIR, "static")
    if not os.path.exists(STATIC_DIR):
        # Fallback to local static if exists
        STATIC_DIR = os.path.join(BASE_DIR, "static")

    # Vercel / Serverless Environment Check
    # On Vercel, the filesystem is read-only except for /tmp
    IS_VERCEL = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    
    if IS_VERCEL:
        UPLOAD_DIR = "/tmp"
    else:
        UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception:
        pass

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
        return {"status": "ok", "service": "Pre-flight Check Backend (Local)", "upload_dir": UPLOAD_DIR}

    @app.post("/api/analyze", response_model=AnalysisResult)
    async def analyze_campaign(
        industry_id: IndustryConfig = Form(...),
        target_cpa: float = Form(...),
        country: str = Form(...),
        budget: float = Form(...),
        landing_page_url: Optional[str] = Form(None),
        audience_age: Optional[str] = Form(None),
        audience_gender: Optional[str] = Form(None),
        video_file: Optional[UploadFile] = File(None),
        video_url_input: Optional[str] = Form(None)
    ):
        import asyncio
        video_url = ""
        has_video = False
        
        # 1. Determine Input Types
        if video_url_input and video_url_input.strip():
            video_url = video_url_input.strip()
            has_video = True
        elif video_file and video_file.filename: # FIX: Check filename
            has_video = True
            file_id = str(uuid.uuid4())
            file_extension = video_file.filename.split(".")[-1]
            local_save_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_extension}")
            # expose for later use
            video_url = "" 
            
            try:
                with open(local_save_path, "wb") as buffer:
                    shutil.copyfileobj(video_file.file, buffer)
                
                # Local URL construction
                video_url = f"http://localhost:8000/static/uploads/{file_id}.{file_extension}"
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")

        if not has_video and not landing_page_url:
            raise HTTPException(status_code=400, detail="Please provide either a Video or a Landing Page URL.")

    # 2. Benchmark Calc
        benchmark_score = BenchmarkService.calculate_benchmark_score(target_cpa, industry_id)

        # 3. Parallel Analysis (Video + LP)
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

        # --- VIDEO PREPARATION ---
        local_video_path = None
        if has_video:
            # If we have a URL but no local file (video_file is None), we must download it
            if video_url_input and video_url_input.strip() and not video_file:
                 try:
                     print(f"Downloading video from {video_url}...", flush=True)
                     import httpx as request_lib
                     async with request_lib.AsyncClient() as dl_client:
                         r = await dl_client.get(video_url, follow_redirects=True)
                         if r.status_code == 200:
                             file_id = str(uuid.uuid4())
                             ext = "mp4"
                             local_video_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
                             with open(local_video_path, "wb") as f:
                                 f.write(r.content)
                             print(f"Downloaded to {local_video_path}", flush=True)
                         else:
                             print(f"Failed to download video: {r.status_code}", flush=True)
                 except Exception as e:
                     print(f"Download error: {e}", flush=True)
            
            if 'local_save_path' in locals() and local_save_path:
                 local_video_path = local_save_path

        tasks = []
        if has_video:
            tasks.append(n8n_client.analyze_video(video_url, campaign_context))
        else:
            async def no_video(): return None
            tasks.append(no_video())

        if landing_page_url:
            tasks.append(n8n_client.analyze_landing_page(landing_page_url))
        else:
            async def no_lp(): return None
            tasks.append(no_lp())

        results = await asyncio.gather(*tasks)
        video_result, lp_result = results[0], results[1]

        # --- LOCAL CREATIVE ANALYSIS ---
        local_creative_data = {}
        if has_video and local_video_path and os.path.exists(local_video_path):
            try:
                print(f"Starting Local Analysis on {local_video_path}...", flush=True)
                analyzer = TikTokVideoAnalyzer(local_video_path)
                analysis_output = analyzer.run_full_analysis()
                local_creative_data = analysis_output.get("creative", {})
                print("Local Analysis Complete", flush=True)
            except Exception as e:
                print(f"Local Analysis Failed: {e}", flush=True)
                local_creative_data = {}
        else:
            if has_video:
                print(f"Skipping Local Analysis: local_video_path={local_video_path}", flush=True)

        # 4. Aggregation Logic
        video_policy_safe = True
        video_policy_reason = ""
        creative_data = local_creative_data # Use LOCAL data

        if video_result:
            p = video_result.get("policy", {})
            video_policy_safe = p.get("is_safe", False)
            video_policy_reason = p.get("reason", "")
        
        lp_policy_safe = True
        lp_policy_reason = ""
        
        if lp_result:
            p = lp_result.get("policy", {})
            lp_policy_safe = p.get("is_safe", False)
            lp_policy_reason = p.get("reason", "")

        # Combine Policy
        final_is_safe = video_policy_safe and lp_policy_safe
        final_reasons = []
        if not video_policy_safe: final_reasons.append(f"Video: {video_policy_reason}")
        if not lp_policy_safe: final_reasons.append(f"LP: {lp_policy_reason}")
        
        # Creative Metrics
        has_creative_metrics = bool(creative_data)
        creative_res = CreativeMetrics(
            hook_score=float(creative_data.get("hook", 0)),
            pacing_score=float(creative_data.get("pacing", 0)),
            safe_zone=bool(creative_data.get("safe_zone", False)),
            duration_seconds=float(creative_data.get("duration", 0))
        )

        # 5. Final Scoring
        dna_score = 0.0
        if has_creative_metrics:
            dna_score = ScoringEngine.calculate_dna_score(creative_res)
        
        predictive_score = 0.0
        if final_is_safe:
            predictive_score = ScoringEngine.calculate_final_score(benchmark_score, dna_score)
        else:
            predictive_score = 0.0

        final_rating = ScoringEngine.get_rating(predictive_score, final_is_safe)
        
        reason_str = "; ".join(final_reasons) if final_reasons else "Policy Safe"

        return AnalysisResult(
            benchmark_score=benchmark_score,
            policy_check=PolicyResult(is_safe=final_is_safe, reason=reason_str),
            creative_metrics=creative_res,
            dna_score=dna_score,
            predictive_score=predictive_score,
            final_rating=final_rating,
            message=f"Analysis Complete. {reason_str}"
        )

    @app.post("/api/webhook/callback")
    async def n8n_callback(data: dict):
        print("\n[CALLBACK RECEIVED] Data from n8n:")
        import json
        print(json.dumps(data, indent=2))
        return {"status": "received"}

except Exception as e:
    import traceback
    error_trace = traceback.format_exc()
    error_msg = str(e)
    
    @app.get("/{catchall:path}")
    def error_handler(catchall: str):
        return {
            "status": "Boot Error",
            "error_type": type(e).__name__,
            "error_message": error_msg,
            "trace": error_trace
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
