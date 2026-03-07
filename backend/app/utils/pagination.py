from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar("T")

class PaginatedParams(BaseModel):
    cursor: Optional[datetime.datetime] = None
    limit: int = 20

async def paginate_cursor(
    db: AsyncSession,
    stmt: Any,
    model: Any,
    cursor: Optional[datetime.datetime],
    limit: int,
    cursor_column: Any
) -> tuple[List[Any], Optional[datetime.datetime]]:
    """
    Standard reusable cursor-based pagination helper.
    Assumes descending order for chronological feeds.
    """
    if cursor:
        stmt = stmt.where(cursor_column < cursor)
        
    stmt = stmt.order_by(cursor_column.desc()).limit(limit)
    
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    next_cursor = None
    if items and len(items) == limit:
        # We got a full page, grab the last item's cursor value using dict mapping or getattr
        last_item = items[-1]
        next_cursor = getattr(last_item, cursor_column.name)
        
    return items, next_cursor
