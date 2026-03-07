from sqlalchemy import Column, String, ForeignKey, DateTime, Index
import datetime
from app.db.base import Base

class Like(Base):
    __tablename__ = "likes"

    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index('ix_likes_post_id', 'post_id'),
    )
