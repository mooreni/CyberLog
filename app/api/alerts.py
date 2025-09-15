from fastapi import APIRouter
from fastapi import HTTPException
from app.models import AlertIn, AlertReciept
from app.storage import add_alert, get_alert, list_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("/", response_model=AlertReciept)
def create_alert(alert: AlertIn):
    new_id = add_alert(alert)
    reciept = get_alert(new_id)
    if not reciept:
        raise HTTPException(status_code=500, detail="Failed to save alert")
    return reciept

@router.get("/", response_model=list[AlertReciept])
def get_alerts_list(limit: int = 10, offset: int = 0):
    return list_alerts(limit=limit, offset=offset)

@router.get("/{alert_id}", response_model=AlertReciept)
def get_single_alert(alert_id: str):
    alert = get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

