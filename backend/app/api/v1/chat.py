from typing import List, Optional
import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# We use async_sessionmaker directly for WS because normal Depends with generation may not work as cleanly in WS exception handling
from app.db.session import AsyncSessionLocal
from app.websockets.manager import manager
from app.services import chat_service
from app.core import security
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import User

router = APIRouter()

async def get_ws_user(token: str, db: AsyncSession) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = payload.get("sub")
    except JWTError:
        return None
    
    if not token_data:
        return None
        
    user = await db.get(User, token_data)
    return user

@router.websocket("/{vibe_id}")
async def websocket_chat_endpoint(websocket: WebSocket, vibe_id: str, token: str = Query(...)):
    async with AsyncSessionLocal() as db:
        user = await get_ws_user(token, db)
        
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid credentials")
            return
            
        try:
            await chat_service.verify_membership_for_chat(db, vibe_id, user.id)
        except HTTPException as e:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=e.detail)
            return
            
        await manager.connect(websocket, vibe_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                # Save into the DB
                saved_message = await chat_service.create_chat_message(
                    db=db,
                    vibe_id=vibe_id,
                    user_id=user.id,
                    content=data
                )
                
                # Broadcast payload
                broadcast_data = {
                    "id": saved_message.id,
                    "vibe_id": vibe_id,
                    "user_id": user.id,
                    "username": user.username,
                    "content": saved_message.content,
                    "created_at": saved_message.created_at.isoformat()
                }
                
                await manager.broadcast_json(broadcast_data, vibe_id)
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, vibe_id)
