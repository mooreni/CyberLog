from fastapi import FastAPI
app = FastAPI(title="RSecurity Project")
@app.get("/health")
def health_check():
    return {"status":"I'm alive!"}

    