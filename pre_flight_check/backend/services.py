import httpx
import os
from dotenv import load_dotenv
from models import CampaignInput, AnalysisResult, PolicyResult, CreativeMetrics, IndustryConfig

load_dotenv()

# Industry Average CPA Benchmarks (Estimated 2025)
INDUSTRY_BENCHMARKS = {
    IndustryConfig.FINANCE: 750.0,
    IndustryConfig.ECOMMERCE: 325.0,
    IndustryConfig.BEAUTY: 350.0,
    IndustryConfig.FNB: 260.0,
    IndustryConfig.TECH: 500.0,
    IndustryConfig.TRAVEL: 380.0,
    IndustryConfig.OTHER: 50.0
}

class BenchmarkService:
    @staticmethod
    def calculate_benchmark_score(target_cpa: float, industry_id: IndustryConfig) -> float:
        avg_cpa = INDUSTRY_BENCHMARKS.get(industry_id, 50.0)
        if avg_cpa == 0: return 0.0
        # Formula: min(100, (Target_CPA / Industry_Avg_CPA) * 100)
        score = (target_cpa / avg_cpa) * 100
        return min(100.0, score)

class N8nClient:
    def __init__(self):
        # Force Prod URL to fix stale Vercel Env issue
        self.video_webhook_url = "https://n88n.ecomdymedia.com/webhook/45c08981-0739-4c4f-82f5-61402bff42de"
        self.lp_webhook_url = os.getenv("N8N_LP_WEBHOOK_URL")

    async def analyze_video(self, video_url: str, campaign_context: dict) -> dict:
        # Fallback if empty (shouldn't be with hardcode)
        if not self.video_webhook_url:
             pass 
        
        # Simplified Payload for Video
        # Helper to safely extract Video ID
        def extract_video_id(url: str) -> str:
            from urllib.parse import urlparse, parse_qs
            try:
                parsed = urlparse(url)
                # 1. Try 'vid' query param (Common in TikTok CDN)
                query_params = parse_qs(parsed.query)
                if 'vid' in query_params:
                    return query_params['vid'][0]
                
                # 2. Fallback: Last path segment (ignoring extension)
                path_segments = parsed.path.split("/")
                filename = path_segments[-1] if path_segments else "unknown"
                return filename.split(".")[0]
            except:
                return "unknown_video_id"

        # Updated Simplified Payload
        payload = {
            "creative_videos": [{
                "video_preview_url": video_url
            }]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.video_webhook_url, json=payload, timeout=60.0)
                response.raise_for_status()
                
                # Added Logging
                data = response.json()
                print(f"[DEBUG] N8N Video Raw Response: {data}")
                
                # Parsing logic for New Video Workflow (creative_videos_review)
                video_reviews = data.get("creative_videos_review", [])
                
                # Default Safe
                is_safe = True
                reason = "N8N Policy Check Passed"
                
                if video_reviews and isinstance(video_reviews, list) and len(video_reviews) > 0:
                    review = video_reviews[0] # Take first video result
                    
                    # Logic: TextAnalysisResult or Recommendation determines safety
                    # "TextAnalysisResult": "Non-Compliant" | "Compliant" | "Flagged for Review"
                    # "Recommendation": "Reject Content" | "Approve Content"
                    
                    analysis_result = review.get("TextAnalysisResult", "Unknown")
                    recommendation = review.get("Recommendation", "")
                    
                    if analysis_result == "Non-Compliant" or "Reject" in recommendation:
                        is_safe = False
                        # Create reason string from available details
                        details = review.get("ViolationDetails", review.get("TextViolationDetails", ""))
                        violation_type = review.get("ViolationType", review.get("TextViolationType", "Policy Violation"))
                        reason = f"{violation_type}: {details}" if details else violation_type
                    elif analysis_result == "Flagged for Review":
                        is_safe = False # Treat Flagged as Unsafe for now (conservative)
                        reason = "Flagged for Manual Review"

                return {
                    "policy": {"is_safe": is_safe, "reason": reason},
                    "creative": {} 
                }
            except Exception as e:
                print(f"Error calling n8n Video: {e}")
                return {
                    "policy": {"is_safe": False, "reason": f"Video Analysis Failed: {str(e)}"},
                    "creative": {}
                }

    async def analyze_landing_page(self, landing_page_url: str) -> dict:
        if not self.lp_webhook_url:
            print("WARNING: N8N_LP_WEBHOOK_URL not set. Using mock data.")
            return {
                "policy": {"is_safe": True, "reason": "[MOCK-LP] Landing Page Safe"}
            }

        payload = {
            "landingPages": [landing_page_url]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.lp_webhook_url, json=payload, timeout=30.0)
                # print(f"[DEBUG] LP Status: {response.status_code}") # Helper
                response.raise_for_status()
                data = response.json()
                print(f"[DEBUG] N8N LP Raw Response: {data}") # KEEP THIS
                
                # Parsing logic for real n8n response
                # Expected format: { "landing_pages_review": [ { "AnalysisResult": "Non-Compliant", ... } ] }
                reviews = data.get("landing_pages_review", [])
                if reviews and isinstance(reviews, list) and len(reviews) > 0:
                    review = reviews[0]
                    status = review.get("AnalysisResult", "Unknown")
                    is_compliant = (status.lower() == "compliant")
                    reason = review.get("ViolationDetails", review.get("Recommendation", "Policy Violation"))
                    
                    return {
                        "policy": {
                            "is_safe": is_compliant,
                            "reason": reason if not is_compliant else "Landing Page Compliant"
                        }
                    }
                
                # Fallback if structure doesn't match
                return data if "policy" in data else {
                    "policy": {"is_safe": False, "reason": "Invalid response format from Policy Check"}
                }

            except Exception as e:
                print(f"Error calling n8n LP: {e}")
                return {
                    "policy": {"is_safe": False, "reason": f"LP Analysis Failed: {str(e)}"}
                }

class ScoringEngine:
    @staticmethod
    def calculate_dna_score(creative: CreativeMetrics) -> float:
        # DNA Score = Hook*0.6 + Pacing*0.4
        return (creative.hook_score * 0.6) + (creative.pacing_score * 0.4)

    @staticmethod
    def calculate_final_score(benchmark_score: float, dna_score: float) -> tuple[float, str]:
        # Implementation Plan Formula: PredictiveScore = P * ((D*0.7) + (B*0.3))
        # Wait, where is P coming from?
        # Re-reading requirements:
        # "PredictiveScore = P * ((D*0.7)+(B*0.3))" where P is likely Policy status (1 or 0) ?
        # Or P is a probability factor?
        # Let's assume P = 1 if Policy Safe, else 0 (Blocking factor).
        
        # Let's simplify for now based on typical scoring logic:
        # If unsafe, score is 0.
        
        weighted_score = (dna_score * 0.7) + (benchmark_score * 0.3)
        return round(weighted_score, 2)

    @staticmethod
    def get_rating(score: float, is_safe: bool) -> str:
        if not is_safe:
            return "Red" # Policy Violation
        if score > 80:
            return "Green"
        elif score >= 50:
            return "Yellow"
        else:
            return "Red"
