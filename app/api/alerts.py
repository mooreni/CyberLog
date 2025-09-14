from fastapi import APIRouter
from fastapi import HTTPException
from app.models import AlertIn, AlertReciept
from app.storage import add_alert, get_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("/", response_model=AlertReciept)
def create_alert(alert: AlertIn):
    new_id = add_alert(alert)
    reciept = get_alert(new_id)
    if not reciept:
        raise HTTPException(status_code=500, detail="Failed to save alert")
    return reciept