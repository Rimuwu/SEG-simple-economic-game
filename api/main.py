from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from global_modules.api_configurate import get_fastapi_app
from global_modules.logs import brain_logger

# Импортируем роуты


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    brain_logger.info("API is starting up...")
    brain_logger.info("Creating missing tables on startup...")
    yield

    # Shutdown

app = get_fastapi_app(
    title="API",
    version="1.0.0",
    description="Brain API",
    debug=False,
    lifespan=lifespan,
    limiter=False,
    middlewares=[],
    routers=[

    ],
    api_logger=brain_logger
)
# app.add_middleware(RequestLoggingMiddleware, logger=brain_logger)

@app.get("/")
async def root(request: Request):
    return {"message": f"{app.description} is running! v{app.version}"}
