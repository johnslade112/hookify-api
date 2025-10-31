from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
import os

from db import Base, engine, get_db
from models import User, Subscription, ApiKey, Link, Generation, PlanType, GenerationType, PLAN_QUOTAS
from schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    SubscriptionResponse, UpgradeRequest,
    HookGenerateRequest, HookGenerateResponse,
    CaptionGenerateRequest, CaptionGenerateResponse,
    HashtagGenerateRequest, HashtagGenerateResponse,
    EmotionAnalyzeRequest, EmotionAnalyzeResponse,
    CompleteGenerateRequest, CompleteGenerateResponse,
    GenerationHistory, UsageStats,
    ShortenRequest, ShortenResponse, LinkAnalytics,
    GenerateRequest, GenerateResponse  # V1 legacy
)
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user, generate_api_key, get_user_by_api_key
)
from ai_generation import (
    generate_hooks, generate_captions, generate_hashtags,
    analyze_emotion, generate_complete
)
from quota import check_and_update_quota, get_quota_info, upgrade_plan
from generation import generate_content  # V1 legacy
from utils import gen_code

APP_URL = os.getenv("APP_URL", "http://localhost:8000")

app = FastAPI(
    title="Hookify API",
    version="2.0.0",
    description="API com IA para geração de hooks, legendas, hashtags e análise de emoção para vídeos",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar tabelas
Base.metadata.create_all(bind=engine)

# ==================== HELPER FUNCTIONS ====================

async def get_current_user_flexible(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Aceita tanto JWT (Bearer token) quanto API Key"""
    
    # Tenta API Key primeiro
    if x_api_key:
        user = get_user_by_api_key(x_api_key, db)
        if user:
            return user
    
    # Tenta JWT
    if authorization and authorization.startswith("Bearer "):
        from fastapi.security import HTTPAuthorizationCredentials
        from auth import decode_token
        
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if user_id:
            user = db.get(User, user_id)
            if user and user.is_active:
                return user
    
    raise HTTPException(status_code=401, detail="Autenticação necessária")

# ==================== ROOT ====================

@app.get("/")
def root():
    return {
        "message": "Hookify API v2.0 - Geração de conteúdo com IA",
        "docs": f"{APP_URL}/docs",
        "version": "2.0.0"
    }

# ==================== AUTH ENDPOINTS ====================

@app.post("/auth/register", response_model=UserResponse, tags=["Auth"])
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registra um novo usuário"""
    
    # Verifica se email já existe
    existing = db.scalar(select(User).where(User.email == user_data.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Cria usuário
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Cria assinatura FREE
    subscription = Subscription(
        user_id=user.id,
        plan_type=PlanType.FREE,
        monthly_quota=PLAN_QUOTAS[PlanType.FREE]
    )
    db.add(subscription)
    
    # Cria API key padrão
    api_key = ApiKey(
        user_id=user.id,
        key=generate_api_key(),
        name="Default Key"
    )
    db.add(api_key)
    
    db.commit()
    db.refresh(user)
    
    return user

@app.post("/auth/login", response_model=Token, tags=["Auth"])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Faz login e retorna token JWT"""
    
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def get_me(user: User = Depends(get_current_user_flexible)):
    """Retorna dados do usuário atual"""
    return user

# ==================== SUBSCRIPTION ENDPOINTS ====================

@app.get("/subscription", response_model=SubscriptionResponse, tags=["Subscription"])
def get_subscription(user: User = Depends(get_current_user_flexible), db: Session = Depends(get_db)):
    """Retorna assinatura atual do usuário"""
    
    if not user.subscription:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    
    sub = user.subscription
    return SubscriptionResponse(
        id=sub.id,
        plan_type=sub.plan_type,
        monthly_quota=sub.monthly_quota,
        used_quota=sub.used_quota,
        remaining_quota=sub.remaining_quota(),
        is_active=sub.is_active,
        start_date=sub.start_date,
        end_date=sub.end_date
    )

@app.post("/subscription/upgrade", response_model=SubscriptionResponse, tags=["Subscription"])
def upgrade_subscription(
    request: UpgradeRequest,
    user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Faz upgrade do plano"""
    
    subscription = upgrade_plan(user, request.plan_type.value, db)
    
    return SubscriptionResponse(
        id=subscription.id,
        plan_type=subscription.plan_type,
        monthly_quota=subscription.monthly_quota,
        used_quota=subscription.used_quota,
        remaining_quota=subscription.remaining_quota(),
        is_active=subscription.is_active,
        start_date=subscription.start_date,
        end_date=subscription.end_date
    )

@app.get("/subscription/usage", response_model=UsageStats, tags=["Subscription"])
def get_usage(user: User = Depends(get_current_user_flexible), db: Session = Depends(get_db)):
    """Retorna estatísticas de uso"""
    
    quota_info = get_quota_info(user)
    
    # Conta gerações do mês
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    generations_count = db.scalar(
        select(func.count(Generation.id))
        .where(Generation.user_id == user.id)
        .where(Generation.created_at >= thirty_days_ago)
    ) or 0
    
    # Tipo mais usado
    most_used = db.execute(
        select(Generation.type, func.count(Generation.id).label("count"))
        .where(Generation.user_id == user.id)
        .where(Generation.created_at >= thirty_days_ago)
        .group_by(Generation.type)
        .order_by(func.count(Generation.id).desc())
        .limit(1)
    ).first()
    
    return UsageStats(
        current_plan=PlanType(quota_info["plan"]) if quota_info["plan"] != "NONE" else PlanType.FREE,
        monthly_quota=quota_info["monthly_quota"],
        used_quota=quota_info["used_quota"],
        remaining_quota=quota_info["remaining_quota"],
        generations_this_month=generations_count,
        most_used_type=most_used[0].value if most_used else None
    )

# ==================== AI GENERATION ENDPOINTS (V2) ====================

@app.post("/v2/generate/hook", response_model=HookGenerateResponse, tags=["AI Generation"])
def generate_hook_v2(
    request: HookGenerateRequest,
    user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Gera hooks virais com IA"""
    
    hooks = generate_hooks(
        niche=request.niche,
        topic=request.topic,
        tone=request.tone,
        platform=request.platform,
        variants=request.variants
    )
    
    remaining = check_and_update_quota(
        user, db, GenerationType.HOOK,
        input_data=request.dict(),
        output_data={"hooks": hooks}
    )
    
    return HookGenerateResponse(hooks=hooks, quota_remaining=remaining)

@app.post("/v2/generate/caption", response_model=CaptionGenerateResponse, tags=["AI Generation"])
def generate_caption_v2(
    request: CaptionGenerateRequest,
    user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Gera legendas persuasivas com IA"""
    
    captions = generate_captions(
        niche=request.niche,
        topic=request.topic,
        tone=request.tone,
        product_name=request.product_name,
        call_to_action=request.call_to_action,
        max_length=request.max_length,
        variants=request.variants
    )
    
    remaining = check_and_update_quota(
        user, db, GenerationType.CAPTION,
        input_data=request.dict(),
        output_data={"captions": captions}
    )
    
    return CaptionGenerateResponse(captions=captions, quota_remaining=remaining)

@app.post("/v2/generate/hashtags", response_model=HashtagGenerateResponse, tags=["AI Generation"])
def generate_hashtags_v2(
    request: HashtagGenerateRequest,
    user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Gera hashtags relevantes com IA"""
    
    hashtags = generate_hashtags(
        niche=request.niche,
        topic=request.topic,
        platform=request.platform,
        count=request.count,
        include_trending=request.include_trending
    )
    
    remaining = check_and_update_quota(
        user, db, GenerationType.HASHTAG,
        input_data=request.dict(),
        output_data={"hashtags": hashtags}
    )
    
    return HashtagGenerateResponse(hashtags=hashtags, quota_remaining=remaining)

@app.post("/v2/analyze/emotion", response_model=EmotionAnalyzeResponse, tags=["AI Generation"])
def analyze_emotion_v2(
    request: EmotionAnalyzeRequest,
    user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Analisa emoção do texto/vídeo"""
    
    result = analyze_emotion(request.text, request.context)
    
    remaining = check_and_update_quota(
        user, db, GenerationType.EMOTION,
        input_data=request.dict(),
        output_data=result
    )
    
    return EmotionAnalyzeResponse(
        primary_emotion=result["primary_emotion"],
        confidence=result["confidence"],
        emotions_breakdown=result["emotions_breakdown"],
        suggestions=result["suggestions"],
        quota_remaining=remaining
    )

@app.post("/v2/generate/complete", response_model=CompleteGenerateResponse, tags=["AI Generation"])
def generate_complete_v2(
    request: CompleteGenerateRequest,
    user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Gera hooks, legendas, hashtags e opcionalmente analisa emoção"""
    
    hooks, captions, hashtags, emotion = generate_complete(
        niche=request.niche,
        topic=request.topic,
        tone=request.tone,
        platform=request.platform,
        product_name=request.product_name,
        call_to_action=request.call_to_action,
        analyze_emotion_flag=request.analyze_emotion
    )
    
    remaining = check_and_update_quota(
        user, db, GenerationType.COMPLETE,
        input_data=request.dict(),
        output_data={"hooks": hooks, "captions": captions, "hashtags": hashtags, "emotion": emotion}
    )
    
    emotion_response = None
    if emotion:
        emotion_response = EmotionAnalyzeResponse(
            primary_emotion=emotion["primary_emotion"],
            confidence=emotion["confidence"],
            emotions_breakdown=emotion["emotions_breakdown"],
            suggestions=emotion["suggestions"],
            quota_remaining=remaining
        )
    
    return CompleteGenerateResponse(
        hooks=hooks,
        captions=captions,
        hashtags=hashtags,
        emotion_analysis=emotion_response,
        quota_remaining=remaining
    )

# ==================== HISTORY ====================

@app.get("/history", response_model=List[GenerationHistory], tags=["History"])
def get_history(
    limit: int = 50,
    user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Retorna histórico de gerações"""
    
    generations = db.scalars(
        select(Generation)
        .where(Generation.user_id == user.id)
        .order_by(Generation.created_at.desc())
        .limit(limit)
    ).all()
    
    return [
        GenerationHistory(
            id=g.id,
            type=g.type,
            created_at=g.created_at,
            input_summary=g.input_data[:100] if g.input_data else ""
        )
        for g in generations
    ]

# ==================== LEGACY V1 ENDPOINTS ====================

@app.get("/templates", tags=["Legacy V1"])
def templates():
    return {
        "platforms": ["tiktok", "reels", "shorts"],
        "tones": ["direto", "motivacional", "educativo", "storytelling"],
        "languages": ["pt"],
        "notes": "Use endpoints /v2/* para geração com IA real"
    }

@app.post("/generate", response_model=GenerateResponse, tags=["Legacy V1"])
def generate_v1(
    req: GenerateRequest,
    user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """[DEPRECATED] Use /v2/generate/complete"""
    
    hooks, captions, hashtags = generate_content(
        language=req.language,
        niche=req.niche,
        tone=req.tone,
        product=req.product_name,
        problems=req.problems,
        cta=req.call_to_action,
        variants=req.variants,
        hashtags_count=req.hashtags_count
    )
    
    check_and_update_quota(user, db, GenerationType.COMPLETE)
    
    return {"hooks": hooks, "captions": captions, "hashtags": hashtags}

# ==================== LINK SHORTENER ====================

@app.post("/links/shorten", response_model=ShortenResponse, tags=["Links"])
def shorten(req: ShortenRequest, db: Session = Depends(get_db)):
    code = gen_code()
    sep = "&" if "?" in str(req.url) else "?"
    target = f"{req.url}{sep}utm_source={req.utm_source}&utm_medium={req.utm_medium}&utm_campaign={req.utm_campaign}"
    link = Link(code=code, url=str(target),
                utm_source=req.utm_source, utm_medium=req.utm_medium, utm_campaign=req.utm_campaign)
    db.add(link)
    db.commit()
    db.refresh(link)
    return ShortenResponse(code=code, short_url=f"{APP_URL}/r/{code}", target_url=link.url, clicks=link.clicks)

@app.get("/r/{code}", tags=["Links"])
def redirect(code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(Link).where(Link.code == code))
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    link.clicks += 1
    db.add(link)
    db.commit()
    return RedirectResponse(link.url, status_code=302)

@app.get("/analytics/links", response_model=List[LinkAnalytics], tags=["Links"])
def analytics(db: Session = Depends(get_db)):
    rows = db.scalars(select(Link)).all()
    return [LinkAnalytics(code=r.code, url=r.url, clicks=r.clicks) for r in rows]
