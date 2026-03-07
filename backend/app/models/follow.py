from sqlalchemy import Column, String, ForeignKey, DateTime, Index
import datetime
from app.db.base import Base

class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    following_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index('ix_follows_follower_following', 'follower_id', 'following_id'),
    )
