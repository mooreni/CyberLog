# app/api/login.py
from fastapi import APIRouter, HTTPException, Depends
from app.models import LoginModel
from app.auth import issue_token, revoke_token
from app.api.alerts import require_token


router = APIRouter(prefix="/login", tags=["auth"])

# super-simple hardcoded user for now (interview-speed)
_VALID_EMAIL = "user@example.com"
_VALID_PASSWORD = "secret123"

@router.post("/", summary="Login and receive an access token")
def login(login_req: LoginModel):
    # validate credentials (replace with real check later)
    if login_req.email != _VALID_EMAIL or login_req.password != _VALID_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # issue a token and return it
    token_info = issue_token(login_req.email)
    return token_info

@router.get("/me", summary="Show info about the current user")
def read_me(user=Depends(require_token)):
    # user is whatever require_token() returned (dict with email/status/expires_at)
    return user

@router.post("/logout", summary="Revoke current access token")
def logout(user=Depends(require_token)):
    tok = user.get("token")
    if not tok:
        # Shouldn't happen in our setup, but being defensive
        raise HTTPException(status_code=400, detail="No token to revoke.")
    tok_exists = revoke_token(tok)
    if not tok_exists:
        # Token was already gone or invalid
        return {"message": "Token already invalid."}
    return {"message": "Logged out."}