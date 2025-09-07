"""
Collaboration API Routes for Proyecto Semilla
REST endpoints for managing collaboration rooms and sessions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.collaboration import (
    CollaborationRoom, RoomParticipant, RoomMessage,
    UserCursor, CollaborativeSession
)
from app.core.security import get_current_user


router = APIRouter(prefix="/api/v1/collaboration", tags=["collaboration"])


# Pydantic Models
class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    max_participants: Optional[int] = 10
    room_type: Optional[str] = "general"
    settings: Optional[dict] = {}


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None
    is_active: Optional[bool] = None
    settings: Optional[dict] = None


class MessageCreate(BaseModel):
    content: str
    message_type: Optional[str] = "text"
    metadata: Optional[dict] = {}


class CursorUpdate(BaseModel):
    document_id: str
    position_x: Optional[int] = 0
    position_y: Optional[int] = 0
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    color: Optional[str] = "#007bff"


# Room Management Endpoints
@router.post("/rooms", response_model=dict)
async def create_room(
    room_data: RoomCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new collaboration room"""
    room_id = str(uuid.uuid4())

    room = CollaborationRoom(
        id=room_id,
        name=room_data.name,
        description=room_data.description,
        tenant_id=current_user.get("tenant_id", "default"),
        created_by=current_user["id"],
        max_participants=room_data.max_participants,
        room_type=room_data.room_type,
        settings=room_data.settings
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return {
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "created_at": room.created_at.isoformat(),
        "message": "Room created successfully"
    }


@router.get("/rooms", response_model=List[dict])
async def list_rooms(
    skip: int = 0,
    limit: int = 50,
    room_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List collaboration rooms"""
    query = db.query(CollaborationRoom).filter(
        CollaborationRoom.tenant_id == current_user.get("tenant_id", "default")
    )

    if room_type:
        query = query.filter(CollaborationRoom.room_type == room_type)

    rooms = query.offset(skip).limit(limit).all()

    return [
        {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "room_type": room.room_type,
            "max_participants": room.max_participants,
            "is_active": room.is_active,
            "participant_count": len(room.participants) if room.participants else 0,
            "created_at": room.created_at.isoformat(),
            "created_by": room.created_by
        } for room in rooms
    ]


@router.get("/rooms/{room_id}", response_model=dict)
async def get_room(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get room details"""
    room = db.query(CollaborationRoom).filter(
        CollaborationRoom.id == room_id,
        CollaborationRoom.tenant_id == current_user.get("tenant_id", "default")
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return {
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "room_type": room.room_type,
        "max_participants": room.max_participants,
        "is_active": room.is_active,
        "settings": room.settings,
        "participant_count": len(room.participants) if room.participants else 0,
        "created_at": room.created_at.isoformat(),
        "created_by": room.created_by
    }


@router.put("/rooms/{room_id}", response_model=dict)
async def update_room(
    room_id: str,
    room_data: RoomUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update room settings"""
    room = db.query(CollaborationRoom).filter(
        CollaborationRoom.id == room_id,
        CollaborationRoom.tenant_id == current_user.get("tenant_id", "default")
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check if user is room owner or has permissions
    if room.created_by != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this room")

    # Update fields
    for field, value in room_data.dict(exclude_unset=True).items():
        if hasattr(room, field):
            setattr(room, field, value)

    room.updated_at = datetime.utcnow()
    db.commit()

    return {
        "id": room.id,
        "name": room.name,
        "message": "Room updated successfully"
    }


@router.delete("/rooms/{room_id}", response_model=dict)
async def delete_room(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete collaboration room"""
    room = db.query(CollaborationRoom).filter(
        CollaborationRoom.id == room_id,
        CollaborationRoom.tenant_id == current_user.get("tenant_id", "default")
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.created_by != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this room")

    db.delete(room)
    db.commit()

    return {"message": "Room deleted successfully"}


# Participant Management
@router.post("/rooms/{room_id}/join", response_model=dict)
async def join_room(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a collaboration room"""
    room = db.query(CollaborationRoom).filter(
        CollaborationRoom.id == room_id,
        CollaborationRoom.tenant_id == current_user.get("tenant_id", "default")
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not room.is_active:
        raise HTTPException(status_code=400, detail="Room is not active")

    # Check participant limit
    participant_count = db.query(RoomParticipant).filter_by(room_id=room_id).count()
    if participant_count >= room.max_participants:
        raise HTTPException(status_code=400, detail="Room is full")

    # Check if already joined
    existing = db.query(RoomParticipant).filter_by(
        room_id=room_id, user_id=current_user["id"]
    ).first()

    if existing:
        existing.is_online = True
        existing.last_seen = datetime.utcnow()
    else:
        participant = RoomParticipant(
            id=str(uuid.uuid4()),
            room_id=room_id,
            user_id=current_user["id"],
            user_name=current_user.get("name", "Unknown"),
            user_avatar=current_user.get("avatar"),
            is_online=True
        )
        db.add(participant)

    db.commit()

    return {
        "room_id": room_id,
        "user_id": current_user["id"],
        "message": "Successfully joined room"
    }


@router.post("/rooms/{room_id}/leave", response_model=dict)
async def leave_room(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a collaboration room"""
    participant = db.query(RoomParticipant).filter_by(
        room_id=room_id, user_id=current_user["id"]
    ).first()

    if participant:
        participant.is_online = False
        participant.last_seen = datetime.utcnow()
        db.commit()

    return {
        "room_id": room_id,
        "user_id": current_user["id"],
        "message": "Successfully left room"
    }


# Message Management
@router.post("/rooms/{room_id}/messages", response_model=dict)
async def send_message(
    room_id: str,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message to room"""
    # Verify user is participant
    participant = db.query(RoomParticipant).filter_by(
        room_id=room_id, user_id=current_user["id"]
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Not a room participant")

    message = RoomMessage(
        id=str(uuid.uuid4()),
        room_id=room_id,
        user_id=current_user["id"],
        user_name=participant.user_name,
        content=message_data.content,
        message_type=message_data.message_type,
        metadata=message_data.metadata
    )

    db.add(message)
    db.commit()

    return {
        "id": message.id,
        "room_id": room_id,
        "user_id": current_user["id"],
        "content": message.content,
        "timestamp": message.created_at.isoformat(),
        "message": "Message sent successfully"
    }


@router.get("/rooms/{room_id}/messages", response_model=List[dict])
async def get_room_messages(
    room_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get room messages"""
    # Verify user is participant
    participant = db.query(RoomParticipant).filter_by(
        room_id=room_id, user_id=current_user["id"]
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Not a room participant")

    messages = db.query(RoomMessage).filter_by(room_id=room_id).order_by(
        RoomMessage.created_at.desc()
    ).offset(skip).limit(limit).all()

    return [
        {
            "id": msg.id,
            "user_id": msg.user_id,
            "user_name": msg.user_name,
            "content": msg.content,
            "message_type": msg.message_type,
            "metadata": msg.metadata,
            "timestamp": msg.created_at.isoformat()
        } for msg in reversed(messages)
    ]


# Cursor Management
@router.put("/rooms/{room_id}/cursor", response_model=dict)
async def update_cursor(
    room_id: str,
    cursor_data: CursorUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user cursor position"""
    # Verify user is participant
    participant = db.query(RoomParticipant).filter_by(
        room_id=room_id, user_id=current_user["id"]
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Not a room participant")

    cursor = db.query(UserCursor).filter_by(
        room_id=room_id,
        user_id=current_user["id"],
        document_id=cursor_data.document_id
    ).first()

    if cursor:
        # Update existing cursor
        cursor.position_x = cursor_data.position_x or 0
        cursor.position_y = cursor_data.position_y or 0
        cursor.selection_start = cursor_data.selection_start
        cursor.selection_end = cursor_data.selection_end
        cursor.color = cursor_data.color or "#007bff"
        cursor.last_updated = datetime.utcnow()
    else:
        # Create new cursor
        cursor = UserCursor(
            id=str(uuid.uuid4()),
            room_id=room_id,
            user_id=current_user["id"],
            user_name=participant.user_name,
            document_id=cursor_data.document_id,
            position_x=cursor_data.position_x or 0,
            position_y=cursor_data.position_y or 0,
            selection_start=cursor_data.selection_start,
            selection_end=cursor_data.selection_end,
            color=cursor_data.color or "#007bff"
        )
        db.add(cursor)

    db.commit()

    return {
        "room_id": room_id,
        "user_id": current_user["id"],
        "document_id": cursor_data.document_id,
        "message": "Cursor updated successfully"
    }


@router.get("/rooms/{room_id}/cursors", response_model=List[dict])
async def get_room_cursors(
    room_id: str,
    document_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active cursors in room"""
    # Verify user is participant
    participant = db.query(RoomParticipant).filter_by(
        room_id=room_id, user_id=current_user["id"]
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Not a room participant")

    query = db.query(UserCursor).filter_by(room_id=room_id)
    if document_id:
        query = query.filter_by(document_id=document_id)

    cursors = query.all()

    return [
        {
            "user_id": cursor.user_id,
            "user_name": cursor.user_name,
            "document_id": cursor.document_id,
            "position_x": cursor.position_x,
            "position_y": cursor.position_y,
            "selection_start": cursor.selection_start,
            "selection_end": cursor.selection_end,
            "color": cursor.color,
            "last_updated": cursor.last_updated.isoformat()
        } for cursor in cursors
    ]


# Room Statistics
@router.get("/rooms/{room_id}/stats", response_model=dict)
async def get_room_stats(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get room statistics"""
    room = db.query(CollaborationRoom).filter(
        CollaborationRoom.id == room_id,
        CollaborationRoom.tenant_id == current_user.get("tenant_id", "default")
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Get statistics
    total_participants = db.query(RoomParticipant).filter_by(room_id=room_id).count()
    active_participants = db.query(RoomParticipant).filter_by(
        room_id=room_id, is_online=True
    ).count()
    total_messages = db.query(RoomMessage).filter_by(room_id=room_id).count()
    active_cursors = db.query(UserCursor).filter_by(room_id=room_id).count()

    return {
        "room_id": room_id,
        "total_participants": total_participants,
        "active_participants": active_participants,
        "total_messages": total_messages,
        "active_cursors": active_cursors,
        "room_age_hours": (datetime.utcnow() - room.created_at).total_seconds() / 3600
    }