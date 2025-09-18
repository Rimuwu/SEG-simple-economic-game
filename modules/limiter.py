from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

# Кастомный обработчик ошибок
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Обработчик превышения лимита"""
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Превышен лимит запросов", 
            "detail": f"{exc.detail}",
            "message": "Слишком много запросов. Попробуйте позже."
        }
    )
    return response

def setup_rate_limiter(app):
    """Настройка rate limiter в приложении"""

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)
    return limiter
