from sqlalchemy import Column, String, ForeignKey, DateTime, Index
import uuid
import datetime
from app.db.base import Base

class Vibe(Base):
    __tablename__ = "vibes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class VibeMember(Base):
    __tablename__ = "vibe_members"

    vibe_id = Column(String(36), ForeignKey("vibes.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(20), default="member") # owner, admin, member
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index('ix_vibe_members_vibe_user', 'vibe_id', 'user_id'),
    )
