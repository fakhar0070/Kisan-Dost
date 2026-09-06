"""
Kisan Dost — web backend.

This wraps the exact same agent logic as main.py (triage_agent, SQLiteSession,
FarmerProfile, guardrail handling) behind a small FastAPI HTTP API, and serves
the frontend/ folder as static files.

Run with:
    uvicorn api:app --reload

Then open http://127.0.0.1:8000 in a browser.
"""

import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents import Runner, SQLiteSession, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered

from agents_config import triage_agent
from models import FarmerProfile


app = FastAPI(title="Kisan Dost API")

# --- In-memory store: one SQLiteSession + FarmerProfile per browser session ---
# Note: the FarmerProfile part resets if the server restarts. The chat history
# itself persists in kisan_dost.db because SQLiteSession writes to disk.
_sessions: dict[str, SQLiteSession] = {}
_profiles: dict[str, FarmerProfile] = {}


def _get_session_and_profile(session_id: str) -> tuple[SQLiteSession, FarmerProfile]:
    if session_id not in _sessions:
        _sessions[session_id] = SQLiteSession(session_id=session_id, db_path="kisan_dost.db")
        _profiles[session_id] = FarmerProfile()
    return _sessions[session_id], _profiles[session_id]


# --- Request/response models -------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    blocked: bool = False


class ProfileUpdateRequest(BaseModel):
    session_id: str
    name: str | None = None
    district: str | None = None
    province: str | None = None
    land_size_acres: float | None = None
    current_crop: str | None = None


# --- API routes ----------------------------------------------------------
# IMPORTANT: these must be declared BEFORE the static-files mount at the
# bottom of this file, otherwise the "/" mount would shadow them.

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    session, profile = _get_session_and_profile(req.session_id)

    try:
        result = await Runner.run(
            triage_agent,
            req.message,
            session=session,
            context=profile,
        )
        return ChatResponse(reply=str(result.final_output))

    except InputGuardrailTripwireTriggered:
        return ChatResponse(
            blocked=True,
            reply=(
                "Maazrat, yeh sawaal farming se related nahi lagta ya human/animal "
                "medical advice maang raha hai — main sirf zaraat (khaiti-baari) "
                "mein madad kar sakta hoon."
            ),
        )
    except OutputGuardrailTripwireTriggered:
        return ChatResponse(
            blocked=True,
            reply=(
                "Maazrat, jawab safe dosage limit cross kar raha tha isliye rok "
                "diya gaya. Baraye meherbani apne nazdeeki agriculture officer se "
                "dosage confirm karein."
            ),
        )


@app.get("/api/profile")
async def get_profile(session_id: str) -> dict:
    _, profile = _get_session_and_profile(session_id)
    return profile.model_dump()


@app.post("/api/profile")
async def update_profile(req: ProfileUpdateRequest) -> dict:
    _, profile = _get_session_and_profile(req.session_id)

    if req.name is not None and req.name.strip():
        profile.name = req.name.strip()
    if req.district is not None and req.district.strip():
        profile.district = req.district.strip()
    if req.province is not None and req.province.strip():
        profile.province = req.province.strip()
    if req.land_size_acres is not None:
        profile.land_size_acres = req.land_size_acres
    if req.current_crop is not None and req.current_crop.strip():
        profile.current_crop = req.current_crop.strip()

    return profile.model_dump()


@app.get("/api/health")
async def health() -> dict:
    return {"ok": True, "api_key_set": bool(os.getenv("OPENAI_API_KEY"))}


# --- Serve the frontend --------------------------------------------------
# Must come AFTER the /api/* routes above.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
