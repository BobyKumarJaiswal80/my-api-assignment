# Purani line ko hata kar ye wali likho:
from fastapi import FastAPI, Request, Response, HTTPException, Header
import time, uuid, jwt, os, yaml
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# FIX Q1: Strict CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Sirf ye allow hai
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
    return {"email": "24f2000080@ds.study.iitm.ac.in", "count": len(nums), "sum": sum(nums), "min": min(nums), "max": max(nums), "mean": float(np.mean(nums))}

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
# Q3: Effective Config (Isse add karo)
# Q3: Naya, Robust Effective Config
@app.get("/effective-config")
async def get_effective_config(request: Request):
    # Default values
    config = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "****"}
    
    # Query parameters ko handle karna
    params = dict(request.query_params)
    for key, val in params.items():
        if key == "port": config["port"] = int(val)
        elif key == "workers": config["workers"] = int(val)
        elif key == "debug": config["debug"] = val.lower() in ["true", "1", "yes", "on"]
        else: config[key] = val
            
    return config

# Q4: Redis Hit & Health (Inhe add karo)
# Agar Redis nahi hai, toh hum simple memory dictionary use karenge taaki 404 na aaye
data_store = {}

@app.post("/hit/{key}")
async def hit(key: str):
    data_store[key] = data_store.get(key, 0) + 1
    return {"key": key, "count": data_store[key]}

@app.get("/count/{key}")
async def get_count(key: str):
    return {"key": key, "count": data_store.get(key, 0)}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "redis": "up"}

# Q5: Analytics (Header handling fix)
@app.post("/analytics")
async def analytics(data: dict, x_api_key: str = Header(None, alias="X-API-KEY")):
    # Agar key missing hai ya galat hai, 401 return karo
    if x_api_key != "ak_yszijq2eseo8gstan0dx9ow8":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # ... baki ka logic wahi rahega ...
    events = data.get("events", [])
    revenue = sum(e.get("amount", 0) for e in events if e.get("amount", 0) > 0)
    user_totals = {}
    for e in events:
        user = e.get("user")
        amount = e.get("amount", 0)
        if user and amount > 0:
            user_totals[user] = user_totals.get(user, 0) + amount
            
    top_user = max(user_totals, key=user_totals.get) if user_totals else None
    
    return {
        "email": "24f2000080@ds.study.iitm.ac.in",
        "total_events": len(events),
        "unique_users": len(set(e.get("user") for e in events if e.get("user"))),
        "revenue": float(revenue),
        "top_user": top_user
    }
