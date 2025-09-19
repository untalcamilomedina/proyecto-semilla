"""
MCP Server for Proyecto Semilla
Provides tools and resources for LLMs to interact with the SaaS platform
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None


class MCPResource(BaseModel):
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"
    handler: Optional[Callable] = None


class MCPPrompt(BaseModel):
    """MCP Prompt definition"""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = []
    handler: Optional[Callable] = None


@dataclass
class MCPMessage:
    """MCP protocol message"""
    jsonrpc: str = "2.0"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class ProyectoSemillaMCPServer:
    """
    MCP Server for Proyecto Semilla
    Enables LLMs to interact with the SaaS platform through structured interfaces
    """

    def __init__(self, base_url: str = "http://localhost:7777"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self.app = FastAPI(title="Proyecto Semilla MCP Server", version="0.1.0")

        # Register core tools
        self._register_core_tools()

        # Register core resources
        self._register_core_resources()

        # Register core prompts
        self._register_core_prompts()

        # Setup routes
        self._setup_routes()

    def _register_core_tools(self):
        """Register core MCP tools for Proyecto Semilla operations"""

        # Authentication tools
        self.register_tool(MCPTool(
            name="auth_login",
            description="Authenticate a user and get access token",
            input_schema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User email"},
                    "password": {"type": "string", "description": "User password"}
                },
                "required": ["email", "password"]
            },
            handler=self._handle_auth_login
        ))

        # Tenant management tools
        self.register_tool(MCPTool(
            name="tenants_list",
            description="List all tenants in the system",
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 100, "description": "Maximum number of tenants to return"},
                    "skip": {"type": "integer", "default": 0, "description": "Number of tenants to skip"}
                }
            },
            handler=self._handle_tenants_list
        ))

        self.register_tool(MCPTool(
            name="tenants_create",
            description="Create a new tenant",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Tenant name"},
                    "slug": {"type": "string", "description": "Tenant slug (URL-friendly)"},
                    "description": {"type": "string", "description": "Tenant description"}
                },
                "required": ["name", "slug"]
            },
            handler=self._handle_tenants_create
        ))

        # User management tools
        self.register_tool(MCPTool(
            name="users_list",
            description="List users in a tenant",
            input_schema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID to filter users"},
                    "limit": {"type": "integer", "default": 100, "description": "Maximum number of users to return"},
                    "skip": {"type": "integer", "default": 0, "description": "Number of users to skip"}
                }
            },
            handler=self._handle_users_list
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
            uri="proyecto-semilla://docs/architecture",
            name="Architecture Documentation",
            description="System architecture and design documentation",
            mime_type="text/markdown",
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
            name="debug_issue",
            description="Help debug an issue in Proyecto Semilla",
            arguments=[
                {
                    "name": "error_message",
                    "description": "Error message or description of the issue",
                    "required": True
                },
                {
                    "name": "component",
                    "description": "Component where the issue occurs",
                    "required": False
                }
            ],
            handler=self._handle_debug_issue_prompt
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
                "version": "0.1.0",
                "description": "MCP Server for Proyecto Semilla SaaS platform",
                "capabilities": {
                    "tools": list(self.tools.keys()),
                    "resources": list(self.resources.keys()),
                    "prompts": list(self.prompts.keys())
                }
            }

        @self.app.post("/tools/call")
        async def call_tool(request: Request):
            """Call an MCP tool"""
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

        @self.app.get("/resources/{path:path}")
        async def get_resource(path: str):
            """Get an MCP resource"""
            resource_uri = f"proyecto-semilla://{path}"

            if resource_uri not in self.resources:
                raise HTTPException(status_code=404, detail=f"Resource '{resource_uri}' not found")

            resource = self.resources[resource_uri]
            if resource.handler:
                result = await resource.handler()
                return JSONResponse(content=result)
            else:
                raise HTTPException(status_code=501, detail=f"Resource '{resource_uri}' not implemented")

        @self.app.post("/prompts/call")
        async def call_prompt(request: Request):
            """Call an MCP prompt"""
            try:
                data = await request.json()
                prompt_name = data.get("name")
                arguments = data.get("arguments", {})

                if prompt_name not in self.prompts:
                    raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")

                prompt = self.prompts[prompt_name]
                if prompt.handler:
                    result = await prompt.handler(**arguments)
                    return {"result": result}
                else:
                    raise HTTPException(status_code=501, detail=f"Prompt '{prompt_name}' not implemented")

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    # Tool handlers
    async def _handle_auth_login(self, email: str, password: str):
        """Handle authentication login"""
        # This would make an actual API call to the backend
        return {
            "message": f"Login attempt for user {email}",
            "note": "This is a mock implementation. In production, this would authenticate with the actual API."
        }

    async def _handle_tenants_list(self, limit: int = 100, skip: int = 0):
        """Handle tenants listing"""
        return {
            "tenants": [
                {"id": "demo-tenant", "name": "Demo Company", "slug": "demo-company"}
            ],
            "total": 1,
            "limit": limit,
            "skip": skip
        }

    async def _handle_tenants_create(self, name: str, slug: str, description: str = None):
        """Handle tenant creation"""
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "slug": slug,
            "description": description,
            "status": "created"
        }

    async def _handle_users_list(self, tenant_id: str = None, limit: int = 100, skip: int = 0):
        """Handle users listing"""
        return {
            "users": [
                {"id": "demo-user", "email": "admin@demo.com", "name": "Demo Admin"}
            ],
            "total": 1,
            "limit": limit,
            "skip": skip
        }


    # Resource handlers
    async def _handle_system_info(self):
        """Handle system information resource"""
        return {
            "name": "Proyecto Semilla",
            "version": "0.1.0",
            "description": "Multi-tenant SaaS platform with Vibecoding capabilities",
            "features": [
                "Multi-tenancy with RLS",
                "JWT Authentication",
                "Audit Logging",
                "MCP Protocol Integration",
                "Docker deployment"
            ],
            "technologies": [
                "FastAPI",
                "PostgreSQL",
                "Redis",
                "Docker",
                "Python 3.11+"
            ]
        }

    async def _handle_tenant_info(self):
        """Handle tenant information resource"""
        return {
            "id": "demo-tenant",
            "name": "Demo Company",
            "slug": "demo-company",
            "description": "Demo tenant for testing",
            "features": ["auth", "tenants", "users", "articles"],
            "user_count": 1,
            "article_count": 0
        }

    async def _handle_architecture_docs(self):
        """Handle architecture documentation resource"""
        return """# Proyecto Semilla - Architecture Overview

## System Architecture

Proyecto Semilla is a multi-tenant SaaS platform built with modern technologies:

### Backend (FastAPI + Python)
- **Framework**: FastAPI for high-performance async APIs
- **Database**: PostgreSQL with Row-Level Security (RLS)
- **Cache**: Redis for session management and caching
- **ORM**: SQLAlchemy 2.0 with async support

### Frontend (Next.js + TypeScript)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui component library
- **State**: React hooks and context

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana (planned)

## Multi-tenancy Implementation

The system uses a shared database with schema separation:
- Each tenant has isolated data through RLS policies
- Tenant context is set via JWT tokens
- All queries are automatically filtered by tenant_id

## Security Features

- JWT-based authentication with refresh tokens
- Row-Level Security (RLS) in PostgreSQL
- Rate limiting and request throttling
- Comprehensive audit logging
- Input validation and sanitization

## MCP Protocol Integration

Proyecto Semilla includes native MCP (Model Context Protocol) support:
- Tools for CRUD operations
- Resources for system information
- Prompts for guided development
- Enables LLMs to understand and extend the platform
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
   └── tests/             # Unit tests
   ```

2. **Define Models**
   - Add tenant_id for multi-tenancy
   - Include created_at/updated_at timestamps
   - Add proper relationships

3. **Create API Endpoints**
   - Implement CRUD operations
   - Add proper error handling
   - Include request validation

4. **Add to Main Router**
   - Register routes in main application
   - Add to MCP tools if needed

5. **Create Database Migrations**
   - Use Alembic for schema changes
   - Test migrations thoroughly

## Best Practices

- Always include tenant_id in models
- Use async/await for database operations
- Add comprehensive error handling
- Include unit tests for all functions
- Document all endpoints with OpenAPI

Would you like me to start implementing this module structure?"""

    async def _handle_debug_issue_prompt(self, error_message: str, component: str = None):
        """Handle debug issue prompt"""
        return f"""# Debugging Issue

## Error Details
**Error**: {error_message}
**Component**: {component or 'Unknown'}

## Debugging Steps

1. **Check Logs**
   ```bash
   docker-compose logs backend | tail -50
   ```

2. **Verify Database Connection**
   ```bash
   docker-compose exec db psql -U admin -d proyecto_semilla
   ```

3. **Test API Endpoints**
   ```bash
   curl -X GET http://localhost:7777/api/v1/health
   ```

4. **Check Environment Variables**
   - Verify .env file exists
   - Check DATABASE_URL format
   - Confirm JWT_SECRET is set

5. **Common Issues**
   - Database connection timeout
   - Missing environment variables
   - Port conflicts (7777)
   - Redis connection issues

## Quick Fixes

**Database Connection Issue:**
```bash
docker-compose restart db
docker-compose restart backend
```

**Port Conflict:**
```bash
# Check what's using port 7777
lsof -i :7777
# Change port in docker-compose.yml if needed
```

Would you like me to help you run these diagnostic commands?"""


# Global MCP server instance
mcp_server = ProyectoSemillaMCPServer()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_server.app, host="0.0.0.0", port=8001)