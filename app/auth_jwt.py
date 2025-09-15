import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import jwt 
from typing import Optional, Dict, Any

# Load .env values into environment
load_dotenv()

# Read config
JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-insecure-secret-change-me")
JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
JWT_TTL_MIN: int = int(os.getenv("JWT_TTL_MIN", "60"))

def _now_utc():
    return datetime.now(timezone.utc)

def create_access_token(sub: str, ttl_min: int = JWT_TTL_MIN) -> str:
    now = _now_utc()
    exp = now + timedelta(minutes=ttl_min)

    payload = {
        "sub": sub,                 # subject: who the token belongs to
        "iat": int(now.timestamp()),# issued at (seconds since epoch)
        "exp": int(exp.timestamp()) # expiry time
    }

    # jwt.encode returns the compact JWT string
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify signature and expiry.
    Return the decoded claims (dict) if valid, else None.
    """
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        # claims is a dict like {"sub": "...", "iat": 123, "exp": 456}
        return claims
    except jwt.ExpiredSignatureError:
        # token's exp time is in the past
        return None
    except jwt.InvalidTokenError:
        # signature mismatch, wrong format, wrong alg, etc.
        return None