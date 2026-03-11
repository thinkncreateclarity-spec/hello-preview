from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import uvicorn

app = FastAPI(title="Ajay's Task Tracker API")

@app.get("/", response_class=HTMLResponse)
async def root():
    pr = os.environ.get('PR_NUMBER', 'main')
    return f"""
    <h1>Ajay's FastAPI 🚀 - PHASE 1 COMPLETE</h1>
    <h2>Multi-Service Task Tracker Backend</h2>
    <p>PR #{pr} live on Railway!</p>
    <p><a href="/docs">FastAPI Swagger UI → /docs</a></p>
    <p>Next: Phase 2 → Postgres + CRUD Tasks</p>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "pr": os.environ.get('PR_NUMBER', 'main')}

@app.post("/tasks")
async def create_task(task: str):
    return {"id": 42, "task": task, "status": "created"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
