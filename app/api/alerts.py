from fastapi import APIRouter, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app import storage, models
from app.auth_jwt import verify_access_token

security_scheme = HTTPBearer()

def require_jwt(creds: HTTPAuthorizationCredentials = Security(security_scheme)):
    # 1) Ensure the header is present and formatted as 'Bearer <token>'
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )

    token = creds.credentials

    # 2) Verify the JWT (signature + exp) using our server secret/algorithm
    claims = verify_access_token(token)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    
    return claims

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    dependencies=[Depends(require_jwt)],
)

@router.post("/", response_model=models.AlertReciept)
def create_alert(alert: models.AlertIn):
    new_id = storage.add_alert(alert)
    reciept = storage.get_alert(new_id)
    if not reciept:
        raise HTTPException(status_code=500, detail="Failed to save alert")
    return reciept

@router.get("/", response_model=list[models.AlertReciept])
def get_alerts_list(limit: int = 10, offset: int = 0):
    return storage.list_alerts(limit=limit, offset=offset)

@router.get("/{alert_id}", response_model=models.AlertReciept)
def get_single_alert(alert_id: str):
    alert = storage.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.delete("/{alert_id}")
def delete_single_alert(alert_id: str):
    success = storage.delete_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"detail": f"Alert {alert_id} deleted"}

@router.patch("/{alert_id}", response_model=models.AlertReciept)
def patch_alert_route(alert_id: str, changes: models.AlertUpdate):
    # enforce: at least one field must be provided
    if (
        changes.title is None
        and changes.severity is None
        and changes.source is None
        and changes.details is None
    ):
        raise HTTPException(status_code=400, detail="No fields to update.")

    updated = storage.update_alert(alert_id, changes)
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return updated

@router.put("/{alert_id}", response_model=models.AlertReciept)
def put_alert_route(alert_id: str, new_data: models.AlertIn):
    updated = storage.replace_alert(alert_id, new_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return updated
