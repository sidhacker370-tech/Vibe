from pydantic import BaseModel
import datetime

class NotificationBase(BaseModel):
    id: str
    user_id: str
    type: str
    reference_id: str
    is_read: bool

class NotificationResponse(NotificationBase):
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: bool
