"""
Proyecto Semilla SDK for LLMs
Provides high-level abstractions for LLMs to understand and extend the platform
"""

import asyncio
import json
import inspect
from typing import Dict, List, Any, Optional, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .client import ProyectoSemillaMCPClient


@dataclass
class ModuleTemplate:
    """Template for creating new modules"""
    name: str
    description: str
    models: List[Dict[str, Any]] = field(default_factory=list)
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    def add_model(self, name: str, fields: Dict[str, Any], description: str = ""):
        """Add a model to the module template"""
        self.models.append({
            "name": name,
            "fields": fields,
            "description": description
        })

    def add_endpoint(self, path: str, method: str, description: str = "", parameters: Dict[str, Any] = None):
        """Add an endpoint to the module template"""
        self.endpoints.append({
            "path": path,
            "method": method,
            "description": description,
            "parameters": parameters or {}
        })


class ProyectoSemillaSDK:
    """
    SDK for LLMs to interact with Proyecto Semilla
    Provides high-level abstractions and code generation capabilities
    """

    def __init__(self, mcp_client: Optional[ProyectoSemillaMCPClient] = None):
        self.client = mcp_client or ProyectoSemillaMCPClient()
        self.system_info = None
        self.architecture_docs = None

    async def initialize(self):
        """Initialize the SDK by loading system information"""
        if not self.system_info:
            system_result = await self.client.get_system_info()
            if system_result.success:
                self.system_info = system_result.content

        if not self.architecture_docs:
            docs_result = await self.client.get_architecture_docs()
            if docs_result.success:
                self.architecture_docs = docs_result.content

    async def get_system_overview(self) -> Dict[str, Any]:
        """Get a comprehensive overview of the Proyecto Semilla system"""
        await self.initialize()

        return {
            "system_info": self.system_info or {"name": "Proyecto Semilla", "version": "0.1.0"},
            "architecture": self.architecture_docs or "Architecture documentation not loaded",
            "capabilities": {
                "multi_tenant": True,
                "authentication": "JWT",
                "database": "PostgreSQL with RLS",
                "cache": "Redis",
                "mcp_enabled": True,
                "vibecoding_ready": True
            },
            "current_modules": [
                "authentication",
                "tenants",
                "users",
                "audit_logging"
            ]
        }

    async def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the codebase structure and patterns"""
        return {
            "architecture_patterns": {
                "dependency_injection": "FastAPI dependency system",
                "database_layer": "SQLAlchemy ORM with async support",
                "security_layer": "JWT + RLS policies",
                "middleware_stack": "Custom middleware for tenant context",
                "error_handling": "Structured error responses",
                "logging": "Comprehensive audit logging"
            },
            "coding_standards": {
                "language": "Python 3.11+",
                "framework": "FastAPI",
                "orm": "SQLAlchemy 2.0",
                "validation": "Pydantic",
                "async_await": "Required for all database operations",
                "type_hints": "Required for all functions",
                "docstrings": "Required for all modules"
            },
            "file_structure": {
                "backend/app/": "Main application code",
                "backend/app/api/v1/endpoints/": "API endpoints",
                "backend/app/models/": "SQLAlchemy models",
                "backend/app/schemas/": "Pydantic schemas",
                "backend/app/core/": "Core functionality",
                "backend/mcp/": "MCP protocol implementation"
            }
        }

    async def generate_module_template(self, module_name: str, description: str) -> ModuleTemplate:
        """Generate a module template based on the request"""
        template = ModuleTemplate(
            name=module_name,
            description=description
        )

        # Analyze the request to determine what models and endpoints are needed
        if "user" in module_name.lower() or "auth" in module_name.lower():
            template.add_model("CustomUser", {
                "tenant_id": "UUID (ForeignKey)",
                "custom_field": "String",
                "created_at": "DateTime",
                "updated_at": "DateTime"
            }, "Extended user model with custom fields")

        if "product" in module_name.lower() or "item" in module_name.lower():
            template.add_model("Product", {
                "tenant_id": "UUID (ForeignKey)",
                "name": "String",
                "description": "Text",
                "price": "Decimal",
                "category_id": "UUID (ForeignKey)",
                "created_at": "DateTime",
                "updated_at": "DateTime"
            }, "Product model for e-commerce functionality")

        # Add standard CRUD endpoints
        template.add_endpoint(f"/api/v1/{module_name}", "GET", f"List {module_name}")
        template.add_endpoint(f"/api/v1/{module_name}", "POST", f"Create {module_name}")
        template.add_endpoint(f"/api/v1/{module_name}/{{id}}", "GET", f"Get {module_name} by ID")
        template.add_endpoint(f"/api/v1/{module_name}/{{id}}", "PUT", f"Update {module_name}")
        template.add_endpoint(f"/api/v1/{module_name}/{{id}}", "DELETE", f"Delete {module_name}")

        # Add dependencies
        template.dependencies = ["fastapi", "sqlalchemy", "pydantic"]

        return template

    async def create_module_from_template(self, template: ModuleTemplate) -> Dict[str, Any]:
        """Create actual module files from a template"""
        module_code = {
            "models.py": self._generate_model_code(template),
            "schemas.py": self._generate_schema_code(template),
            "routes.py": self._generate_route_code(template),
            "services.py": self._generate_service_code(template),
            "__init__.py": f'"""Module: {template.name}"""\n\n__version__ = "0.1.0"'
        }

        return {
            "module_name": template.name,
            "description": template.description,
            "files": module_code,
            "setup_instructions": self._generate_setup_instructions(template)
        }

    def _generate_model_code(self, template: ModuleTemplate) -> str:
        """Generate SQLAlchemy model code"""
        code = f'''"""
SQLAlchemy models for {template.name} module
"""

from datetime import datetime
from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, UUID, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship

from app.core.database import Base


'''

        for model in template.models:
            code += f'''
class {model["name"]}(Base):
    """{model["description"]}"""
    __tablename__ = "{model["name"].lower()}s"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

'''

            for field_name, field_type in model["fields"].items():
                if field_name == "tenant_id":
                    continue  # Already added
                elif "String" in field_type:
                    code += f'    {field_name} = Column(String(255), nullable=True)\n'
                elif "Text" in field_type:
                    code += f'    {field_name} = Column(Text, nullable=True)\n'
                elif "Decimal" in field_type:
                    code += f'    {field_name} = Column(DECIMAL(10, 2), nullable=True)\n'
                elif "UUID" in field_type:
                    code += f'    {field_name} = Column(UUID(as_uuid=True), nullable=True)\n'
                elif "DateTime" in field_type:
                    code += f'    {field_name} = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)\n'

            code += '''
    # Relationships
    tenant = relationship("Tenant", back_populates="users")

    def __repr__(self):
        return f"<{model["name"]}(id={self.id}, tenant_id={self.tenant_id})>"
'''

        return code

    def _generate_schema_code(self, template: ModuleTemplate) -> str:
        """Generate Pydantic schema code"""
        code = f'''"""
Pydantic schemas for {template.name} module
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


'''

        for model in template.models:
            base_name = model["name"]
            code += f'''
class {base_name}Base(BaseModel):
    """Base schema for {base_name}"""
'''

            for field_name, field_type in model["fields"].items():
                if field_name in ["id", "tenant_id", "created_at", "updated_at"]:
                    continue
                if "String" in field_type:
                    code += f'    {field_name}: Optional[str] = None\n'
                elif "Text" in field_type:
                    code += f'    {field_name}: Optional[str] = None\n'
                elif "Decimal" in field_type:
                    code += f'    {field_name}: Optional[float] = None\n'
                elif "UUID" in field_type:
                    code += f'    {field_name}: Optional[UUID] = None\n'

            code += f'''


class {base_name}Create({base_name}Base):
    """Schema for creating {base_name}"""
    pass


class {base_name}Update(BaseModel):
    """Schema for updating {base_name}"""
'''

            for field_name, field_type in model["fields"].items():
                if field_name in ["id", "tenant_id", "created_at", "updated_at"]:
                    continue
                if "String" in field_type:
                    code += f'    {field_name}: Optional[str] = None\n'
                elif "Text" in field_type:
                    code += f'    {field_name}: Optional[str] = None\n'
                elif "Decimal" in field_type:
                    code += f'    {field_name}: Optional[float] = None\n'
                elif "UUID" in field_type:
                    code += f'    {field_name}: Optional[UUID] = None\n'

            code += f'''


class {base_name}Response({base_name}Base):
    """Response schema for {base_name}"""
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
'''

        return code

    def _generate_route_code(self, template: ModuleTemplate) -> str:
        """Generate FastAPI route code"""
        code = f'''"""
API routes for {template.name} module
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
'''

        # Import schemas
        for model in template.models:
            base_name = model["name"]
            code += f'from app.schemas.{template.name} import {base_name}Create, {base_name}Response, {base_name}Update\n'

        code += f'''
router = APIRouter()


'''

        for model in template.models:
            base_name = model["name"]
            model_name_lower = base_name.lower()

            code += f'''@router.get("/", response_model=List[{base_name}Response])
async def read_{model_name_lower}s(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve {model_name_lower}s with pagination
    """
    result = await db.execute(
        text("SELECT * FROM {model_name_lower}s WHERE tenant_id = :tenant_id ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
        {{"tenant_id": str(current_user.tenant_id), "limit": limit, "offset": skip}}
    )
    items = result.fetchall()

    # Convert to response format
    response_list = []
    for row in items:
        item_dict = {{
            "id": str(row[0]),
            "tenant_id": str(row[1]),
'''

            # Add fields
            field_index = 2
            for field_name, field_type in model["fields"].items():
                if field_name in ["id", "tenant_id"]:
                    continue
                elif field_name in ["created_at", "updated_at"]:
                    code += f'            "{field_name}": row[{field_index}],\n'
                else:
                    code += f'            "{field_name}": row[{field_index}],\n'
                field_index += 1

            code += f'''        }}
        response_list.append(item_dict)

    return response_list


@router.post("/", response_model={base_name}Response)
async def create_{model_name_lower}(
    item_in: {base_name}Create,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new {model_name_lower}
    """
    # Implementation here
    return {{"message": "Create {model_name_lower} endpoint - TODO"}}


@router.get("/{{item_id}}", response_model={base_name}Response)
async def read_{model_name_lower}(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get {model_name_lower} by ID
    """
    # Implementation here
    return {{"message": "Read {model_name_lower} endpoint - TODO"}}


@router.put("/{{item_id}}", response_model={base_name}Response)
async def update_{model_name_lower}(
    item_id: UUID,
    item_in: {base_name}Update,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update {model_name_lower}
    """
    # Implementation here
    return {{"message": "Update {model_name_lower} endpoint - TODO"}}


@router.delete("/{{item_id}}")
async def delete_{model_name_lower}(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete {model_name_lower}
    """
    # Implementation here
    return {{"message": "Delete {model_name_lower} endpoint - TODO"}}


'''

        return code

    def _generate_service_code(self, template: ModuleTemplate) -> str:
        """Generate service/business logic code"""
        code = f'''"""
Business logic services for {template.name} module
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.{template.name} import {", ".join([model["name"] for model in template.models])}


class {template.name.title()}Service:
    """Service class for {template.name} business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_items_by_tenant(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get items for a specific tenant"""
        # Implementation here
        return []

    async def create_item(self, tenant_id: UUID, item_data: dict) -> dict:
        """Create a new item"""
        # Implementation here
        return {{"message": "Create item service - TODO"}}

    async def get_item(self, item_id: UUID, tenant_id: UUID) -> Optional[dict]:
        """Get a specific item"""
        # Implementation here
        return None

    async def update_item(self, item_id: UUID, tenant_id: UUID, item_data: dict) -> dict:
        """Update an item"""
        # Implementation here
        return {{"message": "Update item service - TODO"}}

    async def delete_item(self, item_id: UUID, tenant_id: UUID) -> bool:
        """Delete an item"""
        # Implementation here
        return True
'''

        return code

    def _generate_setup_instructions(self, template: ModuleTemplate) -> str:
        """Generate setup instructions for the module"""
        return f'''# Setup Instructions for {template.name} Module

## 1. Create Module Directory
```bash
mkdir -p backend/app/modules/{template.name}
```

## 2. Create Files
Create the following files in `backend/app/modules/{template.name}/`:

- `__init__.py`
- `models.py`
- `schemas.py`
- `routes.py`
- `services.py`

## 3. Register Module
Add to `backend/app/main.py`:
```python
from app.modules.{template.name}.routes import router as {template.name}_router

app.include_router({template.name}_router, prefix=f"/api/v1/{template.name}")
```

## 4. Create Database Migration
```bash
cd backend
alembic revision --autogenerate -m "add {template.name} tables"
alembic upgrade head
```

## 5. Test Endpoints
```bash
curl http://localhost:7777/api/v1/{template.name}
```

## Dependencies
{chr(10).join(f"- {dep}" for dep in template.dependencies)}

## Next Steps
1. Implement the TODO sections in the generated code
2. Add proper error handling
3. Create unit tests
4. Update API documentation
5. Add to MCP tools if needed
'''

    async def get_best_practices(self) -> Dict[str, Any]:
        """Get coding best practices for Proyecto Semilla"""
        return {
            "python_standards": {
                "version": "Python 3.11+",
                "imports": "Standard library first, then third-party, then local",
                "naming": "snake_case for functions/variables, PascalCase for classes",
                "docstrings": "Google style docstrings for all public functions"
            },
            "fastapi_patterns": {
                "dependency_injection": "Use Depends() for database sessions and user auth",
                "response_models": "Always use Pydantic response models",
                "error_handling": "Use HTTPException for API errors",
                "async_await": "Use async/await for all database operations"
            },
            "database_patterns": {
                "tenant_isolation": "Always include tenant_id in queries",
                "migrations": "Use Alembic for all schema changes",
                "indexes": "Add indexes for frequently queried columns",
                "constraints": "Use database constraints for data integrity"
            },
            "security_practices": {
                "input_validation": "Validate all inputs with Pydantic",
                "sql_injection": "Use parameterized queries only",
                "authentication": "Verify JWT tokens on all protected endpoints",
                "authorization": "Check permissions before operations"
            }
        }

    async def analyze_module_request(self, request: str) -> Dict[str, Any]:
        """Analyze a module request and provide implementation guidance"""
        analysis = {
            "request": request,
            "estimated_complexity": "medium",
            "suggested_models": [],
            "suggested_endpoints": [],
            "dependencies": [],
            "implementation_steps": []
        }

        # Simple analysis based on keywords
        if "user" in request.lower() or "auth" in request.lower():
            analysis["suggested_models"].append("CustomUser")
            analysis["suggested_endpoints"].extend([
                "POST /users/custom-fields",
                "GET /users/profile/extended",
                "PUT /users/preferences"
            ])
            analysis["estimated_complexity"] = "low"

        if "product" in request.lower() or "inventory" in request.lower():
            analysis["suggested_models"].extend(["Product", "Category", "Inventory"])
            analysis["suggested_endpoints"].extend([
                "GET /products/search",
                "POST /products/bulk-update",
                "GET /inventory/low-stock"
            ])
            analysis["estimated_complexity"] = "high"

        if "payment" in request.lower() or "billing" in request.lower():
            analysis["suggested_models"].extend(["Payment", "Subscription", "Invoice"])
            analysis["dependencies"].append("stripe")
            analysis["estimated_complexity"] = "high"

        analysis["implementation_steps"] = [
            "1. Create module template with SDK",
            "2. Generate models and schemas",
            "3. Implement CRUD endpoints",
            "4. Add business logic services",
            "5. Create database migrations",
            "6. Add unit tests",
            "7. Update documentation",
            "8. Register MCP tools (if needed)"
        ]

        return analysis


# Convenience functions for LLMs
async def create_module_from_description(description: str) -> Dict[str, Any]:
    """Create a module from a natural language description"""
    sdk = ProyectoSemillaSDK()
    await sdk.initialize()

    # Analyze the description
    analysis = await sdk.analyze_module_request(description)

    # Generate module name from description
    module_name = description.lower().replace(" ", "_").replace("-", "_")[:20]

    # Create template
    template = await sdk.generate_module_template(module_name, description)

    # Generate code
    module_code = await sdk.create_module_from_template(template)

    return {
        "analysis": analysis,
        "module_code": module_code,
        "next_steps": [
            "Review the generated code",
            "Customize models and endpoints as needed",
            "Implement the TODO sections",
            "Test the module thoroughly",
            "Create database migrations",
            "Update API documentation"
        ]
    }


async def get_system_capabilities() -> Dict[str, Any]:
    """Get comprehensive system capabilities for LLMs"""
    sdk = ProyectoSemillaSDK()
    return await sdk.get_system_overview()


async def get_coding_guidance() -> Dict[str, Any]:
    """Get coding guidance and best practices"""
    sdk = ProyectoSemillaSDK()
    return await sdk.get_best_practices()


if __name__ == "__main__":
    # Example usage
    async def demo():
        print("=== Proyecto Semilla SDK Demo ===")

        # Create a module from description
        result = await create_module_from_description("Create an e-commerce module for selling products")
        print(json.dumps(result, indent=2, default=str))

    asyncio.run(demo())