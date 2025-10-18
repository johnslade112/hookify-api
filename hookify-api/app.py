from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
import os

from db import Base, engine, get_db
from models import Link
from schemas import GenerateRequest, GenerateResponse, ShortenRequest, ShortenResponse, LinkAnalytics
from generation import generate_content
from security import verify_api_key
from utils import gen_code

APP_URL = os.getenv("APP_URL", "https://hookify-api.onrender.com")

app = FastAPI(title="Hookify API", version="0.1.0")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://johnslade112.github.io",               # domínio do GitHub Pages
        "https://johnslade112.github.io/hookify-panel", # página do painel
        "*"                                             # na validação, deixe '*'; depois você pode remover
    ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/templates", dependencies=[Depends(verify_api_key)])
def templates():
    return {
        "platforms": ["tiktok", "reels", "shorts"],
        "tones": ["direto", "motivacional", "educativo", "storytelling"],
        "languages": ["pt"],
        "notes": "Use 'variants' para A/B testing e 'hashtags_count' para controlar volume."
    }

@app.post("/generate", response_model=GenerateResponse, dependencies=[Depends(verify_api_key)])
def generate(req: GenerateRequest):
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
    return {"hooks": hooks, "captions": captions, "hashtags": hashtags}

@app.post("/links/shorten", response_model=ShortenResponse, dependencies=[Depends(verify_api_key)])
def shorten(req: ShortenRequest, db: Session = Depends(get_db)):
    code = gen_code()
    # Monta URL destino com UTM
    sep = "&" if "?" in req.url else "?"
    target = f"{req.url}{sep}utm_source={req.utm_source}&utm_medium={req.utm_medium}&utm_campaign={req.utm_campaign}"
    link = Link(code=code, url=str(target),
                utm_source=req.utm_source, utm_medium=req.utm_medium, utm_campaign=req.utm_campaign)
    db.add(link)
    db.commit()
    db.refresh(link)
    return ShortenResponse(code=code, short_url=f"{APP_URL}/r/{code}", target_url=link.url, clicks=link.clicks)

@app.get("/r/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(Link).where(Link.code == code))
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    link.clicks += 1
    db.add(link)
    db.commit()
    return RedirectResponse(link.url, status_code=302)

@app.get("/analytics/links", response_model=List[LinkAnalytics], dependencies=[Depends(verify_api_key)])
def analytics(db: Session = Depends(get_db)):
    rows = db.scalars(select(Link)).all()
    return [LinkAnalytics(code=r.code, url=r.url, clicks=r.clicks) for r in rows]
