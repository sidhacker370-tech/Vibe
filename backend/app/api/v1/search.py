from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.vibe import Vibe
from app.models.post import Post
from app.schemas.user import UserResponse
from app.schemas.vibe import VibeResponse
from app.schemas.post import PostResponse

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(User).where(User.username.ilike(f"%{q}%")).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/vibes", response_model=List[VibeResponse])
async def search_vibes(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Vibe).where(Vibe.name.ilike(f"%{q}%")).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/posts", response_model=List[PostResponse])
async def search_posts(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Depending on Post model, making sure we only return non-deleted posts
    stmt = select(Post).where(Post.content.ilike(f"%{q}%"), getattr(Post, 'is_deleted', False) == False).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
