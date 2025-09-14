from fastapi import FastAPI
from app.api import alerts

app = FastAPI(title="RSecurity Project")
app.include_router(alerts.router)

@app.get("/health")
def health_check():
    return {"status":"I'm alive!"}

    