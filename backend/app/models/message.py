from sqlalchemy import Column, String, ForeignKey, DateTime, Index
import uuid
import datetime
from app.db.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vibe_id = Column(String(36), ForeignKey("vibes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # SET NULL so if user deletes account, message remains
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index('ix_messages_vibe_id_created_at', 'vibe_id', 'created_at'),
    )
