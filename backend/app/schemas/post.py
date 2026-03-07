from typing import Optional, List
from pydantic import BaseModel
import datetime

# Shared properties
class PostBase(BaseModel):
    content: str

# Properties to receive via API on creation
class PostCreate(PostBase):
    pass

# Properties to return via API
class PostInDBBase(PostBase):
    id: str
    vibe_id: str
    user_id: str
    created_at: datetime.datetime
    likes_count: int
    comments_count: int
    score: float

    class Config:
        from_attributes = True

class PostUserResponse(BaseModel):
    id: str
    username: str
    influence_score: int
    vibe_score: Optional[int] = 0

    class Config:
        from_attributes = True

class PostResponse(PostInDBBase):
    user: Optional[PostUserResponse] = None

class PaginatedPostResponse(BaseModel):
    items: List[PostResponse]
    next_cursor: Optional[datetime.datetime] = None
