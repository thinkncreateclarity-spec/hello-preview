from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Ajay's FastAPI 🚀 - PHASE 1 COMPLETE")

@app.get("/health")
async def health():
    return {"status": "healthy", "pr": "#1"}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1>Ajay's FastAPI 🚀 - PHASE 1 COMPLETE</h1>
    <p>FastAPI deployed successfully on Railway!</p>
    <a href="/docs">Swagger UI</a>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
