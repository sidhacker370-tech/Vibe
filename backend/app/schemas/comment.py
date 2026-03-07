from pydantic import BaseModel
import datetime

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: str
    post_id: str
    user_id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
