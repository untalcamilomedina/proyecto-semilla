"""
Real-time Collaboration System for Proyecto Semilla
WebSocket-based collaboration with rooms, presence, and cursors
"""

import json
import asyncio
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.models.collaboration import (
    CollaborationRoom, RoomParticipant, RoomMessage,
    UserCursor, CollaborativeSession
)
from app.websocket.redis_client import RedisClient


logger = logging.getLogger(__name__)


class CollaborationManager:
    """Manages real-time collaboration features"""

    def __init__(self):
        self.redis = RedisClient()
        self.active_rooms: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}
        self.room_participants: Dict[str, Set[str]] = {}

    async def connect_to_room(self, websocket: WebSocket, room_id: str, user_id: str, user_name: str):
        """Connect user to collaboration room"""
        await websocket.accept()

        # Add to active connections
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = set()
        self.active_rooms[room_id].add(websocket)

        if room_id not in self.room_participants:
            self.room_participants[room_id] = set()
        self.room_participants[room_id].add(user_id)

        self.user_connections[user_id] = websocket

        # Update participant status in database
        await self._update_participant_status(room_id, user_id, user_name, online=True)

        # Broadcast user joined
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "user_name": user_name,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Send current room state
        await self._send_room_state(websocket, room_id)

        logger.info(f"User {user_name} joined room {room_id}")

    async def disconnect_from_room(self, room_id: str, user_id: str):
        """Disconnect user from collaboration room"""
        if room_id in self.active_rooms:
            # Remove from active connections
            websockets_to_remove = []
            for ws in self.active_rooms[room_id]:
                # Check if this websocket belongs to the user
                if hasattr(ws, 'user_id') and ws.user_id == user_id:
                    websockets_to_remove.append(ws)

            for ws in websockets_to_remove:
                self.active_rooms[room_id].discard(ws)

            # Clean up empty rooms
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]

        if room_id in self.room_participants:
            self.room_participants[room_id].discard(user_id)
            if not self.room_participants[room_id]:
                del self.room_participants[room_id]

        if user_id in self.user_connections:
            del self.user_connections[user_id]

        # Update participant status in database
        await self._update_participant_status(room_id, user_id, online=False)

        # Broadcast user left
        await self.broadcast_to_room(room_id, {
            "type": "user_left",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        logger.info(f"User {user_id} left room {room_id}")

    async def handle_message(self, room_id: str, user_id: str, message: dict):
        """Handle incoming WebSocket messages"""
        message_type = message.get("type")

        if message_type == "cursor_update":
            await self._handle_cursor_update(room_id, user_id, message)
        elif message_type == "message":
            await self._handle_chat_message(room_id, user_id, message)
        elif message_type == "presence_update":
            await self._handle_presence_update(room_id, user_id, message)
        elif message_type == "selection_change":
            await self._handle_selection_change(room_id, user_id, message)
        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def _handle_cursor_update(self, room_id: str, user_id: str, message: dict):
        """Handle cursor position updates"""
        cursor_data = {
            "user_id": user_id,
            "position_x": message.get("x", 0),
            "position_y": message.get("y", 0),
            "document_id": message.get("document_id", ""),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Update cursor in database
        await self._update_user_cursor(room_id, user_id, cursor_data)

        # Broadcast cursor update to room
        await self.broadcast_to_room(room_id, {
            "type": "cursor_update",
            **cursor_data
        })

    async def _handle_chat_message(self, room_id: str, user_id: str, message: dict):
        """Handle chat messages"""
        db = next(get_db())
        try:
            # Get user name
            participant = db.query(RoomParticipant).filter_by(
                room_id=room_id, user_id=user_id
            ).first()

            if participant:
                # Save message to database
                chat_message = RoomMessage(
                    id=str(uuid.uuid4()),
                    room_id=room_id,
                    user_id=user_id,
                    user_name=participant.user_name,
                    content=message.get("content", ""),
                    message_type="text"
                )
                db.add(chat_message)
                db.commit()

                # Broadcast message to room
                await self.broadcast_to_room(room_id, {
                    "type": "message",
                    "id": chat_message.id,
                    "user_id": user_id,
                    "user_name": participant.user_name,
                    "content": message.get("content", ""),
                    "timestamp": chat_message.created_at.isoformat()
                })

        finally:
            db.close()

    async def _handle_presence_update(self, room_id: str, user_id: str, message: dict):
        """Handle presence updates"""
        presence_data = {
            "user_id": user_id,
            "status": message.get("status", "online"),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Update presence in database
        await self._update_participant_status(room_id, user_id, online=(presence_data["status"] == "online"))

        # Broadcast presence update
        await self.broadcast_to_room(room_id, {
            "type": "presence_update",
            **presence_data
        })

    async def _handle_selection_change(self, room_id: str, user_id: str, message: dict):
        """Handle text selection changes"""
        selection_data = {
            "user_id": user_id,
            "document_id": message.get("document_id", ""),
            "start": message.get("start", 0),
            "end": message.get("end", 0),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Update cursor with selection
        await self._update_user_cursor(room_id, user_id, {
            "selection_start": selection_data["start"],
            "selection_end": selection_data["end"],
            "document_id": selection_data["document_id"]
        })

        # Broadcast selection change
        await self.broadcast_to_room(room_id, {
            "type": "selection_change",
            **selection_data
        })

    async def broadcast_to_room(self, room_id: str, message: dict):
        """Broadcast message to all users in room"""
        if room_id not in self.active_rooms:
            return

        disconnected = []
        for websocket in self.active_rooms[room_id]:
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.append(websocket)

        # Remove disconnected websockets
        for ws in disconnected:
            self.active_rooms[room_id].discard(ws)

    async def _send_room_state(self, websocket: WebSocket, room_id: str):
        """Send current room state to new participant"""
        db = next(get_db())
        try:
            # Get active participants
            participants = db.query(RoomParticipant).filter_by(
                room_id=room_id, is_online=True
            ).all()

            # Get recent messages
            messages = db.query(RoomMessage).filter_by(room_id=room_id).order_by(
                RoomMessage.created_at.desc()
            ).limit(50).all()

            # Get active cursors
            cursors = db.query(UserCursor).filter_by(room_id=room_id).all()

            room_state = {
                "type": "room_state",
                "participants": [
                    {
                        "user_id": p.user_id,
                        "user_name": p.user_name,
                        "role": p.role,
                        "joined_at": p.joined_at.isoformat()
                    } for p in participants
                ],
                "recent_messages": [
                    {
                        "id": m.id,
                        "user_id": m.user_id,
                        "user_name": m.user_name,
                        "content": m.content,
                        "timestamp": m.created_at.isoformat()
                    } for m in reversed(messages)
                ],
                "active_cursors": [
                    {
                        "user_id": c.user_id,
                        "user_name": c.user_name,
                        "position_x": c.position_x,
                        "position_y": c.position_y,
                        "document_id": c.document_id,
                        "color": c.color
                    } for c in cursors
                ]
            }

            await websocket.send_json(room_state)

        finally:
            db.close()

    async def _update_participant_status(self, room_id: str, user_id: str, user_name: str = None, online: bool = True):
        """Update participant online status"""
        db = next(get_db())
        try:
            participant = db.query(RoomParticipant).filter_by(
                room_id=room_id, user_id=user_id
            ).first()

            if participant:
                participant.is_online = online
                participant.last_seen = datetime.utcnow()
            elif user_name:
                # Create new participant
                participant = RoomParticipant(
                    id=str(uuid.uuid4()),
                    room_id=room_id,
                    user_id=user_id,
                    user_name=user_name,
                    is_online=online
                )
                db.add(participant)

            db.commit()

        finally:
            db.close()

    async def _update_user_cursor(self, room_id: str, user_id: str, cursor_data: dict):
        """Update user cursor position"""
        db = next(get_db())
        try:
            # Get user name
            participant = db.query(RoomParticipant).filter_by(
                room_id=room_id, user_id=user_id
            ).first()

            if not participant:
                return

            cursor = db.query(UserCursor).filter_by(
                room_id=room_id, user_id=user_id, document_id=cursor_data.get("document_id", "")
            ).first()

            if cursor:
                # Update existing cursor
                for key, value in cursor_data.items():
                    if hasattr(cursor, key):
                        setattr(cursor, key, value)
                cursor.last_updated = datetime.utcnow()
            else:
                # Create new cursor
                cursor = UserCursor(
                    id=str(uuid.uuid4()),
                    room_id=room_id,
                    user_id=user_id,
                    user_name=participant.user_name,
                    document_id=cursor_data.get("document_id", ""),
                    position_x=cursor_data.get("position_x", 0),
                    position_y=cursor_data.get("position_y", 0),
                    selection_start=cursor_data.get("selection_start"),
                    selection_end=cursor_data.get("selection_end"),
                    color=cursor_data.get("color", "#007bff")
                )
                db.add(cursor)

            db.commit()

        finally:
            db.close()


# Global collaboration manager instance
collaboration_manager = CollaborationManager()


async def get_collaboration_manager() -> CollaborationManager:
    """Dependency injection for collaboration manager"""
    return collaboration_manager