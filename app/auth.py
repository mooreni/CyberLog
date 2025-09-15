from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional

# in-memory token store: token -> {email, expires_at}
_tokens: dict[str, dict[str, object]] = {}

TOKEN_TTL_MINUTES = 60  # tokens live for 1 hour

def issue_token(email: str) -> dict:
    """Create a new access token for this email and return token info."""
    token = secrets.token_urlsafe(32)  # random, URL-safe string
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES)
    _tokens[token] = {"email": email, "expires_at": expires_at}
    return {"access_token": token, "token_type": "bearer", "expires_at": expires_at}

def verify_token(token: str) -> Optional[dict]:
    """Return user info if token is valid, otherwise None."""
    info = _tokens.get(token)
    if not info:
        return None

    expires_at = info["expires_at"]
    if isinstance(expires_at, datetime) and expires_at < datetime.now(timezone.utc):
        _tokens.pop(token, None)
        return None

    return {
        "email": str(info["email"]),
        "status": "logged in",
        "expires_at": expires_at
    }

def revoke_token(token: str) -> bool:
    """Remove a token from the store. Return True if it existed and was removed."""
    return _tokens.pop(token, None) is not None