from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
class AlertIn(BaseModel):
    title: str = Field(..., max_length=200)
    severity: Literal["low", "medium", "high"]
    source: str | None = None
    details: str | None = None

class AlertReciept(BaseModel):
    id: str
    title: str
    severity: Literal["low", "medium", "high"]
    source: str | None = None
    details: str | None = None
    created_at: datetime

class LoginInfo(BaseModel):
    email: str
    password: str

class AlertUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high"]] = None
    source: Optional[str] = None
    details: Optional[str] = None

