from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.session import get_db
from app.api.v1 import auth, vibes, chat, users, feed, notifications, posts, search
from app.core.logging import RequestLoggingMiddleware
from app.core.cache import cache_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache_service.connect()
    yield

app = FastAPI(title="Vibe API", lifespan=lifespan)

# Add logging
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's dev, allow all temporarily.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(vibes.router, prefix="/api/v1/vibes", tags=["vibes"])
app.include_router(chat.router, prefix="/ws/vibes", tags=["chat"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(feed.router, prefix="/api/v1/feed", tags=["feed"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import (
    AppException,
    custom_http_exception_handler,
    app_exception_handler,
    validation_exception_handler,
    global_exception_handler
)

app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"status": "ok", "db_result": result.scalar()}
