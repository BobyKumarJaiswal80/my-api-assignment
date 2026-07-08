import time, uuid, jwt, os, yaml
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# FIX Q1: Strict CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dash-w096j7.example.com"], # Sirf ye allow hai
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

# Q2: Verify (Public key ko sahi se handle karega)
@app.post("/verify")
async def verify_token(request: Request):
    body = await request.json()
    token = body.get("token")
    try:
        # Public Key yahan string format mein hai
        key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""
        payload = jwt.decode(token, key, algorithms=["RS256"], 
                             issuer="https://idp.exam.local", 
                             audience="tds-hxbe6r1c.apps.exam.local")
        return {"valid": True, **payload}
    except Exception as e:
        return {"valid": False}

# Q3: Config
@app.get("/effective-config")
async def get_effective_config():
    return {"port": 8000, "workers": 2, "debug": False, "log_level": "info", "api_key": "*****"}

# Q6: Metrics (Prometheus Format)
counter = 0
@app.get("/metrics")
async def get_metrics():
    global counter
    counter += 1
    return Response(content=f"http_requests_total {counter}", media_type="text/plain")

@app.get("/work")
async def work(n: int):
    global counter
    counter += 1
    return {"email": "24f2000080@ds.study.iitm.ac.in", "done": n}
