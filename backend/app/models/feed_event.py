from sqlalchemy import Column, String, ForeignKey, DateTime
import uuid
import datetime
from app.db.base import Base

class FeedEvent(Base):
    __tablename__ = "feed_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False) # e.g., 'view', 'like', 'comment', 'share', 'click_profile'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
