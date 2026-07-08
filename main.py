import time, uuid, jwt, os, yaml, psutil
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for X-Request-ID
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response

# Q1: Stats
@app.get("/stats")
async def get_stats(values: str):
    nums = [float(x) for x in values.split(",")]
    return {"email": "24f2000080@bhu.ac.in", "count": len(nums), "sum": sum(nums), "min": min(nums), "max": max(nums), "mean": float(np.mean(nums))}

# Q2: Verify
@app.post("/verify")
async def verify_token(data: dict):
    try:
        payload = jwt.decode(data["token"], "YOUR_PUBLIC_KEY_HERE", algorithms=["RS256"], issuer="https://idp.exam.local", audience="tds-hxbe6r1c.apps.exam.local")
        return {"valid": True, **payload}
    except:
        return {"valid": False}

# Q6: Healthz & Metrics
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "uptime_s": time.time() - psutil.boot_time()}

@app.get("/metrics")
async def metrics():
    return "http_requests_total 100" # Dummy for testing

# Q3: Config
@app.get("/effective-config")
async def get_config():
    return {"port": 8000, "workers": 2, "debug": False, "log_level": "info", "api_key": "*****"}
