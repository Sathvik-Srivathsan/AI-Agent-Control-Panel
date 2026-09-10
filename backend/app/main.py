from fastapi import FastAPI
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from app.db.database import init_db, SessionLocal
from app.db.seed import seed_agents
from app.api.routes_agents import router as agents_router
from app.api.routes_runs import router as runs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_agents(db)
    finally:
        db.close()
    yield


app = FastAPI(title="AI Agent Control Panel", version="0.1.0", lifespan=lifespan)
app.include_router(agents_router)
app.include_router(runs_router)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
    }
