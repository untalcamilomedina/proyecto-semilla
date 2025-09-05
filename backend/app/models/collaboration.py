"""
Collaboration Models for Proyecto Semilla
Real-time collaboration features and session management
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CollaborationRoom(Base):
    """Collaboration room for real-time sessions"""
    __tablename__ = "collaboration_rooms"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tenant_id = Column(String(36), nullable=False, index=True)
    created_by = Column(String(36), nullable=False)
    max_participants = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    room_type = Column(String(50), default="general")  # general, document, code, design
    settings = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    participants = relationship("RoomParticipant", back_populates="room", cascade="all, delete-orphan")
    messages = relationship("RoomMessage", back_populates="room", cascade="all, delete-orphan")
    cursors = relationship("UserCursor", back_populates="room", cascade="all, delete-orphan")


class RoomParticipant(Base):
    """Room participant with presence information"""
    __tablename__ = "room_participants"

    id = Column(String(36), primary_key=True, index=True)
    room_id = Column(String(36), ForeignKey("collaboration_rooms.id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    user_name = Column(String(255), nullable=False)
    user_avatar = Column(String(500))
    role = Column(String(50), default="participant")  # owner, moderator, participant
    is_online = Column(Boolean, default=True)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    room = relationship("CollaborationRoom", back_populates="participants")


class RoomMessage(Base):
    """Real-time messages in collaboration rooms"""
    __tablename__ = "room_messages"

    id = Column(String(36), primary_key=True, index=True)
    room_id = Column(String(36), ForeignKey("collaboration_rooms.id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    user_name = Column(String(255), nullable=False)
    message_type = Column(String(50), default="text")  # text, system, file, code
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    room = relationship("CollaborationRoom", back_populates="messages")


class UserCursor(Base):
    """Real-time cursor positions for collaborative editing"""
    __tablename__ = "user_cursors"

    id = Column(String(36), primary_key=True, index=True)
    room_id = Column(String(36), ForeignKey("collaboration_rooms.id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    user_name = Column(String(255), nullable=False)
    document_id = Column(String(36), nullable=False)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    selection_start = Column(Integer, nullable=True)
    selection_end = Column(Integer, nullable=True)
    color = Column(String(7), default="#007bff")  # Hex color

    # Timestamps
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    room = relationship("CollaborationRoom", back_populates="cursors")


class ConflictResolution(Base):
    """Conflict resolution for collaborative editing"""
    __tablename__ = "conflict_resolutions"

    id = Column(String(36), primary_key=True, index=True)
    room_id = Column(String(36), ForeignKey("collaboration_rooms.id"), nullable=False)
    document_id = Column(String(36), nullable=False)
    conflict_type = Column(String(50), nullable=False)  # text, structural, semantic
    original_content = Column(Text, nullable=False)
    conflicting_changes = Column(JSON, nullable=False)
    resolved_content = Column(Text)
    resolved_by = Column(String(36))
    resolution_method = Column(String(50))  # auto, manual, merge

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))


class CollaborativeSession(Base):
    """Active collaborative editing sessions"""
    __tablename__ = "collaborative_sessions"

    id = Column(String(36), primary_key=True, index=True)
    room_id = Column(String(36), ForeignKey("collaboration_rooms.id"), nullable=False)
    document_id = Column(String(36), nullable=False)
    document_type = Column(String(50), nullable=False)  # code, document, design
    session_data = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    participant_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    room = relationship("CollaborationRoom")