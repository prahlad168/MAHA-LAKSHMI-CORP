from fastapi import FastAPI

app = FastAPI(
    title="MAHA Sales Engine API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "status": "running",
        "system": "MAHA Sales Engine"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }