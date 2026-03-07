from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_interest import UserInterestScore

async def add_interest_score(db: AsyncSession, user_id: str, vibe_id: str, score_delta: float):
    if not vibe_id or not user_id:
        return
        
    stmt = select(UserInterestScore).where(
        UserInterestScore.user_id == user_id, 
        UserInterestScore.vibe_id == vibe_id
    )
    result = await db.execute(stmt)
    interest = result.scalars().first()
    
    if interest:
        interest.score += score_delta
    else:
        interest = UserInterestScore(user_id=user_id, vibe_id=vibe_id, score=score_delta)
        db.add(interest)
        
    # We do not commit here to allow the caller to commit as part of their transaction
