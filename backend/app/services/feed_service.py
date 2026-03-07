from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import case, desc
from typing import List, Optional
import datetime

from app.models.post import Post
from app.models.vibe import VibeMember
from app.models.follow import Follow
from app.models.user_interest import UserInterestScore
from app.utils.pagination import paginate_cursor

async def get_user_feed(
    db: AsyncSession, 
    user_id: str, 
    cursor: Optional[datetime.datetime] = None, 
    limit: int = 20
) -> tuple[List[Post], Optional[datetime.datetime]]:
    
    # Get user's vibes
    user_vibes_subquery = select(VibeMember.vibe_id).where(VibeMember.user_id == user_id)
    
    # Get user's followed users
    followed_users_subquery = select(Follow.following_id).where(Follow.follower_id == user_id)
    
    priority_expr = case(
        (Post.user_id.in_(followed_users_subquery), 10),
        (Post.vibe_id.in_(user_vibes_subquery), 5),
        else_=0
    ).label('relevance_score')
    
    # Subquery for user interest
    interest_subq = select(UserInterestScore.score).where(
        UserInterestScore.user_id == user_id,
        UserInterestScore.vibe_id == Post.vibe_id
    ).scalar_subquery()
    
    # Base query for all posts (including remaining posts) with soft delete check
    from sqlalchemy.orm import selectinload
    stmt = select(Post).options(selectinload(Post.user))
    
    if hasattr(Post, 'is_deleted'):
        stmt = stmt.where(Post.is_deleted == False)

    if cursor:
        stmt = stmt.where(Post.created_at < cursor)
        
    # Order by combined engagement + relevance score + dynamic interest score, then chronologically for recency
    # Coalesce interest score to 0.0 if not found
    from sqlalchemy.sql.functions import coalesce
    interest_expr = coalesce(interest_subq, 0.0)
    
    stmt = stmt.order_by(desc(Post.score + priority_expr + interest_expr), desc(Post.created_at)).limit(limit)
    
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    if items:
        # Fetch vibe scores for these posts
        post_pairs = [(p.user_id, p.vibe_id) for p in items]
        if post_pairs:
            from sqlalchemy import tuple_
            # We can just fetch user interest scores for the current user to display their vibes
            # But the requirement says "identity of the author in that vibe" -> user_id = post.user_id
            # So query scores for these authors.
            score_stmt = select(UserInterestScore).where(
                tuple_(UserInterestScore.user_id, UserInterestScore.vibe_id).in_(post_pairs)
            )
            score_res = await db.execute(score_stmt)
            scores = {(s.user_id, s.vibe_id): s.score for s in score_res.scalars().all()}
            
            for post in items:
                vibe_score = scores.get((post.user_id, post.vibe_id), 0.0)
                if post.user:
                    post.user.vibe_score = int(vibe_score)
    
    next_cursor = None
    if items and len(items) == limit:
        last_item = items[-1]
        next_cursor = last_item.created_at
        
    return items, next_cursor
