"""
Audit Logging System for Proyecto Semilla
Comprehensive audit trail with compliance and traceability
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid

from pydantic import BaseModel


class AuditEventType(Enum):
    """Types of audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"
    SYSTEM_EVENT = "system_event"
    USER_ACTIVITY = "user_activity"


class AuditEventSeverity(Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_type: AuditEventType
    severity: AuditEventSeverity = AuditEventSeverity.MEDIUM
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    status: str = "success"
    description: Optional[str] = None
    event_metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create from dictionary"""
        # Convert string enums back to enum objects
        if 'event_type' in data:
            data['event_type'] = AuditEventType(data['event_type'])
        if 'severity' in data:
            data['severity'] = AuditEventSeverity(data['severity'])
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])

        return cls(**data)


@dataclass
class AuditLogEntry:
    """Database audit log entry"""
    id: str
    event_id: str
    event_type: str
    severity: str
    timestamp: datetime
    user_id: Optional[str]
    tenant_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    status: str
    description: Optional[str]
    event_metadata: Dict[str, Any]
    tags: List[str]
    hash: str  # For integrity verification


class AuditLogger:
    """
    Enterprise audit logging system
    """

    def __init__(self, storage_backend: str = "database", retention_days: int = 365):
        self.storage_backend = storage_backend
        self.retention_days = retention_days
        self.queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        self.worker_task: Optional[asyncio.Task] = None

        # Initialize storage
        self._init_storage()

    def _init_storage(self):
        """Initialize storage backend"""
        if self.storage_backend == "database":
            # Database storage will be handled by SQLAlchemy
            pass
        elif self.storage_backend == "file":
            # File-based storage
            import os
            os.makedirs("audit_logs", exist_ok=True)
        elif self.storage_backend == "redis":
            # Redis storage for high-performance scenarios
            pass

    async def start(self):
        """Start the audit logger"""
        if self.is_running:
            return

        self.is_running = True
        self.worker_task = asyncio.create_task(self._process_queue())

    async def stop(self):
        """Stop the audit logger"""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

    async def log_event(self, event: AuditEvent):
        """Log an audit event"""
        await self.queue.put(event)

    async def log_authentication(self, user_id: str, tenant_id: str,
                               ip_address: str, user_agent: str,
                               success: bool, metadata: Optional[Dict] = None):
        """Log authentication event"""
        event = AuditEvent(
            event_type=AuditEventType.AUTHENTICATION,
            severity=AuditEventSeverity.HIGH if not success else AuditEventSeverity.MEDIUM,
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action="login",
            status="success" if success else "failure",
            description=f"User authentication {'successful' if success else 'failed'}",
            event_metadata=metadata or {},
            tags=["authentication", "security"]
        )
        await self.log_event(event)

    async def log_authorization(self, user_id: str, tenant_id: str,
                              resource: str, action: str, allowed: bool,
                              metadata: Optional[Dict] = None):
        """Log authorization event"""
        event = AuditEvent(
            event_type=AuditEventType.AUTHORIZATION,
            severity=AuditEventSeverity.HIGH if not allowed else AuditEventSeverity.LOW,
            user_id=user_id,
            tenant_id=tenant_id,
            resource=resource,
            action=action,
            status="allowed" if allowed else "denied",
            description=f"Access {'granted' if allowed else 'denied'} to {resource}",
            event_metadata=metadata or {},
            tags=["authorization", "access_control"]
        )
        await self.log_event(event)

    async def log_data_access(self, user_id: str, tenant_id: str,
                            resource: str, action: str, record_count: int = 1,
                            metadata: Optional[Dict] = None):
        """Log data access event"""
        event = AuditEvent(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditEventSeverity.MEDIUM,
            user_id=user_id,
            tenant_id=tenant_id,
            resource=resource,
            action=action,
            description=f"Data access: {record_count} records",
            event_metadata={"record_count": record_count, **(metadata or {})},
            tags=["data_access", "privacy"]
        )
        await self.log_event(event)

    async def log_data_modification(self, user_id: str, tenant_id: str,
                                  resource: str, action: str, record_id: str,
                                  changes: Dict[str, Any], metadata: Optional[Dict] = None):
        """Log data modification event"""
        event = AuditEvent(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditEventSeverity.HIGH,
            user_id=user_id,
            tenant_id=tenant_id,
            resource=resource,
            action=action,
            description=f"Data modified: {resource} ({record_id})",
            event_metadata={
                "record_id": record_id,
                "changes": changes,
                **(metadata or {})
            },
            tags=["data_modification", "change_tracking"]
        )
        await self.log_event(event)

    async def log_security_event(self, event_type: str, severity: AuditEventSeverity,
                               description: str, ip_address: Optional[str] = None,
                               metadata: Optional[Dict] = None):
        """Log security-related event"""
        event = AuditEvent(
            event_type=AuditEventType.SECURITY_EVENT,
            severity=severity,
            ip_address=ip_address,
            description=description,
            event_metadata=metadata or {},
            tags=["security", event_type]
        )
        await self.log_event(event)

    async def log_system_event(self, event_type: str, description: str,
                             severity: AuditEventSeverity = AuditEventSeverity.LOW,
                             metadata: Optional[Dict] = None):
        """Log system-related event"""
        event = AuditEvent(
            event_type=AuditEventType.SYSTEM_EVENT,
            severity=severity,
            description=description,
            event_metadata=metadata or {},
            tags=["system", event_type]
        )
        await self.log_event(event)

    async def _process_queue(self):
        """Process audit events from queue"""
        while self.is_running:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self.queue.get(), timeout=1.0)

                # Process the event
                await self._persist_event(event)

                # Mark task as done
                self.queue.task_done()

            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                print(f"Audit logging error: {e}")
                # Continue processing other events

    async def _persist_event(self, event: AuditEvent):
        """Persist audit event to storage"""
        if self.storage_backend == "database":
            await self._persist_to_database(event)
        elif self.storage_backend == "file":
            await self._persist_to_file(event)
        elif self.storage_backend == "redis":
            await self._persist_to_redis(event)

    async def _persist_to_database(self, event: AuditEvent):
        """Persist event to database"""
        try:
            from app.core.database import get_db
            from sqlalchemy import text

            # Create hash for integrity
            event_data = event.to_json()
            event_hash = hashlib.sha256(event_data.encode()).hexdigest()

            async for db in get_db():
                await db.execute(
                    text("""
                        INSERT INTO audit_logs (
                            id, event_id, event_type, severity, timestamp,
                            user_id, tenant_id, session_id, ip_address, user_agent,
                            resource, action, status, description, metadata, tags, hash
                        ) VALUES (
                            :id, :event_id, :event_type, :severity, :timestamp,
                            :user_id, :tenant_id, :session_id, :ip_address, :user_agent,
                            :resource, :action, :status, :description, :metadata, :tags, :hash
                        )
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "event_id": event.id,
                        "event_type": event.event_type.value,
                        "severity": event.severity.value,
                        "timestamp": event.timestamp,
                        "user_id": event.user_id,
                        "tenant_id": event.tenant_id,
                        "session_id": event.session_id,
                        "ip_address": event.ip_address,
                        "user_agent": event.user_agent,
                        "resource": event.resource,
                        "action": event.action,
                        "status": event.status,
                        "description": event.description,
                        "event_metadata": json.dumps(event.event_metadata),
                        "tags": json.dumps(event.tags),
                        "hash": event_hash
                    }
                )
                await db.commit()
                break

        except Exception as e:
            print(f"Database audit logging error: {e}")

    async def _persist_to_file(self, event: AuditEvent):
        """Persist event to file"""
        try:
            import os
            from pathlib import Path

            # Create log directory
            log_dir = Path("audit_logs")
            log_dir.mkdir(exist_ok=True)

            # Create log file for current date
            date_str = event.timestamp.strftime("%Y-%m-%d")
            log_file = log_dir / f"audit_{date_str}.log"

            # Append event to file
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(event.to_json() + '\n')

        except Exception as e:
            print(f"File audit logging error: {e}")

    async def _persist_to_redis(self, event: AuditEvent):
        """Persist event to Redis"""
        try:
            # Redis implementation would go here
            # For now, just print
            print(f"Redis audit log: {event.to_json()}")
        except Exception as e:
            print(f"Redis audit logging error: {e}")

    async def query_events(self, filters: Dict[str, Any],
                          limit: int = 100, offset: int = 0) -> List[AuditEvent]:
        """Query audit events with filters"""
        try:
            from app.core.database import get_db
            from sqlalchemy import text

            # Build query
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []

            if 'event_type' in filters:
                query += f" AND event_type = ${len(params) + 1}"
                params.append(filters['event_type'])

            if 'user_id' in filters:
                query += f" AND user_id = ${len(params) + 1}"
                params.append(filters['user_id'])

            if 'tenant_id' in filters:
                query += f" AND tenant_id = ${len(params) + 1}"
                params.append(filters['tenant_id'])

            if 'start_date' in filters:
                query += f" AND timestamp >= ${len(params) + 1}"
                params.append(filters['start_date'])

            if 'end_date' in filters:
                query += f" AND timestamp <= ${len(params) + 1}"
                params.append(filters['end_date'])

            query += f" ORDER BY timestamp DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
            params.extend([limit, offset])

            events = []
            async for db in get_db():
                result = await db.execute(text(query), params)
                rows = result.fetchall()

                for row in rows:
                    event_data = {
                        'id': row[1],  # event_id
                        'event_type': row[2],
                        'severity': row[3],
                        'timestamp': row[4],
                        'user_id': row[5],
                        'tenant_id': row[6],
                        'session_id': row[7],
                        'ip_address': row[8],
                        'user_agent': row[9],
                        'resource': row[10],
                        'action': row[11],
                        'status': row[12],
                        'description': row[13],
                        'event_metadata': json.loads(row[14]) if row[14] else {},
                        'tags': row[15] if row[15] else []
                    }
                    events.append(AuditEvent.from_dict(event_data))
                break

            return events

        except Exception as e:
            print(f"Audit query error: {e}")
            return []

    async def get_event_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get audit event statistics"""
        try:
            from app.core.database import get_db
            from sqlalchemy import text

            start_date = datetime.utcnow() - timedelta(days=days)

            async for db in get_db():
                # Total events
                total_result = await db.execute(
                    text("SELECT COUNT(*) FROM audit_logs WHERE timestamp >= $1"),
                    [start_date]
                )
                total_events = total_result.fetchone()[0]

                # Events by type
                type_result = await db.execute(
                    text("""
                        SELECT event_type, COUNT(*) as count
                        FROM audit_logs
                        WHERE timestamp >= $1
                        GROUP BY event_type
                        ORDER BY count DESC
                    """),
                    [start_date]
                )
                events_by_type = {row[0]: row[1] for row in type_result.fetchall()}

                # Events by severity
                severity_result = await db.execute(
                    text("""
                        SELECT severity, COUNT(*) as count
                        FROM audit_logs
                        WHERE timestamp >= $1
                        GROUP BY severity
                        ORDER BY count DESC
                    """),
                    [start_date]
                )
                events_by_severity = {row[0]: row[1] for row in severity_result.fetchall()}

                # Failed events
                failed_result = await db.execute(
                    text("""
                        SELECT COUNT(*) FROM audit_logs
                        WHERE timestamp >= $1 AND status != 'success'
                    """),
                    [start_date]
                )
                failed_events = failed_result.fetchone()[0]

                return {
                    'total_events': total_events,
                    'events_by_type': events_by_type,
                    'events_by_severity': events_by_severity,
                    'failed_events': failed_events,
                    'success_rate': ((total_events - failed_events) / total_events * 100) if total_events > 0 else 100,
                    'period_days': days
                }

        except Exception as e:
            print(f"Audit statistics error: {e}")
            return {
                'total_events': 0,
                'events_by_type': {},
                'events_by_severity': {},
                'failed_events': 0,
                'success_rate': 100,
                'period_days': days,
                'error': str(e)
            }

    async def cleanup_old_events(self):
        """Clean up old audit events based on retention policy"""
        try:
            from app.core.database import get_db
            from sqlalchemy import text

            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)

            async for db in get_db():
                result = await db.execute(
                    text("DELETE FROM audit_logs WHERE timestamp < $1"),
                    [cutoff_date]
                )
                deleted_count = result.rowcount
                await db.commit()

                await self.log_system_event(
                    "cleanup",
                    f"Cleaned up {deleted_count} old audit events",
                    AuditEventSeverity.LOW,
                    {"deleted_count": deleted_count, "retention_days": self.retention_days}
                )
                break

        except Exception as e:
            print(f"Audit cleanup error: {e}")

    async def verify_integrity(self, event_id: str) -> bool:
        """Verify integrity of audit event"""
        try:
            from app.core.database import get_db
            from sqlalchemy import text

            async for db in get_db():
                result = await db.execute(
                    text("SELECT * FROM audit_logs WHERE event_id = $1"),
                    [event_id]
                )
                row = result.fetchone()

                if not row:
                    return False

                # Recreate event data for hash verification
                event_data = {
                    'id': row[1],
                    'event_type': row[2],
                    'severity': row[3],
                    'timestamp': row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4]),
                    'user_id': row[5],
                    'tenant_id': row[6],
                    'session_id': row[7],
                    'ip_address': row[8],
                    'user_agent': row[9],
                    'resource': row[10],
                    'action': row[11],
                    'status': row[12],
                    'description': row[13],
                    'event_metadata': json.loads(row[14]) if row[14] else {},
                    'tags': row[15] if row[15] else []
                }

                # Calculate hash
                event_json = json.dumps(event_data, sort_keys=True, default=str)
                calculated_hash = hashlib.sha256(event_json.encode()).hexdigest()

                # Compare with stored hash
                stored_hash = row[16]
                return calculated_hash == stored_hash

        except Exception as e:
            print(f"Audit integrity verification error: {e}")
            return False


# Global audit logger instance
audit_logger = AuditLogger()


# FastAPI integration
async def log_request_middleware(request, call_next):
    """Middleware to log API requests"""
    import time

    start_time = time.time()

    # Get request information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    path = request.url.path
    method = request.method

    # Get user information from request state (set by auth middleware)
    user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    try:
        # Process request
        response = await call_next(request)
        duration = time.time() - start_time

        # Log successful request
        await audit_logger.log_event(AuditEvent(
            event_type=AuditEventType.USER_ACTIVITY,
            severity=AuditEventSeverity.LOW,
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=client_ip,
            user_agent=user_agent,
            resource=path,
            action=method,
            status="success",
            description=f"API request completed in {duration:.2f}s",
            event_metadata={"duration": duration, "status_code": response.status_code},
            tags=["api", "request"]
        ))

        return response

    except Exception as e:
        duration = time.time() - start_time

        # Log failed request
        await audit_logger.log_event(AuditEvent(
            event_type=AuditEventType.SECURITY_EVENT,
            severity=AuditEventSeverity.MEDIUM,
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=client_ip,
            user_agent=user_agent,
            resource=path,
            action=method,
            status="error",
            description=f"API request failed: {str(e)}",
            event_metadata={"duration": duration, "error": str(e)},
            tags=["api", "error", "security"]
        ))

        raise


# Utility functions
async def audit_user_action(user_id: str, tenant_id: str, action: str,
                          resource: str, metadata: Optional[Dict] = None):
    """Convenience function to audit user actions"""
    await audit_logger.log_event(AuditEvent(
        event_type=AuditEventType.USER_ACTIVITY,
        severity=AuditEventSeverity.LOW,
        user_id=user_id,
        tenant_id=tenant_id,
        resource=resource,
        action=action,
        event_metadata=metadata or {},
        tags=["user_action"]
    ))


async def audit_security_incident(description: str, severity: AuditEventSeverity,
                                ip_address: Optional[str] = None,
                                metadata: Optional[Dict] = None):
    """Convenience function to audit security incidents"""
    await audit_logger.log_security_event(
        "incident",
        severity,
        description,
        ip_address,
        metadata
    )


# Compliance helpers
async def generate_compliance_report(compliance_standard: str,
                                   days: int = 90) -> Dict[str, Any]:
    """Generate compliance report for specified standard"""
    # This would implement specific compliance checks
    # For now, return basic structure

    stats = await audit_logger.get_event_statistics(days)

    return {
        'standard': compliance_standard,
        'period_days': days,
        'audit_coverage': stats,
        'compliance_status': 'review_required',
        'recommendations': [
            'Implement automated compliance checks',
            'Regular audit reviews',
            'Staff training on compliance requirements'
        ]
    }


# Startup and shutdown handlers
async def init_audit_logging():
    """Initialize audit logging on startup"""
    await audit_logger.start()

    # Log system startup
    await audit_logger.log_system_event(
        "startup",
        "Audit logging system initialized",
        AuditEventSeverity.LOW,
        {"version": "1.0.0"}
    )


async def shutdown_audit_logging():
    """Shutdown audit logging on shutdown"""
    # Log system shutdown
    await audit_logger.log_system_event(
        "shutdown",
        "Audit logging system shutting down",
        AuditEventSeverity.LOW
    )

    await audit_logger.stop()