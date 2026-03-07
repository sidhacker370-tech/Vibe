from sqlalchemy import Column, String, ForeignKey, DateTime, Index, Boolean, Integer, Float
import uuid
import datetime
from app.db.base import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vibe_id = Column(String(36), ForeignKey("vibes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    from sqlalchemy.orm import relationship
    user = relationship("User", foreign_keys=[user_id])

    # Adding the requested composite index for fast cursor pagination
    __table_args__ = (
        Index('ix_posts_vibe_id_created_at', 'vibe_id', 'created_at'),
    )
