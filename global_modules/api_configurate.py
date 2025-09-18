from fastapi import APIRouter, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

def get_fastapi_app(
        title: str,
        version: str,
        description: str,
        debug: bool = False,
        limiter: bool = False,
        lifespan: any = None,
        middlewares: list[BaseHTTPMiddleware] = None,
        routers: list[APIRouter] = None,
        api_logger = None
    ):
    """Создание FastAPI приложения с базовыми настройками"""

    app = FastAPI(
        title=title,
        version=version,
        description=description,
        debug=debug,
        lifespan=lifespan
    )

    if api_logger:
        app.state.logger = api_logger

    if limiter: 
        from global_modules.limiter import setup_rate_limiter
        setup_rate_limiter(app)

    for middleware in middlewares:
        app.add_middleware(middleware)

    for router in routers:
        app.include_router(router)

    return app