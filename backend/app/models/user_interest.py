from sqlalchemy import Column, String, Float, DateTime, Index
from app.db.base import Base
import datetime

class UserInterestScore(Base):
    __tablename__ = "user_interest_scores"

    user_id = Column(String(36), primary_key=True)
    vibe_id = Column(String(36), primary_key=True)
    score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        Index('idx_interest_user_vibe', 'user_id', 'vibe_id'),
    )
