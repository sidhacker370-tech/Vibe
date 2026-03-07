from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Index
import datetime
from app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False) # e.g., 'follow', 'comment', 'mention'
    reference_id = Column(String(36), nullable=False) # The ID of the follower, post, or comment
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index('ix_notifications_user_id', 'user_id'),
    )
