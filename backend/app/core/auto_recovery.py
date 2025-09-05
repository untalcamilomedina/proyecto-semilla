"""
Auto-Recovery System for Proyecto Semilla
Intelligent service recovery and self-healing capabilities
"""

from typing import Dict, List, Callable, Any, Optional
import asyncio
import time
import logging
from enum import Enum
from dataclasses import dataclass
from app.core.circuit_breaker import get_circuit_breaker


class RecoveryStrategy(Enum):
    """Recovery strategies available"""
    RESTART = "restart"
    FAILOVER = "failover"
    SCALE_UP = "scale_up"
    CIRCUIT_BREAK = "circuit_break"
    CUSTOM = "custom"


@dataclass
class RecoveryAction:
    """Recovery action configuration"""
    strategy: RecoveryStrategy
    priority: int
    max_attempts: int = 3
    cooldown_seconds: int = 60
    custom_handler: Optional[Callable] = None
    enabled: bool = True


@dataclass
class RecoveryAttempt:
    """Recovery attempt record"""
    service_name: str
    strategy: RecoveryStrategy
    attempt_number: int
    timestamp: float
    success: bool
    error_message: Optional[str] = None


class AutoRecoveryEngine:
    """
    Intelligent auto-recovery system for system resilience
    """

    def __init__(self):
        self.recovery_actions: Dict[str, List[RecoveryAction]] = {}
        self.failure_history: Dict[str, List[float]] = {}
        self.recovery_history: List[RecoveryAttempt] = []
        self.max_history_size = 1000
        self.logger = logging.getLogger(__name__)

        # Recovery attempt tracking
        self.active_recoveries: Dict[str, RecoveryAttempt] = {}

    def register_recovery_action(self, service_name: str, action: RecoveryAction):
        """Register recovery action for a service"""
        if service_name not in self.recovery_actions:
            self.recovery_actions[service_name] = []

        self.recovery_actions[service_name].append(action)
        self.recovery_actions[service_name].sort(key=lambda x: x.priority)

        self.logger.info(f"Registered recovery action {action.strategy.value} for service {service_name}")

    def unregister_recovery_action(self, service_name: str, strategy: RecoveryStrategy):
        """Unregister recovery action for a service"""
        if service_name in self.recovery_actions:
            self.recovery_actions[service_name] = [
                action for action in self.recovery_actions[service_name]
                if action.strategy != strategy
            ]

    async def handle_service_failure(self, service_name: str, error: Exception):
        """Handle service failure with auto-recovery"""
        self.logger.error(f"Service {service_name} failed: {error}")

        # Record failure
        if service_name not in self.failure_history:
            self.failure_history[service_name] = []
        self.failure_history[service_name].append(time.time())

        # Clean old failures (keep last 24 hours)
        cutoff_time = time.time() - 86400
        self.failure_history[service_name] = [
            t for t in self.failure_history[service_name] if t > cutoff_time
        ]

        # Check if we're already trying to recover this service
        if service_name in self.active_recoveries:
            self.logger.warning(f"Recovery already in progress for {service_name}")
            return

        # Execute recovery actions
        if service_name in self.recovery_actions:
            await self._execute_recovery_actions(service_name)
        else:
            self.logger.warning(f"No recovery actions registered for {service_name}")

    async def _execute_recovery_actions(self, service_name: str):
        """Execute recovery actions in priority order"""
        actions = self.recovery_actions[service_name]

        for action in actions:
            if not action.enabled:
                continue

            attempt = RecoveryAttempt(
                service_name=service_name,
                strategy=action.strategy,
                attempt_number=self._get_attempt_count(service_name, action.strategy) + 1,
                timestamp=time.time(),
                success=False
            )

            self.active_recoveries[service_name] = attempt

            try:
                success = await self._execute_single_action(service_name, action)
                attempt.success = success

                if success:
                    self.logger.info(f"Recovery action {action.strategy.value} succeeded for {service_name}")
                    break
                else:
                    attempt.error_message = "Recovery action failed"
                    self.logger.warning(f"Recovery action {action.strategy.value} failed for {service_name}")

            except Exception as e:
                attempt.error_message = str(e)
                self.logger.error(f"Recovery action {action.strategy.value} error for {service_name}: {e}")

            finally:
                # Record attempt
                self.recovery_history.append(attempt)
                if len(self.recovery_history) > self.max_history_size:
                    self.recovery_history.pop(0)

                # Clean up active recovery
                if service_name in self.active_recoveries:
                    del self.active_recoveries[service_name]

    async def _execute_single_action(self, service_name: str, action: RecoveryAction) -> bool:
        """Execute single recovery action"""
        if action.strategy == RecoveryStrategy.RESTART:
            return await self._restart_service(service_name)
        elif action.strategy == RecoveryStrategy.FAILOVER:
            return await self._failover_service(service_name)
        elif action.strategy == RecoveryStrategy.SCALE_UP:
            return await self._scale_up_service(service_name)
        elif action.strategy == RecoveryStrategy.CIRCUIT_BREAK:
            return await self._activate_circuit_breaker(service_name)
        elif action.strategy == RecoveryStrategy.CUSTOM and action.custom_handler:
            return await action.custom_handler(service_name)
        else:
            self.logger.error(f"Unknown recovery strategy: {action.strategy}")
            return False

    async def _restart_service(self, service_name: str) -> bool:
        """Restart a service"""
        try:
            self.logger.info(f"Attempting to restart service: {service_name}")

            if service_name == "database":
                success = await self._restart_database_pool()
            elif service_name == "cache":
                success = await self._restart_cache_connection()
            elif service_name == "external_api":
                success = await self._reset_api_client()
            elif service_name == "background_worker":
                success = await self._restart_worker_processes()
            else:
                # Generic restart attempt
                success = await self._generic_service_restart(service_name)

            if success:
                self.logger.info(f"Successfully restarted service: {service_name}")
            else:
                self.logger.warning(f"Failed to restart service: {service_name}")

            return success

        except Exception as e:
            self.logger.error(f"Error restarting {service_name}: {e}")
            return False

    async def _failover_service(self, service_name: str) -> bool:
        """Failover to backup service"""
        try:
            self.logger.info(f"Attempting failover for service: {service_name}")

            if service_name == "database":
                success = await self._switch_to_backup_database()
            elif service_name == "cache":
                success = await self._switch_to_backup_cache()
            elif service_name == "external_api":
                success = await self._switch_to_backup_api()
            else:
                success = False

            if success:
                self.logger.info(f"Successfully failed over service: {service_name}")
            else:
                self.logger.warning(f"Failed to failover service: {service_name}")

            return success

        except Exception as e:
            self.logger.error(f"Error failing over {service_name}: {e}")
            return False

    async def _scale_up_service(self, service_name: str) -> bool:
        """Scale up service resources"""
        try:
            self.logger.info(f"Attempting to scale up service: {service_name}")

            # Implementation would depend on deployment (Docker, Kubernetes, etc.)
            # For now, this is a placeholder
            self.logger.info(f"Scale up not implemented for {service_name}")
            return False

        except Exception as e:
            self.logger.error(f"Error scaling up {service_name}: {e}")
            return False

    async def _activate_circuit_breaker(self, service_name: str) -> bool:
        """Activate circuit breaker for service"""
        try:
            circuit_breaker = get_circuit_breaker(service_name)
            if circuit_breaker:
                circuit_breaker.force_open()
                self.logger.info(f"Activated circuit breaker for {service_name}")
                return True
            else:
                self.logger.warning(f"No circuit breaker found for {service_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error activating circuit breaker for {service_name}: {e}")
            return False

    # Service-specific recovery implementations
    async def _restart_database_pool(self) -> bool:
        """Restart database connection pool"""
        try:
            from app.core.database import engine
            # Close existing connections
            await engine.dispose()
            # New connections will be created on next use
            return True
        except Exception as e:
            self.logger.error(f"Error restarting database pool: {e}")
            return False

    async def _restart_cache_connection(self) -> bool:
        """Restart cache connection"""
        try:
            # Implementation depends on cache system (Redis, etc.)
            self.logger.info("Cache restart not implemented")
            return False
        except Exception as e:
            self.logger.error(f"Error restarting cache: {e}")
            return False

    async def _reset_api_client(self) -> bool:
        """Reset external API client"""
        try:
            # Reset connection pools, clear caches, etc.
            self.logger.info("API client reset not implemented")
            return False
        except Exception as e:
            self.logger.error(f"Error resetting API client: {e}")
            return False

    async def _restart_worker_processes(self) -> bool:
        """Restart background worker processes"""
        try:
            # Implementation depends on worker system
            self.logger.info("Worker restart not implemented")
            return False
        except Exception as e:
            self.logger.error(f"Error restarting workers: {e}")
            return False

    async def _generic_service_restart(self, service_name: str) -> bool:
        """Generic service restart"""
        try:
            # Placeholder for generic restart logic
            self.logger.info(f"Generic restart attempted for {service_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error in generic restart for {service_name}: {e}")
            return False

    async def _switch_to_backup_database(self) -> bool:
        """Switch to backup database"""
        try:
            # Implementation for database failover
            self.logger.info("Database failover not implemented")
            return False
        except Exception as e:
            self.logger.error(f"Error switching database: {e}")
            return False

    async def _switch_to_backup_cache(self) -> bool:
        """Switch to backup cache"""
        try:
            # Implementation for cache failover
            self.logger.info("Cache failover not implemented")
            return False
        except Exception as e:
            self.logger.error(f"Error switching cache: {e}")
            return False

    async def _switch_to_backup_api(self) -> bool:
        """Switch to backup API"""
        try:
            # Implementation for API failover
            self.logger.info("API failover not implemented")
            return False
        except Exception as e:
            self.logger.error(f"Error switching API: {e}")
            return False

    def _get_attempt_count(self, service_name: str, strategy: RecoveryStrategy) -> int:
        """Get number of previous attempts for this service and strategy"""
        return len([
            attempt for attempt in self.recovery_history
            if attempt.service_name == service_name and attempt.strategy == strategy
        ])

    def get_recovery_status(self, service_name: str) -> Dict[str, Any]:
        """Get recovery status for a service"""
        recent_failures = len(self.failure_history.get(service_name, []))
        last_failure = max(self.failure_history.get(service_name, [0]))

        return {
            "service_name": service_name,
            "recent_failures": recent_failures,
            "last_failure": last_failure,
            "time_since_last_failure": time.time() - last_failure if last_failure > 0 else None,
            "available_actions": [
                action.strategy.value for action in self.recovery_actions.get(service_name, [])
            ],
            "active_recovery": service_name in self.active_recoveries,
            "recovery_attempt": self.active_recoveries.get(service_name).__dict__ if service_name in self.active_recoveries else None
        }

    def get_recovery_history(self, service_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recovery history"""
        history = self.recovery_history
        if service_name:
            history = [attempt for attempt in history if attempt.service_name == service_name]

        return [
            {
                "service_name": attempt.service_name,
                "strategy": attempt.strategy.value,
                "attempt_number": attempt.attempt_number,
                "timestamp": attempt.timestamp,
                "success": attempt.success,
                "error_message": attempt.error_message
            }
            for attempt in history[-limit:]
        ]

    def get_service_health_summary(self) -> Dict[str, Any]:
        """Get overall service health summary"""
        services = set(self.recovery_actions.keys())
        failing_services = []

        for service in services:
            recent_failures = len(self.failure_history.get(service, []))
            if recent_failures > 0:
                last_failure = max(self.failure_history[service])
                if time.time() - last_failure < 3600:  # Last hour
                    failing_services.append(service)

        return {
            "total_services": len(services),
            "failing_services": len(failing_services),
            "healthy_services": len(services) - len(failing_services),
            "failing_service_names": failing_services,
            "overall_health": "healthy" if len(failing_services) == 0 else "degraded"
        }


# Global recovery engine instance
recovery_engine = AutoRecoveryEngine()


def get_recovery_engine() -> AutoRecoveryEngine:
    """Dependency injection for recovery engine"""
    return recovery_engine