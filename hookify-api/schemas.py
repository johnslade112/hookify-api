from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List, Optional
from datetime import datetime
from models import PlanType, GenerationType

# ==================== AUTH SCHEMAS ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== SUBSCRIPTION SCHEMAS ====================

class SubscriptionResponse(BaseModel):
    id: int
    plan_type: PlanType
    monthly_quota: int
    used_quota: int
    remaining_quota: int
    is_active: bool
    start_date: datetime
    end_date: Optional[datetime]
    
    class Config:
        from_attributes = True

class UpgradeRequest(BaseModel):
    plan_type: PlanType

# ==================== GENERATION SCHEMAS (V1 - Legacy) ====================

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

# ==================== GENERATION SCHEMAS (V2 - AI Powered) ====================

class HookGenerateRequest(BaseModel):
    niche: str = Field(..., description="Nicho do conteúdo", examples=["fitness", "finanças"])
    topic: str = Field(..., description="Tópico específico", examples=["perder barriga", "investir em ações"])
    tone: str = Field("direto", description="Tom do hook", examples=["direto", "motivacional", "educativo", "storytelling"])
    platform: str = Field("tiktok", examples=["tiktok", "reels", "shorts"])
    variants: int = Field(3, ge=1, le=10, description="Número de variações")

class HookGenerateResponse(BaseModel):
    hooks: List[str]
    quota_remaining: int

class CaptionGenerateRequest(BaseModel):
    niche: str = Field(..., examples=["emagrecimento"])
    topic: str = Field(..., examples=["dieta low carb"])
    tone: str = Field("direto", examples=["direto", "motivacional", "educativo"])
    product_name: Optional[str] = None
    call_to_action: Optional[str] = Field(None, examples=["Comenta 'quero' para receber o guia"])
    max_length: int = Field(150, ge=50, le=300, description="Tamanho máximo em palavras")
    variants: int = Field(3, ge=1, le=10)

class CaptionGenerateResponse(BaseModel):
    captions: List[str]
    quota_remaining: int

class HashtagGenerateRequest(BaseModel):
    niche: str = Field(..., examples=["fitness"])
    topic: str = Field(..., examples=["treino em casa"])
    platform: str = Field("tiktok", examples=["tiktok", "instagram", "youtube"])
    count: int = Field(10, ge=5, le=30, description="Número de hashtags")
    include_trending: bool = Field(True, description="Incluir hashtags em alta")

class HashtagGenerateResponse(BaseModel):
    hashtags: List[str]
    quota_remaining: int

class EmotionAnalyzeRequest(BaseModel):
    text: str = Field(..., description="Texto ou descrição do vídeo para análise")
    context: Optional[str] = Field(None, description="Contexto adicional")

class EmotionAnalyzeResponse(BaseModel):
    primary_emotion: str = Field(..., description="Emoção predominante", examples=["alegria", "surpresa", "medo", "raiva", "tristeza", "neutro"])
    confidence: float = Field(..., ge=0, le=1, description="Confiança da análise")
    emotions_breakdown: dict = Field(..., description="Distribuição de todas as emoções")
    suggestions: List[str] = Field(..., description="Sugestões para melhorar o engajamento")
    quota_remaining: int

class CompleteGenerateRequest(BaseModel):
    niche: str
    topic: str
    tone: str = "direto"
    platform: str = "tiktok"
    product_name: Optional[str] = None
    call_to_action: Optional[str] = None
    analyze_emotion: bool = Field(False, description="Incluir análise de emoção")

class CompleteGenerateResponse(BaseModel):
    hooks: List[str]
    captions: List[str]
    hashtags: List[str]
    emotion_analysis: Optional[EmotionAnalyzeResponse] = None
    quota_remaining: int

# ==================== HISTORY & ANALYTICS ====================

class GenerationHistory(BaseModel):
    id: int
    type: GenerationType
    created_at: datetime
    input_summary: str
    
    class Config:
        from_attributes = True

class UsageStats(BaseModel):
    current_plan: PlanType
    monthly_quota: int
    used_quota: int
    remaining_quota: int
    generations_this_month: int
    most_used_type: Optional[str]

# ==================== LINK SHORTENER (Legacy) ====================

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
