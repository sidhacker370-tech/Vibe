from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List, Optional
import datetime

from app.models.message import Message
from app.models.vibe import VibeMember, Vibe
from app.utils.pagination import paginate_cursor

async def verify_membership_for_chat(db: AsyncSession, vibe_id: str, user_id: str):
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

async def create_chat_message(db: AsyncSession, vibe_id: str, user_id: str, content: str) -> Message:
    await verify_membership_for_chat(db, vibe_id, user_id)
    
    db_obj = Message(
        vibe_id=vibe_id,
        user_id=user_id,
        content=content
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def list_chat_messages(db: AsyncSession, vibe_id: str, user_id: str, cursor: Optional[datetime.datetime] = None, limit: int = 50) -> tuple[List[Message], Optional[datetime.datetime]]:
    await verify_membership_for_chat(db, vibe_id, user_id)
    
    stmt = select(Message).where(Message.vibe_id == vibe_id)
    
    from app.utils.pagination import paginate_cursor
    return await paginate_cursor(
        db=db,
        stmt=stmt,
        model=Message,
        cursor=cursor,
        limit=limit,
        cursor_column=Message.created_at
    )
