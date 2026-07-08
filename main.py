import time, uuid, jwt, os, yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

# Sabhi questions ke liye CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Q1: Metrics API ---
@app.get("/stats")
async def get_stats(values: str):
    nums = [float(x) for x in values.split(",")]
    return {
        "email": "24f2000080@bhu.ac.in",
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": float(np.mean(nums))
    }

# --- Q2: OAuth Verification ---
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNno/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

@app.post("/verify")
async def verify_token(request: Request):
    data = await request.json()
    token = data.get("token")
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], 
                             issuer="https://idp.exam.local", 
                             audience="tds-hxbe6r1c.apps.exam.local")
        return {"valid": True, "email": payload.get("email"), "sub": payload.get("sub"), "aud": payload.get("aud")}
    except:
        return {"valid": False}

# --- Q3: Config Precedence ---
@app.get("/effective-config")
async def get_effective_config(request: Request):
    config = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            config.update(yaml.safe_load(f))
    if os.getenv("NUM_WORKERS"): config["workers"] = int(os.getenv("NUM_WORKERS"))
    if os.getenv("APP_PORT"): config["port"] = int(os.getenv("APP_PORT"))
    for key, value in request.query_params.multi_items():
        if key in ["port", "workers"]: config[key] = int(value)
        elif key == "debug": config[key] = value.lower() in ["true", "1", "yes", "on"]
        else: config[key] = value
    config["api_key"] = "*****"
    return config
