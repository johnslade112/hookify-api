from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class GenerateRequest(BaseModel):
    niche: str = Field(..., examples=["emagrecimento", "ganhar dinheiro com IA"])
    platform: str = Field(..., examples=["tiktok","reels","shorts"])
    tone: str = Field(..., examples=["direto","motivacional","educativo","storytelling"])
    language: str = Field("pt", examples=["pt","en","es"])
    product_name: Optional[str] = None
    problems: Optional[List[str]] = None
    call_to_action: Optional[str] = None
    variants: int = 3
    hashtags_count: int = 5

class GenerateResponse(BaseModel):
    hooks: List[str]
    captions: List[str]
    hashtags: List[str]

class ShortenRequest(BaseModel):
    url: HttpUrl
    utm_source: Optional[str] = "tiktok"
    utm_medium: Optional[str] = "organic"
    utm_campaign: Optional[str] = "default"

class ShortenResponse(BaseModel):
    code: str
    short_url: str
    target_url: str
    clicks: int

class LinkAnalytics(BaseModel):
    code: str
    url: str
    clicks: int
