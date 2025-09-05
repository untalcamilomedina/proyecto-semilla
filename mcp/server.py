"""
Proyecto Semilla MCP Server - Model Context Protocol Implementation
Permite que LLMs como Claude interactúen con Proyecto Semilla automáticamente
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp import Server, Tool, Resource, ResourceTemplate
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from proyecto_semilla import ProyectoSemillaClient
from proyecto_semilla.models import (
    ModuleSpec, ModuleCategory, Tenant, User,
    ModuleStatus, GenerationResult
)
from proyecto_semilla.exceptions import (
    ProyectoSemillaError, AuthenticationError,
    APIError, ValidationError
)


class ProyectoSemillaMCPServer(Server):
    """
    MCP Server para Proyecto Semilla

    Proporciona herramientas y recursos que permiten a LLMs:
    - Generar módulos automáticamente desde especificaciones naturales
    - Gestionar tenants, usuarios y módulos
    - Actualizar documentación en tiempo real
    - Monitorear estado del sistema
    - Ejecutar operaciones administrativas
    """

    def __init__(
        self,
        instance_url: str = "http://localhost:7777",
        api_key: Optional[str] = None,
        auto_auth: bool = True
    ):
        """
        Initialize MCP Server

        Args:
            instance_url: URL of Proyecto Semilla instance
            api_key: API key for authentication
            auto_auth: Automatically authenticate when needed
        """
        super().__init__("proyecto-semilla-mcp")

        self.instance_url = instance_url
        self.api_key = api_key
        self.auto_auth = auto_auth
        self.client: Optional[ProyectoSemillaClient] = None
        self.authenticated = False

        # Initialize tools and resources
        self._register_tools()
        self._register_resources()

        self.logger.info("Proyecto Semilla MCP Server initialized")

    async def _ensure_client(self) -> ProyectoSemillaClient:
        """Ensure Proyecto Semilla client is initialized and authenticated"""
        if self.client is None:
            self.client = ProyectoSemillaClient(
                base_url=self.instance_url,
                api_key=self.api_key,
                auto_refresh=True
            )

        if self.auto_auth and not self.authenticated:
            try:
                # Health check to verify connection
                health = await self.client.health_check()
                if health['status'] == 'healthy':
                    self.authenticated = True
                    self.logger.info("Successfully connected to Proyecto Semilla")
                else:
                    raise APIError(f"Health check failed: {health}")
            except Exception as e:
                self.logger.error(f"Failed to connect to Proyecto Semilla: {e}")
                raise

        return self.client

    def _register_tools(self):
        """Register all MCP tools"""

        # Tool 1: Generate Module
        @self.tool("generate_module")
        async def generate_module(
            name: str,
            description: str,
            category: str,
            features: List[str],
            entities: Optional[List[Dict[str, Any]]] = None
        ) -> str:
            """
            Generate a complete module from natural language specification

            Args:
                name: Module name (snake_case)
                description: Human-readable description
                category: Module category (cms, inventory, crm, etc.)
                features: List of features to implement
                entities: Optional list of entities to create

            Returns:
                Success message with generation details
            """
            try:
                client = await self._ensure_client()

                # Validate category
                try:
                    module_category = ModuleCategory(category.lower())
                except ValueError:
                    valid_categories = [cat.value for cat in ModuleCategory]
                    return f"Error: Invalid category '{category}'. Valid categories: {', '.join(valid_categories)}"

                # Create module specification
                spec = ModuleSpec(
                    name=name,
                    display_name=name.replace('_', ' ').title(),
                    description=description,
                    category=module_category,
                    features=features,
                    entities=entities or []
                )

                # Generate module
                result = await client.generate_module(spec)

                return f"""✅ Module '{result.module_name}' generated successfully!

📊 Generation Summary:
• Files Created: {result.files_created}
• APIs Generated: {result.apis_generated}
• UI Components: {result.ui_components_created}
• Execution Time: {result.execution_time_seconds:.2f}s

🎯 Features Implemented:
{chr(10).join(f'• {feature}' for feature in features)}

The module is ready for deployment and use!"""

            except ValidationError as e:
                return f"❌ Validation Error: {e.message}"
            except AuthenticationError:
                return "❌ Authentication Error: Please check your API credentials"
            except APIError as e:
                return f"❌ API Error: {e.message}"
            except Exception as e:
                self.logger.error(f"Module generation failed: {e}")
                return f"❌ Unexpected error during module generation: {str(e)}"

        # Tool 2: List Tenants
        @self.tool("list_tenants")
        async def list_tenants() -> str:
            """
            Get list of all available tenants

            Returns:
                Formatted list of tenants with details
            """
            try:
                client = await self._ensure_client()
                tenants = await client.get_tenants()

                if not tenants:
                    return "📭 No tenants found in the system"

                result = f"🏢 **Available Tenants ({len(tenants)})**\n\n"
                for tenant in tenants:
                    result += f"**{tenant.name}**\n"
                    result += f"• Slug: `{tenant.slug}`\n"
                    result += f"• Status: {'✅ Active' if tenant.is_active else '❌ Inactive'}\n"
                    result += f"• Created: {tenant.created_at.strftime('%Y-%m-%d')}\n\n"

                return result

            except AuthenticationError:
                return "❌ Authentication Error: Admin access required for tenant listing"
            except Exception as e:
                return f"❌ Error listing tenants: {str(e)}"

        # Tool 3: Create User
        @self.tool("create_user")
        async def create_user(
            email: str,
            password: str,
            tenant_id: str,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None
        ) -> str:
            """
            Create a new user in specified tenant

            Args:
                email: User email address
                password: User password
                tenant_id: Tenant ID where user will be created
                first_name: Optional first name
                last_name: Optional last name

            Returns:
                Success message with user details
            """
            try:
                client = await self._ensure_client()

                from proyecto_semilla.models import UserCreate
                user_data = UserCreate(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    tenant_id=tenant_id
                )

                user = await client.create_user(user_data)

                result = f"✅ User created successfully!\n\n"
                result += f"👤 **{user.full_name or user.email}**\n"
                result += f"• Email: {user.email}\n"
                result += f"• Tenant: {user.tenant_id}\n"
                result += f"• Status: {'✅ Active' if user.is_active else '❌ Inactive'}\n"
                result += f"• Email Verified: {'✅ Yes' if user.is_verified else '❌ No'}\n"

                return result

            except ValidationError as e:
                return f"❌ Validation Error: {e.message}"
            except Exception as e:
                return f"❌ Error creating user: {str(e)}"

        # Tool 4: Get Module Status
        @self.tool("get_module_status")
        async def get_module_status(module_name: str) -> str:
            """
            Check status of a generated module

            Args:
                module_name: Name of the module to check

            Returns:
                Detailed status information
            """
            try:
                client = await self._ensure_client()
                status = await client.get_module_status(module_name)

                result = f"📦 **Module: {module_name}**\n\n"
                result += f"**Status:** {status.status.upper()}\n"
                result += f"**Description:** {status.description}\n\n"

                if status.files_count:
                    result += f"📁 **Files:** {status.files_count}\n"
                if status.api_endpoints_count:
                    result += f"🔌 **API Endpoints:** {status.api_endpoints_count}\n"
                if status.ui_components_count:
                    result += f"🖥️ **UI Components:** {status.ui_components_count}\n"

                result += f"\n🕒 **Last Updated:** {status.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"

                return result

            except Exception as e:
                return f"❌ Error getting module status: {str(e)}"

        # Tool 5: Deploy Module
        @self.tool("deploy_module")
        async def deploy_module(module_name: str, tenant_id: str) -> str:
            """
            Deploy module to specific tenant

            Args:
                module_name: Name of module to deploy
                tenant_id: Target tenant ID

            Returns:
                Deployment result
            """
            try:
                client = await self._ensure_client()
                success = await client.deploy_module(module_name, tenant_id)

                if success:
                    return f"✅ Module '{module_name}' deployed successfully to tenant '{tenant_id}'!\n\nThe module is now available for use in the specified tenant."
                else:
                    return f"❌ Failed to deploy module '{module_name}' to tenant '{tenant_id}'"

            except Exception as e:
                return f"❌ Error deploying module: {str(e)}"

        # Tool 6: Update Documentation
        @self.tool("update_documentation")
        async def update_documentation(module_name: str) -> str:
            """
            Update auto-generated documentation for module

            Args:
                module_name: Name of module to update docs for

            Returns:
                Documentation update result
            """
            try:
                client = await self._ensure_client()
                result = await client.update_module_docs(module_name)

                update_msg = f"✅ Documentation updated for module '{module_name}'!\n\n"
                update_msg += f"📚 **Files Updated:** {result['files_updated']}\n"

                if result.get('readme_generated'):
                    update_msg += "• README.md generated/updated\n"
                if result.get('api_docs_generated'):
                    update_msg += "• API documentation updated\n"
                if result.get('index_updated'):
                    update_msg += "• Main index updated\n"

                return update_msg

            except Exception as e:
                return f"❌ Error updating documentation: {str(e)}"

        # Tool 7: Analyze Codebase
        @self.tool("analyze_codebase")
        async def analyze_codebase() -> str:
            """
            Analyze current codebase structure and provide insights

            Returns:
                Comprehensive codebase analysis
            """
            try:
                client = await self._ensure_client()

                # Get system information
                health = await client.health_check()
                tenants = await client.get_tenants()
                modules = await client.list_modules()

                analysis = "🔍 **Proyecto Semilla Codebase Analysis**\n\n"

                # System Health
                analysis += f"🏥 **System Health:** {health['status'].upper()}\n"
                analysis += f"📊 **Response Time:** {health['response_time']:.2f}s\n"
                analysis += f"🏷️ **Version:** {health.get('version', 'Unknown')}\n\n"

                # Tenants
                analysis += f"🏢 **Tenants:** {len(tenants)}\n"
                active_tenants = sum(1 for t in tenants if t.is_active)
                analysis += f"✅ **Active:** {active_tenants}\n\n"

                # Modules
                analysis += f"📦 **Modules:** {len(modules)}\n"
                if modules:
                    status_counts = {}
                    for module in modules:
                        status_counts[module.status] = status_counts.get(module.status, 0) + 1

                    for status, count in status_counts.items():
                        analysis += f"• {status.title()}: {count}\n"

                # Recommendations
                analysis += "\n💡 **Recommendations:**\n"
                if health['status'] != 'healthy':
                    analysis += "• System health needs attention\n"
                if len(tenants) == 0:
                    analysis += "• Consider creating demo tenants\n"
                if len(modules) == 0:
                    analysis += "• Generate your first module to get started\n"

                return analysis

            except Exception as e:
                return f"❌ Error analyzing codebase: {str(e)}"

        # Tool 8: Generate API Tests
        @self.tool("generate_api_tests")
        async def generate_api_tests(module_name: str) -> str:
            """
            Generate comprehensive API tests for module

            Args:
                module_name: Name of module to generate tests for

            Returns:
                Test generation result
            """
            try:
                client = await self._ensure_client()

                # This would integrate with a test generation service
                # For now, return a placeholder
                return f"🧪 Test generation for module '{module_name}' is not yet implemented.\n\nThis feature will be available in a future update."

            except Exception as e:
                return f"❌ Error generating API tests: {str(e)}"

        # Tool 9: Optimize Performance
        @self.tool("optimize_performance")
        async def optimize_performance(module_name: str) -> str:
            """
            Analyze and optimize module performance

            Args:
                module_name: Name of module to optimize

            Returns:
                Performance optimization results
            """
            try:
                client = await self._ensure_client()

                # This would integrate with a performance analysis service
                # For now, return a placeholder
                return f"⚡ Performance optimization for module '{module_name}' is not yet implemented.\n\nThis feature will be available in a future update."

            except Exception as e:
                return f"❌ Error optimizing performance: {str(e)}"

    def _register_resources(self):
        """Register MCP resources"""

        # Resource 1: Architecture Overview
        @self.resource("proyecto-semilla://architecture")
        async def get_architecture() -> str:
            """Get current system architecture information"""
            try:
                client = await self._ensure_client()

                # Get basic system info
                health = await client.health_check()
                tenants = await client.get_tenants()

                architecture = f"""# Proyecto Semilla Architecture

## System Overview
- **Status**: {health['status']}
- **Version**: {health.get('version', 'Unknown')}
- **Tenants**: {len(tenants)}
- **Base URL**: {self.instance_url}

## Multi-Tenant Architecture
Proyecto Semilla implements a robust multi-tenant architecture with:
- Row-Level Security (RLS) for data isolation
- Tenant-specific configurations
- Shared infrastructure with tenant boundaries

## Module System
- Dynamic module loading and deployment
- Auto-generated APIs and UI components
- Type-safe module specifications
- Real-time documentation updates

## Vibecoding Integration
- MCP Protocol for LLM integration
- Auto-generation from natural language
- Type-safe SDK for programmatic access
- Comprehensive error handling and validation
"""

                return architecture

            except Exception as e:
                return f"Error retrieving architecture: {str(e)}"

        # Resource 2: Database Schema
        @self.resource("proyecto-semilla://database/schema")
        async def get_database_schema() -> str:
            """Get current database schema information"""
            schema = """# Database Schema - Proyecto Semilla

## Core Tables

### tenants
- id: UUID (Primary Key)
- name: VARCHAR(100)
- slug: VARCHAR(50) UNIQUE
- settings: JSONB
- is_active: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

### users
- id: UUID (Primary Key)
- tenant_id: UUID (Foreign Key)
- email: VARCHAR(255) UNIQUE
- first_name: VARCHAR(50)
- last_name: VARCHAR(50)
- is_active: BOOLEAN
- is_verified: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

### modules
- id: UUID (Primary Key)
- name: VARCHAR(100)
- display_name: VARCHAR(100)
- description: TEXT
- category: VARCHAR(50)
- version: VARCHAR(20)
- status: VARCHAR(20)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

## Security Features
- Row-Level Security (RLS) enabled
- Tenant-based data isolation
- JWT authentication with refresh tokens
- API key authentication support

## Indexes
- tenants(slug) - UNIQUE
- users(tenant_id, email) - UNIQUE
- users(tenant_id) - Performance
- modules(name) - UNIQUE
"""
            return schema

        # Resource 3: API Endpoints
        @self.resource("proyecto-semilla://api/endpoints")
        async def get_api_endpoints() -> str:
            """Get all available API endpoints"""
            endpoints = """# API Endpoints - Proyecto Semilla

## Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

## Tenants
- `GET /tenants/` - List all tenants (admin)
- `POST /tenants/` - Create tenant (admin)
- `GET /tenants/{id}` - Get tenant details
- `PUT /tenants/{id}` - Update tenant
- `DELETE /tenants/{id}` - Delete tenant

## Users
- `GET /users/` - List users (filtered by tenant)
- `POST /users/` - Create user
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

## Modules
- `POST /modules/generate` - Generate new module
- `GET /modules/` - List all modules
- `GET /modules/{name}/status` - Get module status
- `POST /modules/{name}/deploy` - Deploy module to tenant
- `POST /modules/{name}/update-docs` - Update module documentation

## Health & Monitoring
- `GET /health` - System health check
- `GET /` - API information

## Response Format
All endpoints return JSON with the following structure:
```json
{
  "success": true|false,
  "data": { ... } | null,
  "message": "Optional message",
  "errors": ["Error messages"] | null
}
```

## Authentication
Include Bearer token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting
- 100 requests per minute per IP
- 1000 requests per hour per user
"""
            return endpoints

    async def run(self):
        """Run the MCP server"""
        self.logger.info("Starting Proyecto Semilla MCP Server...")
        # Server run logic would go here
        # This would integrate with the MCP protocol