import asyncio
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from demo_data import DEMO_DOSSIER, DEMO_SCENE
from models import AnalysisRequest, Dossier
from service import analyze_scene


app = FastAPI(title="Dramaturg", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict:
    gemini_ready = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    parallel_ready = bool(os.getenv("PARALLEL_API_KEY"))
    return {"liveReady": gemini_ready and parallel_ready, "geminiReady": gemini_ready, "parallelReady": parallel_ready}


@app.get("/api/demo", response_model=Dossier)
def demo() -> Dossier:
    return DEMO_DOSSIER


@app.get("/api/demo-scene")
def demo_scene() -> dict:
    return {"scene": DEMO_SCENE}


@app.post("/api/analyze", response_model=Dossier)
async def analyze(request: AnalysisRequest) -> Dossier:
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) or not os.getenv("PARALLEL_API_KEY"):
        raise HTTPException(status_code=503, detail="Live analysis requires Gemini and Parallel API keys")
    try:
        return await asyncio.to_thread(analyze_scene, request.scene.strip())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Live analysis failed: {error}") from error
