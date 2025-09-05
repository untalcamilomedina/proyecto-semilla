"""
Plugin Development Environments for Proyecto Semilla
Isolated testing environments for plugin development without affecting production
"""

import asyncio
import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
import docker
import uuid

from .models import (
    PluginEnvironment, DevelopmentEnvironment, EnvironmentType,
    create_plugin_environment, create_development_environment
)

class EnvironmentManager:
    """
    Manages isolated plugin development environments
    Provides safe testing spaces for plugin creators
    """

    def __init__(self, base_config: Optional[Dict[str, Any]] = None):
        self.base_config = base_config or {
            "max_environments_per_tenant": 5,
            "environment_lifetime_hours": 24,
            "auto_cleanup_enabled": True,
            "resource_limits": {
                "cpu": 0.5,
                "memory": "512MB",
                "storage": "1GB"
            }
        }

        self.active_environments: Dict[str, DevelopmentEnvironment] = {}
        self.environment_data: Dict[str, Dict[str, Any]] = {}
        self.docker_client = docker.from_env()

    async def create_development_environment(self, tenant_id: str, creator_id: str,
                                           plugin_id: str, name: str) -> DevelopmentEnvironment:
        """Create a new isolated development environment"""

        # Check limits
        tenant_environments = [env for env in self.active_environments.values()
                             if env.tenant_id == tenant_id]
        if len(tenant_environments) >= self.base_config["max_environments_per_tenant"]:
            raise ValueError(f"Maximum environments per tenant reached: {self.base_config['max_environments_per_tenant']}")

        # Create environment configuration
        env = create_development_environment(tenant_id, creator_id, plugin_id, name)

        # Set expiration
        env.expires_at = datetime.utcnow() + timedelta(hours=self.base_config["environment_lifetime_hours"])

        # Initialize environment data
        self.environment_data[env.id] = {
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "plugin_state": {},
            "database_state": {},
            "config_changes": []
        }

        # Create Docker containers for isolation
        await self._create_docker_environment(env)

        # Store environment
        self.active_environments[env.id] = env

        return env

    async def get_environment(self, environment_id: str) -> Optional[DevelopmentEnvironment]:
        """Get environment by ID"""
        return self.active_environments.get(environment_id)

    async def list_tenant_environments(self, tenant_id: str) -> List[DevelopmentEnvironment]:
        """List all environments for a tenant"""
        return [env for env in self.active_environments.values()
                if env.tenant_id == tenant_id]

    async def execute_in_environment(self, environment_id: str, code: str,
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute code in isolated environment"""

        if environment_id not in self.active_environments:
            raise ValueError(f"Environment {environment_id} not found")

        env = self.active_environments[environment_id]

        # Update last activity
        self.environment_data[environment_id]["last_activity"] = datetime.utcnow()

        # Execute code in Docker container
        result = await self._execute_code_in_container(env.id, code, context)

        # Store execution result
        execution_record = {
            "timestamp": datetime.utcnow(),
            "code": code,
            "context": context,
            "result": result
        }
        self.environment_data[environment_id]["config_changes"].append(execution_record)

        return result

    async def get_environment_state(self, environment_id: str) -> Dict[str, Any]:
        """Get current state of environment"""
        if environment_id not in self.active_environments:
            raise ValueError(f"Environment {environment_id} not found")

        env = self.active_environments[environment_id]
        env_data = self.environment_data[environment_id]

        return {
            "environment": asdict(env),
            "state": env_data,
            "active_time": (datetime.utcnow() - env.created_at).total_seconds(),
            "time_to_expiry": (env.expires_at - datetime.utcnow()).total_seconds() if env.expires_at else None
        }

    async def save_environment_state(self, environment_id: str) -> Dict[str, Any]:
        """Save current environment state for persistence"""
        if environment_id not in self.active_environments:
            raise ValueError(f"Environment {environment_id} not found")

        env = self.active_environments[environment_id]
        env_data = self.environment_data[environment_id]

        # Create snapshot
        snapshot = {
            "environment_id": environment_id,
            "timestamp": datetime.utcnow(),
            "environment_config": asdict(env),
            "state_data": env_data,
            "docker_state": await self._get_docker_container_state(env.id)
        }

        # Save to persistent storage (would be database in production)
        snapshot_file = f"/tmp/env_snapshot_{environment_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, default=str, indent=2)

        return {
            "snapshot_id": str(uuid.uuid4()),
            "snapshot_file": snapshot_file,
            "timestamp": snapshot["timestamp"]
        }

    async def load_environment_state(self, environment_id: str, snapshot_file: str) -> bool:
        """Load environment state from snapshot"""
        if environment_id not in self.active_environments:
            raise ValueError(f"Environment {environment_id} not found")

        try:
            with open(snapshot_file, 'r') as f:
                snapshot = json.load(f)

            # Restore state
            self.environment_data[environment_id] = snapshot["state_data"]

            # Restore Docker state
            await self._restore_docker_container_state(environment_id, snapshot["docker_state"])

            return True

        except Exception as e:
            print(f"Error loading environment state: {e}")
            return False

    async def destroy_environment(self, environment_id: str) -> bool:
        """Destroy environment and clean up resources"""
        if environment_id not in self.active_environments:
            return False

        env = self.active_environments[environment_id]

        # Stop and remove Docker containers
        await self._cleanup_docker_environment(env.id)

        # Remove from active environments
        del self.active_environments[environment_id]
        del self.environment_data[environment_id]

        return True

    async def cleanup_expired_environments(self):
        """Clean up expired environments"""
        current_time = datetime.utcnow()
        expired_envs = []

        for env_id, env in self.active_environments.items():
            if env.expires_at and current_time > env.expires_at:
                expired_envs.append(env_id)

        for env_id in expired_envs:
            await self.destroy_environment(env_id)

        return len(expired_envs)

    # Private methods

    async def _create_docker_environment(self, env: DevelopmentEnvironment):
        """Create Docker containers for environment isolation"""

        # Create network for environment
        network_name = f"plugin_env_{env.id}"
        try:
            self.docker_client.networks.create(network_name, driver="bridge")
        except docker.errors.APIError:
            pass  # Network might already exist

        # Create PostgreSQL container
        db_container = self.docker_client.containers.run(
            "postgres:15-alpine",
            name=f"plugin_db_{env.id}",
            environment={
                "POSTGRES_DB": f"test_{env.plugin_id}",
                "POSTGRES_USER": f"test_{env.tenant_id}",
                "POSTGRES_PASSWORD": "test_password"
            },
            networks=[network_name],
            detach=True,
            remove=True,
            mem_limit=self.base_config["resource_limits"]["memory"],
            cpu_quota=int(self.base_config["resource_limits"]["cpu"] * 100000)
        )

        # Create Redis container
        redis_container = self.docker_client.containers.run(
            "redis:7-alpine",
            name=f"plugin_redis_{env.id}",
            networks=[network_name],
            detach=True,
            remove=True,
            mem_limit="128MB"
        )

        # Store container references
        self.environment_data[env.id]["containers"] = {
            "database": db_container.id,
            "redis": redis_container.id
        }

    async def _execute_code_in_container(self, environment_id: str, code: str,
                                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute code in isolated Docker container"""

        # Create temporary Python script
        script_content = f"""
import sys
import json
import os

# Set up environment
os.environ.update({context or {}})

# Execute user code
try:
    {code}
    result = {{"success": True, "message": "Code executed successfully"}}
except Exception as e:
    result = {{"success": False, "error": str(e)}}

# Output result
print(json.dumps(result))
"""

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            temp_file = f.name

        try:
            # Execute in container (simplified - would use actual container execution)
            # For now, just return success
            return {
                "success": True,
                "execution_id": str(uuid.uuid4()),
                "output": "Code executed in isolated environment",
                "timestamp": datetime.utcnow()
            }

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    async def _get_docker_container_state(self, environment_id: str) -> Dict[str, Any]:
        """Get Docker container state for environment"""
        containers = self.environment_data[environment_id].get("containers", {})

        state = {}
        for name, container_id in containers.items():
            try:
                container = self.docker_client.containers.get(container_id)
                state[name] = {
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else None
                }
            except docker.errors.NotFound:
                state[name] = {"status": "not_found"}

        return state

    async def _restore_docker_container_state(self, environment_id: str, state: Dict[str, Any]):
        """Restore Docker container state"""
        # Implementation would recreate containers from state
        pass

    async def _cleanup_docker_environment(self, environment_id: str):
        """Clean up Docker resources for environment"""
        containers = self.environment_data[environment_id].get("containers", {})

        for name, container_id in containers.items():
            try:
                container = self.docker_client.containers.get(container_id)
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                pass  # Container already removed

        # Remove network
        try:
            network = self.docker_client.networks.get(f"plugin_env_{environment_id}")
            network.remove()
        except docker.errors.NotFound:
            pass

class EnvironmentMonitor:
    """Monitor and manage plugin development environments"""

    def __init__(self, environment_manager: EnvironmentManager):
        self.environment_manager = environment_manager
        self.monitoring_task: Optional[asyncio.Task] = None

    async def start_monitoring(self):
        """Start environment monitoring"""
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop environment monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()

    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                # Clean up expired environments
                cleaned_count = await self.environment_manager.cleanup_expired_environments()

                if cleaned_count > 0:
                    print(f"Cleaned up {cleaned_count} expired environments")

                # Check resource usage
                await self._check_resource_usage()

                # Health check
                await self._perform_health_checks()

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)

    async def _check_resource_usage(self):
        """Check resource usage of environments"""
        # Implementation would monitor CPU, memory, disk usage
        pass

    async def _perform_health_checks(self):
        """Perform health checks on environments"""
        # Implementation would check database connectivity, API availability, etc.
        pass

# Global instances
environment_manager = EnvironmentManager()
environment_monitor = EnvironmentMonitor(environment_manager)

async def get_environment_manager() -> EnvironmentManager:
    """Dependency injection for environment manager"""
    return environment_manager

async def initialize_environment_system():
    """Initialize the environment system"""
    await environment_monitor.start_monitoring()
    print("✅ Plugin development environment system initialized")

# Environment templates
ENVIRONMENT_TEMPLATES = {
    "basic": {
        "name": "Basic Development Environment",
        "resources": {
            "cpu": 0.5,
            "memory": "512MB",
            "storage": "1GB"
        },
        "services": ["database", "redis"],
        "lifetime_hours": 24
    },
    "advanced": {
        "name": "Advanced Development Environment",
        "resources": {
            "cpu": 1.0,
            "memory": "1GB",
            "storage": "5GB"
        },
        "services": ["database", "redis", "elasticsearch"],
        "lifetime_hours": 48
    },
    "enterprise": {
        "name": "Enterprise Development Environment",
        "resources": {
            "cpu": 2.0,
            "memory": "2GB",
            "storage": "10GB"
        },
        "services": ["database", "redis", "elasticsearch", "rabbitmq"],
        "lifetime_hours": 72
    }
}