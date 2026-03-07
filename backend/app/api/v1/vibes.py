from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.vibe import VibeCreate, VibeResponse, VibeMemberResponse
from app.schemas.post import PostCreate, PostResponse, PaginatedPostResponse
from app.api.deps import get_db, get_current_user
from app.services import vibe_service, post_service
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=VibeResponse, status_code=status.HTTP_201_CREATED)
async def create_vibe(
    vibe_in: VibeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await vibe_service.create_vibe(db=db, vibe_in=vibe_in, user_id=current_user.id)

@router.post("/{vibe_id}/join", response_model=VibeMemberResponse)
async def join_vibe(
    vibe_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await vibe_service.join_vibe(db=db, vibe_id=vibe_id, user_id=current_user.id)

@router.get("/", response_model=List[VibeResponse])
async def read_vibes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await vibe_service.list_vibes(db=db)

@router.get("/trending", response_model=List[VibeResponse])
async def get_trending_vibes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vibes = await vibe_service.list_vibes(db=db)
    # Sort by member count for trending
    return sorted(vibes, key=lambda v: v.member_count, reverse=True)[:5]
    
@router.get("/new", response_model=List[VibeResponse])
async def get_new_vibes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vibes = await vibe_service.list_vibes(db=db)
    # Sort by recent creation
    return sorted(vibes, key=lambda v: v.created_at, reverse=True)[:5]

@router.get("/{vibe_id}", response_model=VibeResponse)
async def read_vibe(
    vibe_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await vibe_service.get_vibe(db=db, vibe_id=vibe_id, user_id=current_user.id)

@router.delete("/{vibe_id}", status_code=status.HTTP_200_OK)
async def delete_vibe(
    vibe_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await vibe_service.delete_vibe(db=db, vibe_id=vibe_id, user_id=current_user.id)
    return {"success": True, "message": "Vibe deleted successfully"}

# Post endpoints nested under vibes
@router.post("/{vibe_id}/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_vibe_post(
    vibe_id: str,
    post_in: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await post_service.create_post(db=db, vibe_id=vibe_id, user_id=current_user.id, post_in=post_in)

@router.get("/{vibe_id}/posts", response_model=PaginatedPostResponse)
async def read_vibe_posts(
    vibe_id: str,
    cursor: Optional[datetime.datetime] = Query(None, description="Cursor for pagination (ISO 8601 datetime format)"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items, next_cursor = await post_service.list_posts(
        db=db, 
        vibe_id=vibe_id, 
        user_id=current_user.id, 
        cursor=cursor, 
        limit=limit
    )
    return {"items": items, "next_cursor": next_cursor}
