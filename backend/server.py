# Compatibility shim for Starlette 1.10+ with FastAPI 0.110
import socket, os
try:
    socket.create_connection(('1.1.1.1', 53), timeout=0.2).close()
except Exception:
    os.environ['HF_HUB_OFFLINE'] = '1'

import starlette.routing
_orig_router_init = starlette.routing.Router.__init__
def _compat_router_init(self, *args, **kwargs):
    kwargs.pop("on_startup", None)
    kwargs.pop("on_shutdown", None)
    res = _orig_router_init(self, *args, **kwargs)
    self.on_startup = []
    self.on_shutdown = []
    return res
starlette.routing.Router.__init__ = _compat_router_init
starlette.routing.Router.add_event_handler = lambda self, event_type, func: (
    self.on_startup.append(func) if event_type == "startup" else self.on_shutdown.append(func)
)

from fastapi import FastAPI, APIRouter, UploadFile, File, Response, WebSocket, WebSocketDisconnect, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import io
import json
import logging
from backend.logging_config import configure_logging

# Initialise logging as early as possible
configure_logging()

logger = logging.getLogger(__name__)
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from backend.services.stt_service import MoonshineSTTService
from backend.services.tts_service import PocketTTSService
from backend.services.wakeword_service import WakeWordService
from backend.services.gemini_service import GeminiService, GeminiServiceError

from jarvis.api.bridge import AgentBridge
from jarvis.api.schemas import TaskSubmitData, ApprovalResponseData, EventType

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with graceful fallback
mongo_url = os.environ.get('MONGO_URL')
if mongo_url:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=1000)
        db_name = os.environ.get('DB_NAME', 'jarvis_db')
        db = client[db_name]
    except Exception:
        client = None
        db = None
else:
    client = None
    db = None

# Create the main app without a prefix
app = FastAPI(title="JARVIS API Server", description="Desktop Agent & Voice API Server")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize Speech Services
stt_service = MoonshineSTTService.get_instance()
tts_service = PocketTTSService.get_instance()
wakeword_service = WakeWordService.get_instance(enabled=False)
gemini_service = GeminiService()

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class VoiceConfig(BaseModel):
    wakeword_enabled: bool
    hotkey: str
    stt_model: str
    tts_model: str
    tts_voice: str

class VoiceConfigUpdate(BaseModel):
    wakeword_enabled: Optional[bool] = None
    tts_voice: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    voice: str = "alba"
    format: str = "wav"

class AssistantRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)

class AssistantResponse(BaseModel):
    text: str
    model: str

# Add routes to the router
@api_router.get("/")
async def root():
    return {
        "message": "JARVIS API Server Online",
        "status": "operational",
        "voice": {
            "stt_engine": stt_service.engine,
            "tts_engine": tts_service.engine,
            "wakeword_engine": wakeword_service.engine,
            "wakeword_enabled": wakeword_service.enabled,
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "stt": stt_service.engine,
        "tts": tts_service.engine,
        "gemini": {
            "configured": gemini_service.is_configured,
            "model": gemini_service.model,
        },
        "wakeword": {
            "engine": wakeword_service.engine,
            "enabled": wakeword_service.enabled,
        }
    }

@api_router.get("/voice/config", response_model=VoiceConfig)
def get_voice_config():
    return VoiceConfig(
        wakeword_enabled=wakeword_service.enabled,
        hotkey="<ctrl_r>+<space>",
        stt_model=stt_service.engine,
        tts_model=tts_service.engine,
        tts_voice="alba",
    )

@api_router.post("/voice/config", response_model=VoiceConfig)
def update_voice_config(update: VoiceConfigUpdate):
    if update.wakeword_enabled is not None:
        wakeword_service.set_enabled(update.wakeword_enabled)
    return VoiceConfig(
        wakeword_enabled=wakeword_service.enabled,
        hotkey="<ctrl_r>+<space>",
        stt_model=stt_service.engine,
        tts_model=tts_service.engine,
        tts_voice=update.tts_voice or "alba",
    )

@api_router.post("/stt/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    result = stt_service.transcribe_bytes(audio_bytes)
    return result

@api_router.post("/assistant/respond", response_model=AssistantResponse)
async def assistant_respond(request: AssistantRequest):
    try:
        response_text = await gemini_service.respond(
            "You are JARVIS, a concise and helpful voice assistant. "
            "Answer the user's request naturally. Do not mention internal APIs, "
            "models, or implementation details.\n\nUser: "
            + request.text
        )
    except GeminiServiceError as error:
        logger.error("Gemini assistant request failed: %s", error)
        raise HTTPException(status_code=502, detail=str(error)) from error
    return AssistantResponse(text=response_text, model=gemini_service.last_model)

@api_router.post("/tts/speech")
async def generate_speech(req: TTSRequest):
    wav_bytes = tts_service.generate_speech(req.text, voice=req.voice)
    return Response(content=wav_bytes, media_type="audio/wav")

@api_router.websocket("/voice/stream")
async def voice_stream(websocket: WebSocket):
    await websocket.accept()
    stream_session = stt_service.create_streaming_session()
    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data and data["bytes"]:
                chunk = data["bytes"]
                # 1. If wakeword detection is enabled, check for wake word
                if wakeword_service.enabled:
                    wake_res = wakeword_service.predict_chunk(chunk)
                    if wake_res.get("detected"):
                        await websocket.send_text(json.dumps({
                            "event": "wakeword_detected",
                            "keyword": wake_res.get("keyword"),
                            "confidence": wake_res.get("confidence"),
                        }))

                # 2. Add chunk to STT session
                partial_text = stream_session.add_chunk(chunk)
                if partial_text:
                    await websocket.send_text(json.dumps({
                        "event": "partial_transcript",
                        "text": partial_text,
                    }))
            elif "text" in data and data["text"]:
                msg = json.loads(data["text"])
                if msg.get("command") == "finish":
                    final_text = stream_session.finish()
                    await websocket.send_text(json.dumps({
                        "event": "final_transcript",
                        "text": final_text,
                    }))
                    stream_session = stt_service.create_streaming_session()
    except WebSocketDisconnect:
        logger.info("Voice stream client disconnected.")
    except Exception as e:
        logger.error(f"Voice stream error: {e}")

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    if db is not None:
        _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    if db is not None:
        status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
        for check in status_checks:
            if isinstance(check['timestamp'], str):
                check['timestamp'] = datetime.fromisoformat(check['timestamp'])
        return status_checks
    return []

# Task management & Agent Bridge routes
@api_router.post("/task/submit")
async def submit_task(data: TaskSubmitData):
    bridge = AgentBridge.get_instance()
    task_id = await bridge.submit_task(
        goal=data.goal,
        planner_mode=data.planner_mode,
        engine=data.engine,
        arm=data.arm,
        seed=data.seed,
    )
    return {"ok": True, "task_id": task_id}

@api_router.get("/task/status/{task_id}")
async def get_task_status(task_id: str):
    bridge = AgentBridge.get_instance()
    status = bridge.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True, "task": status}

@api_router.post("/task/cancel/{task_id}")
async def cancel_task(task_id: str):
    bridge = AgentBridge.get_instance()
    cancelled = await bridge.cancel_task(task_id)
    return {"ok": cancelled}

@api_router.post("/task/approval")
async def respond_approval(data: ApprovalResponseData):
    bridge = AgentBridge.get_instance()
    resolved = await bridge.respond_approval(
        task_id=data.task_id,
        nonce=data.nonce,
        approved=data.approved,
        reason=data.reason,
    )
    return {"ok": resolved}

@api_router.get("/capabilities")
async def get_capabilities():
    from jarvis.capabilities import get_system_capabilities
    return get_system_capabilities()

@api_router.websocket("/ws")
async def api_websocket(websocket: WebSocket):
    bridge = AgentBridge.get_instance()
    await websocket.accept()
    await bridge.register_websocket(websocket)
    logger.info("[WS] Client registered and connection accepted")
    try:
        while True:
            # Receive any kind of frame (text, binary, etc.)
            data = await websocket.receive()
            logger.info(f"[WS] Received raw data: {data}")
            if "text" in data:
                text = data["text"]
                logger.info(f"[WS] Received text payload: {text}")
                try:
                    msg = json.loads(text)
                    cmd = msg.get("command")
                    payload = msg.get("data", {})
                    if cmd == "task.submit":
                        task_id = await bridge.submit_task(
                            goal=payload.get("goal", ""),
                            planner_mode=payload.get("planner_mode", "auto"),
                            engine=payload.get("engine", "state_machine"),
                        )
                        await bridge.send_to_client(
                            websocket,
                            EventType.TASK_ACCEPTED,
                            {"task_id": task_id, "goal": payload.get("goal")},
                            task_id=task_id,
                        )
                    elif cmd == "task.cancel":
                        t_id = payload.get("task_id") or bridge.current_task_id
                        if t_id:
                            await bridge.cancel_task(t_id)
                    elif cmd == "approval.respond":
                        await bridge.respond_approval(
                            task_id=payload.get("task_id", ""),
                            nonce=payload.get("nonce", ""),
                            approved=bool(payload.get("approved", False)),
                            reason=payload.get("reason", ""),
                        )
                    elif cmd == "system.ping":
                        await bridge.send_to_client(websocket, EventType.SYSTEM_PONG, {"status": "pong"})
                except Exception as ex:
                    logger.error(f"Error handling WS message: {ex}")
            else:
                # Non‑text frames are ignored for now
                logger.debug("[WS] Non‑text frame received; ignoring")
    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected")
        bridge.unregister_websocket(websocket)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        bridge.unregister_websocket(websocket)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()
