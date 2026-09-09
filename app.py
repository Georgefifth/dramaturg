import asyncio
import hashlib
import logging
import os
import secrets
import threading
import time
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from demo_data import DEMO_DOSSIER, DEMO_SCENE
from models import AnalysisRequest, Dossier
from service import analyze_scene


logger = logging.getLogger("dramaturg")
app = FastAPI(title="Dramaturg", version="1.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
analysis_cache: dict[str, tuple[float, Dossier]] = {}
ip_attempts: dict[str, deque[float]] = defaultdict(deque)
daily_attempts: deque[float] = deque()
job_store: dict[str, dict] = {}
state_lock = threading.Lock()
analysis_lock = threading.Lock()


def _cache_key(scene: str) -> str:
    return hashlib.sha256(scene.strip().encode()).hexdigest()


def _cached(scene: str) -> Dossier | None:
    key = _cache_key(scene)
    ttl = int(os.getenv("ANALYSIS_CACHE_TTL_SECONDS", "21600"))
    with state_lock:
        cached = analysis_cache.get(key)
        if cached and time.time() - cached[0] <= ttl:
            return cached[1]
        if cached:
            analysis_cache.pop(key, None)
    return None


def _store(scene: str, dossier: Dossier) -> None:
    limit = int(os.getenv("ANALYSIS_CACHE_MAX_ITEMS", "100"))
    with state_lock:
        if len(analysis_cache) >= limit:
            oldest = min(analysis_cache, key=lambda key: analysis_cache[key][0])
            analysis_cache.pop(oldest, None)
        analysis_cache[_cache_key(scene)] = (time.time(), dossier)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _enforce_limits(client_ip: str) -> None:
    now = time.time()
    hourly_limit = int(os.getenv("RATE_LIMIT_PER_HOUR", "3"))
    daily_limit = int(os.getenv("GLOBAL_DAILY_ANALYSIS_LIMIT", "50"))
    with state_lock:
        attempts = ip_attempts[client_ip]
        while attempts and attempts[0] <= now - 3600:
            attempts.popleft()
        while daily_attempts and daily_attempts[0] <= now - 86400:
            daily_attempts.popleft()
        if len(attempts) >= hourly_limit:
            raise HTTPException(status_code=429, detail="Live analysis limit reached for this hour. Cached scenes and the evidence sample remain available.", headers={"Retry-After": "3600"})
        if len(daily_attempts) >= daily_limit:
            raise HTTPException(status_code=429, detail="The public live-analysis budget is exhausted for today. The evidence sample remains available.", headers={"Retry-After": "86400"})
        attempts.append(now)
        daily_attempts.append(now)


def _prune_jobs() -> None:
    cutoff = time.time() - int(os.getenv("JOB_TTL_SECONDS", "3600"))
    with state_lock:
        expired = [job_id for job_id, job in job_store.items() if job["updatedAt"] < cutoff]
        for job_id in expired:
            job_store.pop(job_id, None)


def _update_job(job_id: str, **values) -> None:
    with state_lock:
        if job_id in job_store:
            job_store[job_id].update(values, updatedAt=time.time())


def _run_job(job_id: str, scene: str) -> None:
    def report(phase: str, message: str, completed: int, total: int) -> None:
        _update_job(job_id, phase=phase, message=message, completed=completed, total=total)

    try:
        dossier = analyze_scene(scene, progress=report)
        _store(scene, dossier)
        _update_job(job_id, status="complete", phase="complete", message="The dossier is ready", dossier=dossier)
    except Exception:
        logger.exception("Background live analysis failed")
        _update_job(job_id, status="failed", phase="failed", message="A research provider could not complete this dossier. Please try again later.")
    finally:
        analysis_lock.release()


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
    return {
        "liveReady": gemini_ready and parallel_ready,
        "geminiReady": gemini_ready,
        "parallelReady": parallel_ready,
        "rateLimitPerHour": int(os.getenv("RATE_LIMIT_PER_HOUR", "3")),
        "cacheTtlSeconds": int(os.getenv("ANALYSIS_CACHE_TTL_SECONDS", "21600")),
    }


@app.get("/api/demo", response_model=Dossier)
def demo() -> Dossier:
    return DEMO_DOSSIER


@app.get("/api/demo-scene")
def demo_scene() -> dict:
    return {"scene": DEMO_SCENE}


@app.post("/api/jobs", status_code=202)
def create_job(payload: AnalysisRequest, request: Request):
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) or not os.getenv("PARALLEL_API_KEY"):
        raise HTTPException(status_code=503, detail="Live analysis is temporarily unavailable. The evidence sample remains available.")
    scene = payload.scene.strip()
    cached = _cached(scene)
    if cached:
        return JSONResponse(status_code=200, content={"status": "complete", "cache": "HIT", "dossier": cached.model_dump(mode="json")})
    _enforce_limits(_client_ip(request))
    if not analysis_lock.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Another live dossier is being prepared. Try again shortly.", headers={"Retry-After": "60"})
    _prune_jobs()
    job_id = secrets.token_urlsafe(16)
    now = time.time()
    with state_lock:
        job_store[job_id] = {
            "jobId": job_id,
            "status": "running",
            "phase": "queued",
            "message": "The research job is queued",
            "completed": 0,
            "total": 1,
            "createdAt": now,
            "updatedAt": now,
        }
    threading.Thread(target=_run_job, args=(job_id, scene), daemon=True).start()
    return {"jobId": job_id, "status": "running", "cache": "MISS"}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    _prune_jobs()
    with state_lock:
        job = job_store.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Research job not found or expired.")
        return job.copy()


@app.post("/api/analyze", response_model=Dossier)
async def analyze(payload: AnalysisRequest, request: Request, response: Response) -> Dossier:
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) or not os.getenv("PARALLEL_API_KEY"):
        raise HTTPException(status_code=503, detail="Live analysis is temporarily unavailable. The evidence sample remains available.")
    scene = payload.scene.strip()
    cached = _cached(scene)
    if cached:
        response.headers["X-Dramaturg-Cache"] = "HIT"
        return cached
    _enforce_limits(_client_ip(request))
    if not analysis_lock.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Another live dossier is being prepared. Try again shortly.", headers={"Retry-After": "60"})
    try:
        dossier = await asyncio.to_thread(analyze_scene, scene)
        _store(scene, dossier)
        response.headers["X-Dramaturg-Cache"] = "MISS"
        return dossier
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        logger.exception("Live analysis failed")
        raise HTTPException(status_code=502, detail="A research provider could not complete this dossier. Please try again later.") from error
    finally:
        analysis_lock.release()
