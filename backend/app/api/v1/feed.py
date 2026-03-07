from typing import Optional
import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.services import feed_service
from app.models.user import User
from app.schemas.post import PaginatedPostResponse, PostResponse
from app.core.cache import cache_service

router = APIRouter()

@router.get("/", response_model=PaginatedPostResponse)
async def get_feed(
    cursor: Optional[datetime.datetime] = Query(None, description="Cursor for pagination (ISO 8601 datetime format)"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cursor_str = str(cursor.timestamp()) if cursor else 'none'
    cache_key = f"feed:user:{current_user.id}:{cursor_str}:{limit}"
    
    cached_feed = await cache_service.get(cache_key)
    if cached_feed:
        return cached_feed
        
    items, next_cursor = await feed_service.get_user_feed(
        db=db,
        user_id=current_user.id,
        cursor=cursor,
        limit=limit
    )
    
    # Needs dict serialization for cache
    # Serialize datetime to isoformat
    items_dict = []
    for item in items:
        # Pydantic schema validation happens here first manually or we just let it pass through the router?
        # Actually it's easier to cache the response object, but router validates it after.
        pass 
        
    # We can use the schema to dump it safely
    response_data = {
        "items": [PostResponse.model_validate(item).model_dump() for item in items],
        "next_cursor": next_cursor.isoformat() if next_cursor else None
    }
    
    # Store with stringified datetime 
    # TTL config: 60 seconds as requested
    await cache_service.set(cache_key, response_data, ttl_seconds=60)
    
    return response_data
