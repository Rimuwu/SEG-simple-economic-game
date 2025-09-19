from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from global_modules.api_configurate import get_fastapi_app
from global_modules.logs import main_logger

# Импортируем роуты
from routers import connect_ws

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    main_logger.info("API is starting up...")
    main_logger.info("Creating missing tables on startup...")
    yield

    # Shutdown

app = get_fastapi_app(
    title="API",
    version="1.0.0",
    description="SEG API",
    debug=False,
    lifespan=lifespan,
    limiter=False,
    middlewares=[],
    routers=[
        connect_ws.router
    ],
    api_logger=main_logger
)

@app.get("/")
async def root(request: Request):
    return {"message": f"{app.description} is running! v{app.version}"}
