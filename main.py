from fastapi import FastAPI, Request, Response, HTTPException, Header, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import defaultdict, deque
from time import time
from uuid import uuid4
import jwt
import re

app = FastAPI()

EMAIL = "24f2000080@ds.study.iitm.ac.in"
STARTED_AT = time()

LOGS = deque(maxlen=2000)
HTTP_REQUESTS_TOTAL = 0
COUNTS = defaultdict(int)
IDEMPOTENCY = {}
RATE_BUCKETS = defaultdict(list)
ORDERS = [{"id": i} for i in range(1, 58)]

ALLOWED_ORIGINS = [
    "https://dash-w096j7.example.com",
    "https://app-1967ia.example.com",
    "https://exam.sanand.workers.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_headers(request: Request, call_next):
    global HTTP_REQUESTS_TOTAL
    start = time()
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    HTTP_REQUESTS_TOTAL += 1
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{time() - start:.6f}"
    LOGS.append({
        "level": "info",
        "ts": time(),
        "path": request.url.path,
        "request_id": request_id,
    })
    return response

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "uptime_s": float(max(0.0, time() - STARTED_AT))}

@app.get("/logs/tail")
async def logs_tail(limit: int = Query(10, ge=1, le=100)):
    return list(LOGS)[-limit:]

@app.get("/metrics")
async def metrics():
    return PlainTextResponse(f"http_requests_total {HTTP_REQUESTS_TOTAL}\n", media_type="text/plain")

@app.get("/work")
async def work(n: int = Query(1, ge=0)):
    for _ in range(n):
        pass
    return {"email": EMAIL, "done": n}

# ---------------- Q2 Verify ----------------
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

class VerifyBody(BaseModel):
    token: str

@app.post("/verify")
async def verify_token(body: VerifyBody):
    try:
        claims = jwt.decode(
            body.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer="https://idp.exam.local",
            audience="tds-hxbe6r1c.apps.exam.local",
        )
        return {
            "valid": True,
            "email": claims.get("email"),
            "sub": claims.get("sub"),
            "aud": claims.get("aud"),
        }
    except Exception:
        return JSONResponse(status_code=401, content={"valid": False})

# ---------------- Q3 Config ----------------
@app.get("/effective-config")
async def effective_config(request: Request):
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "****",
    }

    layer_yaml = {
        "port": 8516,
        "workers": 6,
        "debug": False,
        "log_level": "debug",
    }

    layer_env = {
        "workers": 2,  # NUM_WORKERS -> workers
        "log_level": "error",
    }

    layer_os = {
        "port": 8505,
        "workers": 6,
    }

    config.update(layer_yaml)
    config.update(layer_env)
    config.update(layer_os)

    for key, value in request.query_params.multi_items():
        if key == "set" and "=" in value:
            k, v = value.split("=", 1)
            if k in ("port", "workers"):
                config[k] = int(v)
            elif k == "debug":
                config[k] = v.lower() in ("true", "1", "yes", "on")
            elif k == "api_key":
                config[k] = "****"
            else:
                config[k] = v

    config["api_key"] = "****"
    return config

# ---------------- Q4 Compose/Redis fallback ----------------
@app.post("/hit/{key}")
async def hit(key: str):
    COUNTS[key] += 1
    return {"key": key, "count": COUNTS[key]}

@app.get("/count/{key}")
async def count(key: str):
    return {"key": key, "count": COUNTS[key]}

# ---------------- Q5 Analytics ----------------
class AnalyticsBody(BaseModel):
    events: list[dict]

@app.post("/analytics")
async def analytics(body: AnalyticsBody, x_api_key: str = Header(None, alias="X-API-Key")):
    if x_api_key != "ak_yszijq2eseo8gstan0dx9ow8":
        raise HTTPException(status_code=401, detail="Unauthorized")

    events = body.events or []
    total_events = len(events)
    users = [e.get("user") for e in events if e.get("user") is not None]
    unique_users = len(set(users))
    revenue = sum(float(e.get("amount", 0)) for e in events if float(e.get("amount", 0)) > 0)

    totals = defaultdict(float)
    for e in events:
        user = e.get("user")
        amt = float(e.get("amount", 0))
        if user and amt > 0:
            totals[user] += amt

    top_user = max(totals, key=totals.get) if totals else None

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": float(revenue),
        "top_user": top_user,
    }

# ---------------- Q8 Extract ----------------
class ExtractBody(BaseModel):
    text: str

@app.post("/extract")
async def extract(body: ExtractBody):
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="Invalid input")

    vendor_match = re.search(r"([A-Za-z0-9\- ]+(?:Industries Ltd\.|Ltd\.|Inc\.|LLC|Corp\.|Company))", text)
    amount_match = re.search(r"\b(?:USD|EUR|GBP)?\s*([0-9]+(?:\.[0-9]+)?)\b", text)
    currency_match = re.search(r"\b(USD|EUR|GBP)\b", text)
    date_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)

    return {
        "vendor": vendor_match.group(1).strip() if vendor_match else "",
        "amount": float(amount_match.group(1)) if amount_match else 0.0,
        "currency": currency_match.group(1) if currency_match else "USD",
        "date": date_match.group(1) if date_match else "",
    }

# ---------------- Q9 Orders ----------------
@app.post("/orders")
async def create_order(idempotency_key: str = Header(None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key")
    if idempotency_key in IDEMPOTENCY:
        return IDEMPOTENCY[idempotency_key]
    order = {"id": str(uuid4())}
    IDEMPOTENCY[idempotency_key] = order
    return JSONResponse(status_code=201, content=order)

@app.get("/orders")
async def list_orders(limit: int = Query(10, ge=1), cursor: int = Query(0, ge=0), x_client_id: str = Header("default", alias="X-Client-Id")):
    now = time()
    bucket = [t for t in RATE_BUCKETS[x_client_id] if now - t < 10]
    if len(bucket) >= 16:
        raise HTTPException(status_code=429, detail="Rate limit")
    bucket.append(now)
    RATE_BUCKETS[x_client_id] = bucket

    start = int(cursor)
    items = ORDERS[start:start + limit]
    next_cursor = str(start + len(items)) if start + len(items) < len(ORDERS) else None
    return {"items": items, "next_cursor": next_cursor}

# ---------------- Q10 Ping ----------------
@app.get("/ping")
async def ping(request: Request):
    rid = request.headers.get("X-Request-ID") or str(uuid4())
    return JSONResponse(content={"email": EMAIL, "request_id": rid}, headers={"X-Request-ID": rid})
