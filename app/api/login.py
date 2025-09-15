from fastapi import APIRouter, HTTPException, Depends, status
from app.auth_jwt import create_access_token, JWT_TTL_MIN
from app.api.alerts import require_jwt
from app.models import LoginModel


router = APIRouter(prefix="/login", tags=["auth"])


_VALID_EMAIL = "user@example.com"
_VALID_PASSWORD = "secret123"


@router.post("/", summary="Login and receive a JWT")
def login(login_req: LoginModel):
    if login_req.email != _VALID_EMAIL or login_req.password != _VALID_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(sub=login_req.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_TTL_MIN  # seconds
    }


@router.get("/me", summary="Show info about the current user")
def who_am_i(current_user = Depends(require_jwt)):
    return {"you_are": current_user["sub"]}