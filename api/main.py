# from fastapi import FastAPI, Request
# from contextlib import asynccontextmanager

# from global_modules.api_configurate import get_fastapi_app
# from global_modules.logs import brain_logger

# # Импортируем роуты
# from routers.game_data import router as game_data_router

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     brain_logger.info("API is starting up...")
#     brain_logger.info("Creating missing tables on startup...")
#     yield

#     # Shutdown

# app = get_fastapi_app(
#     title="API",
#     version="1.0.0",
#     description="Brain API",
#     debug=False,
#     lifespan=lifespan,
#     limiter=False,
#     middlewares=[],
#     routers=[
#         game_data_router,
#     ],
#     api_logger=brain_logger
# )
# # app.add_middleware(RequestLoggingMiddleware, logger=brain_logger)

# @app.get("/")
# async def root(request: Request):
#     return {"message": f"{app.description} is running! v{app.version}"}

from modules.json_database import JSONDatabase, db_sessions
from modules.session import Session

if db_sessions.get_tables() == []:
    db_sessions.create_table('sessions')

session = db_sessions.find_one('sessions')
print(session)

if session is None:
    new_session = Session()
    print("New session created with ID:", new_session.session_id)
else:
    existing_session = Session(session['session_id'])
    print("Loaded existing session with ID:", existing_session.session_id)