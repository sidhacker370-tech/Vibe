from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_event import UserEvent

async def log_event(db: AsyncSession, user_id: str, event_type: str, target_id: str):
    """
    Log an analytics event.
    Events: user_join_vibe, user_create_post, user_comment, user_like, user_open_chat
    """
    db_obj = UserEvent(
        user_id=user_id,
        event_type=event_type,
        target_id=target_id
    )
    db.add(db_obj)
    # We commit these usually flush with the main action, but to be safe if not:
    # No commit here so it attaches to caller's transaction
