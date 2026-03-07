from sqlalchemy import Column, String, DateTime, Index
import uuid
import datetime
from app.db.base import Base

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    target_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_user_events_user_event', 'user_id', 'event_type'),
    )
