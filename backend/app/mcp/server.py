"""
Extended MCP Server for Proyecto Semilla with Module Management
Provides tools and resources for module lifecycle management and system interaction
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .protocol import (
    MCPTool, MCPResource, MCPPrompt, MCPMessage,
    MCPInitializeRequest, MCPInitializeResponse,
    MCPListToolsRequest, MCPListToolsResponse,
    MCPListResourcesRequest, MCPListResourcesResponse,
    MCPListPromptsRequest, MCPListPromptsResponse,
    MCPCallToolRequest, MCPCallToolResponse,
    MCPReadResourceRequest, MCPReadResourceResponse,
    MCPGetPromptRequest, MCPGetPromptResponse,
    MCPError, MCPProtocol
)
from app.core.database import get_db
from app.services.module_service import ModuleService
from app.core.config import settings


class ProyectoSemillaMCPServer:
    """
    Extended MCP Server for Proyecto Semilla with full module management capabilities
    """

    def __init__(self, base_url: str = "http://localhost:7777"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.protocol = MCPProtocol()

        # MCP components
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}

        # FastAPI app
        self.app = FastAPI(
            title="Proyecto Semilla MCP Server",
            version="1.0.0",
            description="MCP Server with Module Management for Proyecto Semilla SaaS platform"
        )

        # Register core components
        self._register_core_tools()
        self._register_core_resources()
        self._register_core_prompts()

        # Setup routes
        self._setup_routes()

    def _register_core_tools(self):
        """Register core MCP tools including module management"""

        # Authentication tools
        self.register_tool(MCPTool(
            name="auth_login",
            description="Authenticate a user and get access token",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User email"},
                    "password": {"type": "string", "description": "User password"}
                },
                "required": ["email", "password"]
            },
            handler=self._handle_auth_login
        ))

        # Module management tools
        self.register_tool(MCPTool(
            name="modules_list",
            description="List modules for a tenant",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "status": {"type": "string", "description": "Filter by status (optional)"},
                    "limit": {"type": "integer", "default": 100, "description": "Maximum number of modules to return"},
                    "skip": {"type": "integer", "default": 0, "description": "Number of modules to skip"}
                },
                "required": ["tenant_id"]
            },
            handler=self._handle_modules_list
        ))

        self.register_tool(MCPTool(
            name="modules_install",
            description="Install a module for a tenant",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "name": {"type": "string", "description": "Module name"},
                    "version": {"type": "string", "description": "Module version"},
                    "config": {"type": "object", "description": "Module configuration (optional)"}
                },
                "required": ["tenant_id", "name", "version"]
            },
            handler=self._handle_modules_install
        ))

        self.register_tool(MCPTool(
            name="modules_activate",
            description="Activate a module",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "module_id": {"type": "string", "description": "Module ID"}
                },
                "required": ["tenant_id", "module_id"]
            },
            handler=self._handle_modules_activate
        ))

        self.register_tool(MCPTool(
            name="modules_deactivate",
            description="Deactivate a module",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "module_id": {"type": "string", "description": "Module ID"}
                },
                "required": ["tenant_id", "module_id"]
            },
            handler=self._handle_modules_deactivate
        ))

        self.register_tool(MCPTool(
            name="modules_uninstall",
            description="Uninstall a module",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "module_id": {"type": "string", "description": "Module ID"}
                },
                "required": ["tenant_id", "module_id"]
            },
            handler=self._handle_modules_uninstall
        ))

        self.register_tool(MCPTool(
            name="modules_update_config",
            description="Update module configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "module_id": {"type": "string", "description": "Module ID"},
                    "config": {"type": "object", "description": "New configuration"}
                },
                "required": ["tenant_id", "module_id", "config"]
            },
            handler=self._handle_modules_update_config
        ))

        self.register_tool(MCPTool(
            name="modules_discover",
            description="Discover available modules",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category (optional)"},
                    "limit": {"type": "integer", "default": 50, "description": "Maximum number of modules to return"}
                }
            },
            handler=self._handle_modules_discover
        ))

        # Tenant management tools
        self.register_tool(MCPTool(
            name="tenants_list",
            description="List all tenants in the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 100, "description": "Maximum number of tenants to return"},
                    "skip": {"type": "integer", "default": 0, "description": "Number of tenants to skip"}
                }
            },
            handler=self._handle_tenants_list
        ))

    def _register_core_resources(self):
        """Register core MCP resources"""

        self.register_resource(MCPResource(
            uri="proyecto-semilla://system/info",
            name="System Information",
            description="General information about Proyecto Semilla system",
            handler=self._handle_system_info
        ))

        self.register_resource(MCPResource(
            uri="proyecto-semilla://tenants/{tenant_id}",
            name="Tenant Information",
            description="Detailed information about a specific tenant",
            handler=self._handle_tenant_info
        ))

        self.register_resource(MCPResource(
            uri="proyecto-semilla://modules/{tenant_id}",
            name="Tenant Modules",
            description="List of modules installed for a tenant",
            handler=self._handle_tenant_modules
        ))

        self.register_resource(MCPResource(
            uri="proyecto-semilla://modules/{tenant_id}/{module_id}",
            name="Module Information",
            description="Detailed information about a specific module",
            handler=self._handle_module_info
        ))

        self.register_resource(MCPResource(
            uri="proyecto-semilla://docs/architecture",
            name="Architecture Documentation",
            description="System architecture and design documentation",
            mimeType="text/markdown",
            handler=self._handle_architecture_docs
        ))

    def _register_core_prompts(self):
        """Register core MCP prompts"""

        self.register_prompt(MCPPrompt(
            name="create_module",
            description="Help create a new module for Proyecto Semilla",
            arguments=[
                {
                    "name": "module_name",
                    "description": "Name of the module to create",
                    "required": True
                },
                {
                    "name": "description",
                    "description": "Description of what the module does",
                    "required": True
                }
            ],
            handler=self._handle_create_module_prompt
        ))

        self.register_prompt(MCPPrompt(
            name="debug_module_issue",
            description="Help debug a module-related issue",
            arguments=[
                {
                    "name": "module_name",
                    "description": "Name of the problematic module",
                    "required": True
                },
                {
                    "name": "error_message",
                    "description": "Error message or description of the issue",
                    "required": True
                }
            ],
            handler=self._handle_debug_module_prompt
        ))

    def register_tool(self, tool: MCPTool):
        """Register a new MCP tool"""
        self.tools[tool.name] = tool

    def register_resource(self, resource: MCPResource):
        """Register a new MCP resource"""
        self.resources[resource.uri] = resource

    def register_prompt(self, prompt: MCPPrompt):
        """Register a new MCP prompt"""
        self.prompts[prompt.name] = prompt

    def _setup_routes(self):
        """Setup FastAPI routes for MCP protocol"""

        @self.app.get("/")
        async def root():
            return {
                "name": "Proyecto Semilla MCP Server",
                "version": "1.0.0",
                "description": "MCP Server with Module Management for Proyecto Semilla SaaS platform",
                "capabilities": {
                    "tools": list(self.tools.keys()),
                    "resources": list(self.resources.keys()),
                    "prompts": list(self.prompts.keys())
                }
            }

        @self.app.post("/mcp")
        async def handle_mcp_request(request: Request, db: AsyncSession = Depends(get_db)):
            """Handle MCP JSON-RPC requests"""
            try:
                data = await request.json()
                message = MCPMessage.from_json(json.dumps(data))

                # Validate request
                validation_error = self.protocol.validate_request(message.method, message.params)
                if validation_error:
                    return self.protocol.create_error_response(message.id, validation_error).to_json()

                # Route to appropriate handler
                result = await self._handle_mcp_method(message.method, message.params, db)

                return self.protocol.create_success_response(message.id, result).to_json()

            except Exception as e:
                error = MCPError.create_error(MCPError.INTERNAL_ERROR, str(e))
                return self.protocol.create_error_response(data.get("id", "unknown"), error).to_json()

        # Legacy REST endpoints for backward compatibility
        @self.app.post("/tools/call")
        async def call_tool(request: Request):
            """Legacy tool call endpoint"""
            try:
                data = await request.json()
                tool_name = data.get("name")
                arguments = data.get("arguments", {})

                if tool_name not in self.tools:
                    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

                tool = self.tools[tool_name]
                if tool.handler:
                    result = await tool.handler(**arguments)
                    return {"result": result}
                else:
                    raise HTTPException(status_code=501, detail=f"Tool '{tool_name}' not implemented")

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    async def _handle_mcp_method(self, method: str, params: Optional[Dict[str, Any]], db: AsyncSession) -> Any:
        """Handle MCP method calls"""
        if method == "initialize":
            request = MCPInitializeRequest.from_params(params or {})
            response = self.protocol.handle_initialize(request)
            return response.to_result()

        elif method == "tools/list":
            request = MCPListToolsRequest.from_params(params)
            tools = list(self.tools.values())
            response = MCPListToolsResponse(tools=tools)
            return response.to_result()

        elif method == "tools/call":
            request = MCPCallToolRequest.from_params(params)
            if request.name not in self.tools:
                raise ValueError(f"Tool '{request.name}' not found")

            tool = self.tools[request.name]
            if not tool.handler:
                raise ValueError(f"Tool '{request.name}' not implemented")

            # Call tool handler with database session
            result = await tool.handler(db=db, **(request.arguments or {}))
            response = MCPCallToolResponse(content=[{"type": "text", "text": json.dumps(result)}])
            return response.to_result()

        elif method == "resources/list":
            request = MCPListResourcesRequest.from_params(params)
            resources = list(self.resources.values())
            response = MCPListResourcesResponse(resources=resources)
            return response.to_result()

        elif method == "resources/read":
            request = MCPReadResourceRequest.from_params(params)
            if request.uri not in self.resources:
                raise ValueError(f"Resource '{request.uri}' not found")

            resource = self.resources[request.uri]
            if not resource.handler:
                raise ValueError(f"Resource '{request.uri}' not implemented")

            result = await resource.handler(db=db)
            response = MCPReadResourceResponse(
                contents=[{
                    "uri": request.uri,
                    "mimeType": resource.mimeType,
                    "text": json.dumps(result)
                }]
            )
            return response.to_result()

        elif method == "prompts/list":
            request = MCPListPromptsRequest.from_params(params)
            prompts = list(self.prompts.values())
            response = MCPListPromptsResponse(prompts=prompts)
            return response.to_result()

        elif method == "prompts/get":
            request = MCPGetPromptRequest.from_params(params)
            if request.name not in self.prompts:
                raise ValueError(f"Prompt '{request.name}' not found")

            prompt = self.prompts[request.name]
            if not prompt.handler:
                raise ValueError(f"Prompt '{request.name}' not implemented")

            result = await prompt.handler(**request.arguments)
            response = MCPGetPromptResponse(
                description=prompt.description,
                messages=[{"role": "user", "content": {"type": "text", "text": result}}]
            )
            return response.to_result()

        else:
            raise ValueError(f"Unknown method: {method}")

    # Tool handlers

    async def _handle_auth_login(self, email: str, password: str, **kwargs):
        """Handle authentication login"""
        return {
            "message": f"Login attempt for user {email}",
            "note": "This is a mock implementation. In production, this would authenticate with the actual API."
        }

    async def _handle_modules_list(self, tenant_id: str, status: Optional[str] = None, limit: int = 100, skip: int = 0, db: AsyncSession = None):
        """Handle modules listing"""
        modules = await ModuleService.get_modules(tenant_id, db, skip, limit)
        return [self._module_to_dict(module) for module in modules]

    async def _handle_modules_install(self, tenant_id: str, name: str, version: str, config: Optional[Dict[str, Any]] = None, db: AsyncSession = None):
        """Handle module installation"""
        module = await ModuleService.install_module(tenant_id, name, version, config, db)
        return self._module_to_dict(module)

    async def _handle_modules_activate(self, tenant_id: str, module_id: str, db: AsyncSession = None):
        """Handle module activation"""
        module = await ModuleService.activate_module(uuid.UUID(module_id), uuid.UUID(tenant_id), db)
        return self._module_to_dict(module)

    async def _handle_modules_deactivate(self, tenant_id: str, module_id: str, db: AsyncSession = None):
        """Handle module deactivation"""
        module = await ModuleService.deactivate_module(uuid.UUID(module_id), uuid.UUID(tenant_id), db)
        return self._module_to_dict(module)

    async def _handle_modules_uninstall(self, tenant_id: str, module_id: str, db: AsyncSession = None):
        """Handle module uninstallation"""
        success = await ModuleService.uninstall_module(uuid.UUID(module_id), uuid.UUID(tenant_id), db)
        return {"success": success}

    async def _handle_modules_update_config(self, tenant_id: str, module_id: str, config: Dict[str, Any], db: AsyncSession = None):
        """Handle module configuration update"""
        config_obj = await ModuleService.update_module_config(uuid.UUID(module_id), uuid.UUID(tenant_id), config, db)
        return {
            "module_id": str(config_obj.module_id),
            "tenant_id": str(config_obj.tenant_id),
            "config_data": config_obj.config_data
        }

    async def _handle_modules_discover(self, category: Optional[str] = None, limit: int = 50, db: AsyncSession = None):
        """Handle module discovery"""
        modules = await ModuleService.discover_available_modules(db)
        return modules[:limit]

    async def _handle_tenants_list(self, limit: int = 100, skip: int = 0, **kwargs):
        """Handle tenants listing"""
        return {
            "tenants": [
                {"id": "demo-tenant", "name": "Demo Company", "slug": "demo-company"}
            ],
            "total": 1,
            "limit": limit,
            "skip": skip
        }

    # Resource handlers

    async def _handle_system_info(self, **kwargs):
        """Handle system information resource"""
        return {
            "name": "Proyecto Semilla",
            "version": "1.0.0",
            "description": "Multi-tenant SaaS platform with MCP module system",
            "features": [
                "Multi-tenancy with RLS",
                "JWT Authentication",
                "MCP Protocol Integration",
                "Extensible Module System",
                "Hot-reload Capabilities"
            ],
            "technologies": [
                "FastAPI",
                "PostgreSQL",
                "Redis",
                "Docker",
                "Python 3.11+"
            ]
        }

    async def _handle_tenant_info(self, tenant_id: str, **kwargs):
        """Handle tenant information resource"""
        return {
            "id": tenant_id,
            "name": f"Tenant {tenant_id}",
            "slug": f"tenant-{tenant_id}",
            "description": f"Information for tenant {tenant_id}",
            "features": ["auth", "tenants", "users", "modules"],
            "user_count": 1,
            "module_count": 0
        }

    async def _handle_tenant_modules(self, tenant_id: str, db: AsyncSession = None):
        """Handle tenant modules resource"""
        modules = await ModuleService.get_modules(tenant_id, db)
        return [self._module_to_dict(module) for module in modules]

    async def _handle_module_info(self, tenant_id: str, module_id: str, db: AsyncSession = None):
        """Handle module information resource"""
        module = await ModuleService.get_module_by_id(uuid.UUID(module_id), uuid.UUID(tenant_id), db)
        if not module:
            raise ValueError("Module not found")
        return self._module_to_dict(module)

    async def _handle_architecture_docs(self, **kwargs):
        """Handle architecture documentation resource"""
        return """# Proyecto Semilla - Architecture Overview

## System Architecture

Proyecto Semilla is a multi-tenant SaaS platform with an extensible module system:

### Backend (FastAPI + Python)
- **Framework**: FastAPI for high-performance async APIs
- **Database**: PostgreSQL with Row-Level Security (RLS)
- **Cache**: Redis for session management and caching
- **ORM**: SQLAlchemy 2.0 with async support

### Module System
- **MCP Protocol**: Model Context Protocol for module communication
- **Hot-reload**: Dynamic module loading without downtime
- **Versioning**: Semantic versioning with dependency management
- **Configuration**: Tenant-specific module configuration

### Frontend (Next.js + TypeScript)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui component library

## Multi-tenancy Implementation

The system uses a shared database with schema separation:
- Each tenant has isolated data through RLS policies
- Tenant context is set via JWT tokens
- Module configurations are tenant-specific

## Security Features

- JWT-based authentication with refresh tokens
- Row-Level Security (RLS) in PostgreSQL
- Module sandboxing and isolation
- Comprehensive audit logging
"""

    # Prompt handlers

    async def _handle_create_module_prompt(self, module_name: str, description: str):
        """Handle create module prompt"""
        return f"""# Creating Module: {module_name}

## Module Description
{description}

## Implementation Steps

1. **Create Module Structure**
   ```
   backend/app/modules/{module_name}/
   ├── __init__.py
   ├── models.py          # SQLAlchemy models
   ├── schemas.py         # Pydantic schemas
   ├── routes.py          # FastAPI routes
   ├── services.py        # Business logic
   ├── mcp_client.py      # MCP communication
   └── tests/             # Unit tests
   ```

2. **Implement MCP Integration**
   - Register module with MCP server
   - Define module capabilities and tools
   - Implement communication protocols

3. **Add Module Metadata**
   - Define dependencies and compatibility
   - Create configuration schema
   - Set up health checks

4. **Register with System**
   - Add to module registry
   - Implement installation/uninstallation
   - Configure tenant-specific settings

## Best Practices

- Always include tenant_id in models
- Use async/await for all operations
- Implement proper error handling
- Add comprehensive logging
- Create unit tests for all functions

Would you like me to start implementing this module structure?"""

    async def _handle_debug_module_prompt(self, module_name: str, error_message: str):
        """Handle debug module prompt"""
        return f"""# Debugging Module Issue: {module_name}

## Error Details
**Module**: {module_name}
**Error**: {error_message}

## Debugging Steps

1. **Check Module Status**
   ```bash
   # Check if module is properly installed and active
   curl -X GET "http://localhost:7777/api/v1/modules/status?tenant_id=YOUR_TENANT&name={module_name}"
   ```

2. **Verify Configuration**
   - Check module configuration is valid
   - Verify tenant-specific settings
   - Validate dependencies

3. **Check Logs**
   ```bash
   # Check backend logs for module-related errors
   docker-compose logs backend | grep "{module_name}"
   ```

4. **Test MCP Communication**
   ```bash
   # Test if module can communicate with MCP server
   curl -X POST http://localhost:8001/mcp \\
     -H "Content-Type: application/json" \\
     -d '{{"jsonrpc": "2.0", "id": "1", "method": "tools/list"}}'
   ```

5. **Common Module Issues**
   - Configuration schema validation errors
   - Missing dependencies
   - Version compatibility issues
   - MCP protocol communication failures

## Quick Fixes

**Configuration Issue:**
```bash
# Update module configuration
curl -X PUT "http://localhost:7777/api/v1/modules/config" \\
  -H "Content-Type: application/json" \\
  -d '{{"tenant_id": "YOUR_TENANT", "module_id": "MODULE_ID", "config": {{}}}}'
```

Would you like me to help you diagnose this specific issue?"""

    def _module_to_dict(self, module) -> Dict[str, Any]:
        """Convert module object to dictionary"""
        return {
            "id": str(module.id),
            "tenant_id": str(module.tenant_id),
            "name": module.name,
            "display_name": module.display_name,
            "version": module.version,
            "description": module.description,
            "status": module.status,
            "is_system": module.is_system,
            "installed_at": module.installed_at.isoformat() if module.installed_at else None,
            "activated_at": module.activated_at.isoformat() if module.activated_at else None,
            "last_used_at": module.last_used_at.isoformat() if module.last_used_at else None,
            "created_at": module.created_at.isoformat(),
            "updated_at": module.updated_at.isoformat()
        }


# Global MCP server instance
mcp_server = ProyectoSemillaMCPServer()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_server.app, host="0.0.0.0", port=8001)