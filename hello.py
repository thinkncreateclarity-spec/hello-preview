from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy", "pr": "#1"}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1>Ajay's FastAPI 🚀 - PHASE 1 LIVE!</h1>
    <p>✅ Railway PR environment + gunicorn + FastAPI</p>
    <a href="/docs">Swagger UI</a>
    """

@app.get("/docs")
async def docs():
    return {"message": "Visit /docs for Swagger UI"}
