"""
CivicAid Backend — FastAPI Application
AI-powered social services navigator for Davis/Sacramento, CA
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from services.gemini_service import GeminiService
from services.resource_service import ResourceService
from services.voice_service import VoiceService

# Initialize app
app = FastAPI(
    title="CivicAid API",
    description="AI-powered social services navigator for Davis/Sacramento, CA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
gemini_service = GeminiService()
resource_service = ResourceService()
voice_service = VoiceService()


# ──────────────── Request / Response Models ────────────────

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    category: Optional[str] = None

class ResourceSearchRequest(BaseModel):
    category: Optional[str] = None
    city: Optional[str] = None
    service_type: Optional[str] = None
    query: Optional[str] = None
    student: Optional[bool] = None

class VoiceRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None

class TranslateRequest(BaseModel):
    text: str
    target_language: str


# ──────────────── API Routes ────────────────

@app.get("/")
async def root():
    return {
        "name": "CivicAid API",
        "version": "1.0.0",
        "status": "running",
        "ai_enabled": gemini_service.use_ai,
        "voice_enabled": voice_service.use_voice
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ─── Chat ───

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """AI-powered chat for intake and resource matching."""
    try:
        result = await gemini_service.chat(
            message=request.message,
            history=request.history,
            category=request.category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Resources ───

@app.get("/api/categories")
async def get_categories():
    """Get all resource categories."""
    return resource_service.get_all_categories()


@app.post("/api/resources/search")
async def search_resources(request: ResourceSearchRequest):
    """Search and filter resources."""
    results = resource_service.search_resources(
        category=request.category,
        city=request.city,
        service_type=request.service_type,
        query=request.query,
        student=request.student
    )
    return {"results": results, "count": len(results)}


@app.get("/api/resources/{resource_id}")
async def get_resource(resource_id: str):
    """Get a single resource by ID."""
    resource = resource_service.get_resource_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@app.get("/api/resources/category/{category}")
async def get_resources_by_category(category: str):
    """Get all resources in a category."""
    results = resource_service.get_resources_by_category(category)
    return {"results": results, "count": len(results)}


@app.get("/api/crisis")
async def get_crisis_resources():
    """Get emergency/crisis resources."""
    results = resource_service.get_crisis_resources()
    return {"results": results, "count": len(results)}


# ─── Voice ───

@app.post("/api/voice")
async def text_to_speech(request: VoiceRequest):
    """Convert text to speech using ElevenLabs."""
    result = await voice_service.text_to_speech(
        text=request.text,
        voice_id=request.voice_id
    )
    return result


# ─── Translation ───

@app.post("/api/translate")
async def translate(request: TranslateRequest):
    """Translate text using Gemini."""
    try:
        translated = await gemini_service.translate(
            text=request.text,
            target_language=request.target_language
        )
        return {"original": request.text, "translated": translated, "language": request.target_language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
