from fastapi import FastAPI, Request
import jwt

app = FastAPI()

# Yeh wo Public Key hai jo aapke assignment mein di gayi hai
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAQEA2okOhSpNjga+2rTLbeuY
cxIP/hGBC6Sb9iwg3yIAA4HCnpITcbWCSeIbvbYGuc3EBny4xFyf5Cbj5DHJMlD
Ekry0gyd2giIII BOUB j8S63UgCnRpOBH9NFatfNwh eKuzsPuVNLdu6A9cNteNpXc
W yjG2axVFmq7i6SuKr1JOWYG7xTTAVKPuj5140tsQF03h5NepzdfXpr2BoNnzFw
ed+zcLR6BcmNno/WVfJ4xycLSf08BCQgdTgW6PdaChd119VDetJZVEgC5tkyvXsFI
SI6iyrYbKRONebSq q4XKade jsCs4F1RncsS4Lligni7G1kL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

# Yeh rules hain jo token ko check karne ke liye chahiye
EXPECTED_ISSUER = "https://idp.exam.local"
EXPECTED_AUDIENCE = "tds-hxbe6r1c.apps.exam.local"

@app.post("/verify")
async def verify_token(request: Request):
    data = await request.json()
    token = data.get("token")
    
    try:
        # JWT verify karna (signature, issuer, audience, expiry)
        payload = jwt.decode(
            token, 
            PUBLIC_KEY, 
            algorithms=["RS256"],
            issuer=EXPECTED_ISSUER,
            audience=EXPECTED_AUDIENCE
        )
        # Agar token sahi hai, toh ye return karo
        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud")
        }
    except:
        # Agar token galti hai (tampered, expired, etc), toh ye return karo
        return {"valid": False}
