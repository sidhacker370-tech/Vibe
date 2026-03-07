from typing import Optional, List
from pydantic import BaseModel
import datetime

# Shared properties
class VibeBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties to receive via API on creation
class VibeCreate(VibeBase):
    pass

# Properties to return via API
class VibeInDBBase(VibeBase):
    id: str
    owner_id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class VibeResponse(VibeInDBBase):
    member_count: Optional[int] = 0
    online_count: Optional[int] = 0

class VibeMemberResponse(BaseModel):
    vibe_id: str
    user_id: str
    joined_at: datetime.datetime

    class Config:
        from_attributes = True
