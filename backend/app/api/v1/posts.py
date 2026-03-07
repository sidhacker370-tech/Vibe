from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import datetime
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.models.notification import Notification
from app.models.feed_event import FeedEvent
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.interest_service import add_interest_score
from app.services.analytics_service import log_event
from app.core.cache import cache_service
from app.models.vibe import VibeMember

router = APIRouter()

@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: str,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = await db.get(Post, post_id)
    if not post or post.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_in.content
    )
    db.add(new_comment)
    
    post.comments_count += 1
    post.score = (post.likes_count * 2) + (post.comments_count * 3)
    
    # Trigger notification and update author influence
    if post.user_id != current_user.id:
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=post.user_id,
            type="comment",
            reference_id=post_id
        )
        db.add(notif)
        
        # +3 influence to post author for receiving a comment
        author = await db.get(User, post.user_id)
        if author:
            author.influence_score += 3
        
    # Log Feed Event
    feed_event = FeedEvent(
        user_id=current_user.id,
        post_id=post_id,
        event_type="comment"
    )
    db.add(feed_event)
    
    # Update interest score
    await add_interest_score(db, current_user.id, post.vibe_id, 5)
    
    # Update current user influence score (XP) for commenting
    current_user.influence_score += 5
    
    from app.services.analytics_service import log_event
    await log_event(db, current_user.id, "user_comment", str(new_comment.id))
        
    await db.commit()
    await db.refresh(new_comment)
    
    await cache_service.delete_prefix(f"feed:user:{current_user.id}")
    
    return new_comment

@router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    post_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id, Comment.is_deleted == False)
        .order_by(Comment.created_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/{post_id}/like")
async def like_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = await db.get(Post, post_id)
    if not post or post.is_deleted:
        raise HTTPException(status_code=404, detail="Post not found")
        
    existing = await db.execute(select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id))
    if not existing.scalars().first():
        new_like = Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        
        post.likes_count += 1
        post.score = (post.likes_count * 2) + (post.comments_count * 3)
        
        if post.user_id != current_user.id:
            author = await db.get(User, post.user_id)
            if author:
                author.influence_score += 2
        
        feed_event = FeedEvent(
            user_id=current_user.id,
            post_id=post_id,
            event_type="like"
        )
        db.add(feed_event)
        
        # Update interest score
        await add_interest_score(db, current_user.id, post.vibe_id, 3)
        
        await db.commit()
        await cache_service.delete_prefix(f"feed:user:{current_user.id}")
        
    return {"success": True}

@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = await db.get(Post, post_id)
    if not post or post.is_deleted:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Later we will add admin checking, for now check ownership
    if post.user_id != current_user.id:
        # Check if owner/admin of vibe
        from app.models.vibe import VibeMember
        member = await db.execute(select(VibeMember).where(
            VibeMember.vibe_id == post.vibe_id,
            VibeMember.user_id == current_user.id,
            VibeMember.role.in_(["owner", "admin"]) # Based on Role System to be added
        ))
        if not member.scalars().first():
            raise HTTPException(status_code=403, detail="Forbidden")

    post.is_deleted = True
    await db.commit()
    return {"success": True}

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = await db.get(Comment, comment_id)
    if not comment or comment.is_deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    comment.is_deleted = True
    
    post = await db.get(Post, comment.post_id)
    if post:
        post.comments_count = max(0, post.comments_count - 1)
        post.score = (post.likes_count * 2) + (post.comments_count * 3)
        
        # Optionally deduct influence if we want perfectly matched decrement, but usually we just leave it for now, 
        # or we decrement it safely. Let's do it safely.
        if post.user_id != current_user.id:
            author = await db.get(User, post.user_id)
            if author:
                author.influence_score = max(0, author.influence_score - 3)

    await db.commit()
    return {"success": True}

@router.post("/{post_id}/view")
async def view_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = await db.get(Post, post_id)
    if not post or post.is_deleted:
        raise HTTPException(status_code=404, detail="Post not found")
        
    feed_event = FeedEvent(
        user_id=current_user.id,
        post_id=post_id,
        event_type="view"
    )
    db.add(feed_event)
    
    # Update interest score
    await add_interest_score(db, current_user.id, post.vibe_id, 1)
    
    await db.commit()
    return {"success": True}

