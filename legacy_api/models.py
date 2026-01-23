from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class IndustryConfig(str, Enum):
    FINANCE = "FIN"
    ECOMMERCE = "ECOMM"
    BEAUTY = "BEAUTY"
    FNB = "FNB"
    TECH = "TECH"
    TRAVEL = "TRAVEL"
    OTHER = "OTHER"

class CampaignInput(BaseModel):
    industry_id: IndustryConfig
    target_cpa: float
    country: str
    audience_age: Optional[str] = None
    audience_gender: Optional[str] = None
    budget: float
    landing_page_url: str

class CreativeMetrics(BaseModel):
    hook_score: float
    pacing_score: float
    safe_zone: bool
    duration_seconds: float

class PolicyResult(BaseModel):
    is_safe: bool
    reason: Optional[str] = None

class AnalysisResult(BaseModel):
    benchmark_score: float
    policy_check: PolicyResult
    creative_metrics: CreativeMetrics
    dna_score: float
    predictive_score: float
    final_rating: str  # Green, Yellow, Red
    message: str
