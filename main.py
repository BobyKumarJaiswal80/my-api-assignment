import time, uuid, jwt, os, yaml
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# FIX Q1: Strict CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dash-w096j7.example.com"], # Sirf is origin ko allow karo
    allow_methods=["*"],
    allow_headers=["*"],
)

# Q1
@app.get("/stats")
async def get_stats(values: str, request: Request):
    nums = [float(x) for x in values.split(",")]
    start = time.time()
    # Yahan logic...
    res = {
        "email": "24f2000080@bhu.ac.in",
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": float(np.mean(nums))
    }
    # Headers ke liye manual response return kar sakte ho ya middleware
    return res

# Q2
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

class VerifyRequest(BaseModel):
    token: str

@app.post("/verify")
async def verify_token(body: VerifyRequest):
    try:
        payload = jwt.decode(body.token, PUBLIC_KEY, algorithms=["RS256"], 
                             issuer="https://idp.exam.local", 
                             audience="tds-hxbe6r1c.apps.exam.local")
        return {"valid": True, "email": payload.get("email"), "sub": payload.get("sub"), "aud": payload.get("aud")}
    except:
        return {"valid": False}

# Q3
@app.get("/effective-config")
async def get_effective_config(request: Request):
    config = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            config.update(yaml.safe_load(f))
    # ... baki logic
    config["api_key"] = "*****"
    return config
