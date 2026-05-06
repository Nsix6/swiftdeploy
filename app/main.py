from fastapi import FastAPI, Request, Response
import time
import os
import random

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

START_TIME = time.time()
MODE = os.getenv("MODE", "stable")

chaos_mode = None
error_rate = 0

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "path", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    buckets=[0.1, 0.3, 0.5, 1, 2, 5]
)

APP_UPTIME = Gauge("app_uptime_seconds", "Application uptime in seconds")
APP_MODE = Gauge("app_mode", "Application mode (0=stable, 1=canary)")
CHAOS_STATE = Gauge("chaos_active", "Chaos state (0=none,1=slow,2=error)")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    if chaos_mode == "slow":
        time.sleep(3)

    if chaos_mode == "error" and random.random() < error_rate:
        REQUEST_COUNT.labels(request.method, request.url.path, "500").inc()
        return Response(content='{"error":"Injected failure"}', status_code=500)

    response = await call_next(request)

    duration = time.time() - start_time

    REQUEST_LATENCY.observe(duration)
    REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()

    return response


@app.get("/")
def root():
    return {
        "message": "Welcome to SwiftDeploy API",
        "mode": MODE,
        "version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }


@app.get("/healthz")
def health():
    uptime = int(time.time() - START_TIME)
    return {"status": "ok", "uptime": uptime}


@app.post("/chaos")
def chaos(payload: dict):
    global chaos_mode, error_rate

    mode = payload.get("mode")

    if mode == "slow":
        chaos_mode = "slow"
        return {"status": "slow mode enabled"}

    if mode == "error":
        chaos_mode = "error"
        error_rate = payload.get("rate", 0.5)
        return {"status": "error mode enabled"}

    if mode == "recover":
        chaos_mode = None
        error_rate = 0
        return {"status": "recovered"}

    return {"error": "invalid mode"}


@app.get("/metrics")
def metrics():
    uptime = time.time() - START_TIME
    APP_UPTIME.set(uptime)
    APP_MODE.set(1 if MODE == "canary" else 0)

    if chaos_mode == "slow":
        CHAOS_STATE.set(1)
    elif chaos_mode == "error":
        CHAOS_STATE.set(2)
    else:
        CHAOS_STATE.set(0)

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
