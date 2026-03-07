from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.message import Message
from app.models.follow import Follow
from app.models.notification import Notification
from app.models.comment import Comment
from app.models.like import Like
from app.models.feed_event import FeedEvent
from app.models.user_interest import UserInterestScore
from app.models.user_event import UserEvent
