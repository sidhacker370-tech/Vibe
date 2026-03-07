from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.follow import Follow
from app.models.user import User
from app.core.cache import cache_service

async def follow_user(db: AsyncSession, follower_id: str, following_id: str) -> None:
    if follower_id == following_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself")
        
    user = await db.get(User, following_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    result = await db.execute(select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id))
    existing = result.scalars().first()
    
    if existing:
        return # Already following
        
    db_obj = Follow(follower_id=follower_id, following_id=following_id)
    db.add(db_obj)
    
    # +10 influence for gaining a follower
    user.influence_score += 10
    
    # Create notification
    from app.models.notification import Notification
    import uuid
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=following_id,
        type="follow",
        reference_id=follower_id
    )
    db.add(notif)
    
    await db.commit()
    await cache_service.delete_prefix(f"feed:user:{follower_id}")

async def unfollow_user(db: AsyncSession, follower_id: str, following_id: str) -> None:
    result = await db.execute(select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id))
    existing = result.scalars().first()
    
    if existing:
        await db.delete(existing)
        
        user = await db.get(User, following_id)
        if user:
            user.influence_score = max(0, user.influence_score - 10)
            
        await db.commit()
        await cache_service.delete_prefix(f"feed:user:{follower_id}")

async def get_followers(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 20):
    query = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_following(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 20):
    query = (
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()
