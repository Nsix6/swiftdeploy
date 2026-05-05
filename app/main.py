from fastapi import FastAPI, Request, Response, HTTPException
import os
import time
import random
from datetime import datetime

app = FastAPI()

START_TIME = time.time()

MODE = os.getenv("MODE", "stable")
VERSION = os.getenv("APP_VERSION", "1.0.0")

CHAOS_STATE = {
    "mode": None,
    "duration": 0,
    "rate": 0.0
}


@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    if MODE == "canary" and request.url.path != "/chaos":
        if CHAOS_STATE["mode"] == "slow":
            time.sleep(CHAOS_STATE["duration"])

        if CHAOS_STATE["mode"] == "error":
            if random.random() < CHAOS_STATE["rate"]:
                return Response(
                    content='{"error":"Injected failure"}',
                    status_code=500,
                    media_type="application/json"
                )

    response = await call_next(request)

    if MODE == "canary":
        response.headers["X-Mode"] = "canary"

    return response


@app.get("/")
def root():
    return {
        "message": "Welcome to SwiftDeploy API",
        "mode": MODE,
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/healthz")
def health():
    uptime = int(time.time() - START_TIME)
    return {
        "status": "ok",
        "uptime": uptime
    }


@app.post("/chaos")
def chaos(payload: dict):
    if MODE != "canary":
        raise HTTPException(status_code=403, detail="Chaos only allowed in canary mode")

    mode = payload.get("mode")

    if mode == "slow":
        CHAOS_STATE["mode"] = "slow"
        CHAOS_STATE["duration"] = payload.get("duration", 1)
        return {"status": "slow mode enabled"}

    elif mode == "error":
        CHAOS_STATE["mode"] = "error"
        CHAOS_STATE["rate"] = payload.get("rate", 0.5)
        return {"status": "error mode enabled"}

    elif mode == "recover":
        CHAOS_STATE["mode"] = None
        CHAOS_STATE["duration"] = 0
        CHAOS_STATE["rate"] = 0.0
        return {"status": "recovered"}

    else:
        raise HTTPException(status_code=400, detail="Invalid chaos mode")
