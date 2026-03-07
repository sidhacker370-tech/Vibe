from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.vibe import Vibe, VibeMember
from app.schemas.vibe import VibeCreate
from app.services.interest_service import add_interest_score
from app.core.cache import cache_service

async def create_vibe(db: AsyncSession, vibe_in: VibeCreate, user_id: str) -> Vibe:
    db_obj = Vibe(
        name=vibe_in.name,
        description=vibe_in.description,
        owner_id=user_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)

    # Immediately make the creator an owner member
    member_obj = VibeMember(vibe_id=db_obj.id, user_id=user_id, role="owner")
    db.add(member_obj)
    
    await add_interest_score(db, user_id, db_obj.id, 10)
    from app.services.analytics_service import log_event
    await log_event(db, user_id, "user_create_vibe", db_obj.id)
    
    await db.commit()
    await cache_service.delete_prefix(f"feed:user:{user_id}")

    return db_obj

async def join_vibe(db: AsyncSession, vibe_id: str, user_id: str) -> VibeMember:
    # First ensure the vibe exists:
    vibe = await db.get(Vibe, vibe_id)
    if not vibe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vibe not found",
        )
        
    # Check if already a member:
    result = await db.execute(
        select(VibeMember).where(VibeMember.vibe_id == vibe_id, VibeMember.user_id == user_id)
    )
    existing_member = result.scalars().first()
    if existing_member:
        return existing_member

    # Create new membership
    member_obj = VibeMember(vibe_id=vibe_id, user_id=user_id)
    db.add(member_obj)
    
    await add_interest_score(db, user_id, vibe_id, 10)
    
    # Add XP for joining vibe (Level progression)
    from app.models.user import User
    user = await db.get(User, user_id)
    if user:
        user.influence_score += 3
        
    from app.services.analytics_service import log_event
    await log_event(db, user_id, "user_join_vibe", vibe_id)
    
    await db.commit()
    await db.refresh(member_obj)
    
    await cache_service.delete_prefix(f"feed:user:{user_id}")

    return member_obj


async def list_vibes(db: AsyncSession) -> list[Vibe]:
    # We will fetch all vibes and manually attach member count
    from sqlalchemy import func
    stmt = select(Vibe, func.count(VibeMember.user_id).label('member_count')).outerjoin(VibeMember, Vibe.id == VibeMember.vibe_id).group_by(Vibe.id)
    result = await db.execute(stmt)
    rows = result.all()
    
    vibes_ret = []
    import random
    for vibe, m_count in rows:
        vibe.member_count = m_count
        # Simple heuristic for online count: randomly 10-40% of members
        vibe.online_count = max(1, int(m_count * random.uniform(0.1, 0.4))) if m_count > 0 else 0
        vibes_ret.append(vibe)
    
    return vibes_ret

async def get_vibe(db: AsyncSession, vibe_id: str, user_id: str) -> Vibe:
    # Check if vibe exists
    vibe = await db.get(Vibe, vibe_id)
    if not vibe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vibe not found",
        )

    # Membership check: must exist in VibeMember
    result = await db.execute(
        select(VibeMember).where(VibeMember.vibe_id == vibe_id, VibeMember.user_id == user_id)
    )
    member = result.scalars().first()
    
    if not member and vibe.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this Vibe",
        )
        
    return vibe

async def delete_vibe(db: AsyncSession, vibe_id: str, user_id: str) -> None:
    vibe = await db.get(Vibe, vibe_id)
    if not vibe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vibe not found",
        )
        
    result = await db.execute(
        select(VibeMember).where(VibeMember.vibe_id == vibe_id, VibeMember.user_id == user_id, VibeMember.role == "owner")
    )
    owner = result.scalars().first()
    
    if not owner and vibe.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the vibe owner can delete this vibe",
        )
        
    await db.delete(vibe)
    await db.commit()
