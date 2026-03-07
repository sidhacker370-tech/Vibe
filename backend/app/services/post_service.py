from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
import datetime

from app.models.post import Post
from app.models.vibe import VibeMember, Vibe
from app.schemas.post import PostCreate
from app.services.interest_service import add_interest_score
from app.core.cache import cache_service

async def _check_membership(db: AsyncSession, vibe_id: str, user_id: str):
    # Quick check if user is a member or owner
    vibe = await db.get(Vibe, vibe_id)
    if not vibe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vibe not found",
        )
        
    result = await db.execute(
        select(VibeMember).where(VibeMember.vibe_id == vibe_id, VibeMember.user_id == user_id)
    )
    member = result.scalars().first()
    
    if not member and vibe.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this Vibe",
        )

async def create_post(db: AsyncSession, vibe_id: str, user_id: str, post_in: PostCreate) -> Post:
    await _check_membership(db, vibe_id, user_id)
    
    db_obj = Post(
        vibe_id=vibe_id,
        user_id=user_id,
        content=post_in.content
    )
    db.add(db_obj)
    
    await add_interest_score(db, user_id, vibe_id, 7)
    
    # Add 10 XP on post creation
    from app.models.user import User
    user = await db.get(User, user_id)
    if user:
        user.influence_score += 10
        
    from app.services.analytics_service import log_event
    await log_event(db, user_id, "user_create_post", str(db_obj.id))
    
    await db.commit()
    await db.refresh(db_obj)
    
    await cache_service.delete_prefix(f"feed:user:{user_id}")
    
    return db_obj

async def list_posts(db: AsyncSession, vibe_id: str, user_id: str, cursor: Optional[datetime.datetime] = None, limit: int = 20) -> tuple[List[Post], Optional[datetime.datetime]]:
    await _check_membership(db, vibe_id, user_id)
    
    from sqlalchemy.orm import selectinload
    stmt = select(Post).options(selectinload(Post.user)).where(Post.vibe_id == vibe_id)
    
    from app.utils.pagination import paginate_cursor
    return await paginate_cursor(
        db=db,
        stmt=stmt,
        model=Post,
        cursor=cursor,
        limit=limit,
        cursor_column=Post.created_at
    )
