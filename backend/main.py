import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import router as v1_router
from db import db_session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    yield
    # Shutdown: close database connections
    await db_session_manager.close()


app = FastAPI(
    title="Expense Tracker API",
    description="API for tracking expenses with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run(app)
