from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.services import follow_service
from app.models.user import User
from app.schemas.user import UserResponse
router = APIRouter()

@router.post("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def follow_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await follow_service.follow_user(db=db, follower_id=current_user.id, following_id=user_id)
    return {"success": True, "message": "User followed successfully"}

@router.delete("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def unfollow_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await follow_service.unfollow_user(db=db, follower_id=current_user.id, following_id=user_id)
    return {"success": True, "message": "User unfollowed successfully"}

@router.get("/{user_id}/followers", response_model=list[UserResponse])
async def get_followers(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    users = await follow_service.get_followers(db=db, user_id=user_id, skip=skip, limit=limit)
    return users

@router.get("/{user_id}/following", response_model=list[UserResponse])
async def get_following(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    users = await follow_service.get_following(db=db, user_id=user_id, skip=skip, limit=limit)
    return users
