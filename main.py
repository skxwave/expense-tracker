import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka

from src.api.v1 import router as v1_router
from src.core.exceptions_handler import add_exception_handlers
from src.core.ioc import create_container
from src.db import db_session_manager


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
    version="0.0.2",
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
add_exception_handlers(app)
app.include_router(v1_router)

# Setup dishka DI container
container = create_container()
setup_dishka(container, app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        log_config=None,
        host="0.0.0.0",
        reload=True,
        port=8000,
    )
