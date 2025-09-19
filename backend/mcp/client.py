"""
MCP Client for Proyecto Semilla
Client library for LLMs to interact with the MCP server
"""

import asyncio
import json
import httpx
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class MCPToolResult:
    """Result from calling an MCP tool"""
    success: bool
    result: Any = None
    error: Optional[str] = None


@dataclass
class MCPResourceResult:
    """Result from getting an MCP resource"""
    success: bool
    content: Any = None
    mime_type: str = "application/json"
    error: Optional[str] = None


class ProyectoSemillaMCPClient:
    """
    MCP Client for Proyecto Semilla
    Enables LLMs to interact with the SaaS platform through structured interfaces
    """

    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        self.mcp_server_url = mcp_server_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def get_server_info(self) -> Dict[str, Any]:
        """Get information about the MCP server"""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to get server info: {str(e)}"}

    async def list_tools(self) -> List[str]:
        """List available MCP tools"""
        info = await self.get_server_info()
        return info.get("capabilities", {}).get("tools", [])

    async def list_resources(self) -> List[str]:
        """List available MCP resources"""
        info = await self.get_server_info()
        return info.get("capabilities", {}).get("resources", [])

    async def list_prompts(self) -> List[str]:
        """List available MCP prompts"""
        info = await self.get_server_info()
        return info.get("capabilities", {}).get("prompts", [])

    async def call_tool(self, tool_name: str, **arguments) -> MCPToolResult:
        """Call an MCP tool"""
        try:
            payload = {
                "name": tool_name,
                "arguments": arguments
            }

            response = await self.client.post(
                f"{self.mcp_server_url}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            return MCPToolResult(
                success=True,
                result=result.get("result")
            )

        except Exception as e:
            return MCPToolResult(
                success=False,
                error=str(e)
            )

    async def get_resource(self, resource_path: str) -> MCPResourceResult:
        """Get an MCP resource"""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/resources/{resource_path}")
            response.raise_for_status()

            content = response.json()
            return MCPResourceResult(
                success=True,
                content=content,
                mime_type=response.headers.get("content-type", "application/json")
            )

        except Exception as e:
            return MCPResourceResult(
                success=False,
                error=str(e)
            )

    async def call_prompt(self, prompt_name: str, **arguments) -> MCPToolResult:
        """Call an MCP prompt"""
        try:
            payload = {
                "name": prompt_name,
                "arguments": arguments
            }

            response = await self.client.post(
                f"{self.mcp_server_url}/prompts/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            return MCPToolResult(
                success=True,
                result=result.get("result")
            )

        except Exception as e:
            return MCPToolResult(
                success=False,
                error=str(e)
            )

    # Convenience methods for common operations

    async def authenticate_user(self, email: str, password: str) -> MCPToolResult:
        """Authenticate a user"""
        return await self.call_tool("auth_login", email=email, password=password)

    async def list_tenants(self, limit: int = 100, skip: int = 0) -> MCPToolResult:
        """List tenants"""
        return await self.call_tool("tenants_list", limit=limit, skip=skip)

    async def create_tenant(self, name: str, slug: str, description: str = None) -> MCPToolResult:
        """Create a new tenant"""
        return await self.call_tool("tenants_create", name=name, slug=slug, description=description)

    async def list_users(self, tenant_id: str = None, limit: int = 100, skip: int = 0) -> MCPToolResult:
        """List users"""
        return await self.call_tool("users_list", tenant_id=tenant_id, limit=limit, skip=skip)


    async def get_system_info(self) -> MCPResourceResult:
        """Get system information"""
        return await self.get_resource("system/info")

    async def get_tenant_info(self, tenant_id: str) -> MCPResourceResult:
        """Get tenant information"""
        return await self.get_resource(f"tenants/{tenant_id}")

    async def get_architecture_docs(self) -> MCPResourceResult:
        """Get architecture documentation"""
        return await self.get_resource("docs/architecture")

    async def create_module_prompt(self, module_name: str, description: str) -> MCPToolResult:
        """Get help creating a new module"""
        return await self.call_prompt("create_module", module_name=module_name, description=description)

    async def debug_issue_prompt(self, error_message: str, component: str = None) -> MCPToolResult:
        """Get help debugging an issue"""
        return await self.call_prompt("debug_issue", error_message=error_message, component=component)


# Example usage and testing functions
async def test_mcp_client():
    """Test the MCP client functionality"""
    async with ProyectoSemillaMCPClient() as client:
        print("=== MCP Client Test ===")

        # Test server info
        print("\n1. Server Info:")
        info = await client.get_server_info()
        print(json.dumps(info, indent=2))

        # Test tools
        print("\n2. Available Tools:")
        tools = await client.list_tools()
        print(tools)

        # Test resources
        print("\n3. Available Resources:")
        resources = await client.list_resources()
        print(resources)

        # Test prompts
        print("\n4. Available Prompts:")
        prompts = await client.list_prompts()
        print(prompts)

        # Test system info resource
        print("\n5. System Info Resource:")
        system_info = await client.get_system_info()
        if system_info.success:
            print(json.dumps(system_info.content, indent=2))
        else:
            print(f"Error: {system_info.error}")

        # Test create module prompt
        print("\n6. Create Module Prompt:")
        module_help = await client.create_module_prompt(
            module_name="ecommerce",
            description="E-commerce module for selling products"
        )
        if module_help.success:
            print(module_help.result)
        else:
            print(f"Error: {module_help.error}")


if __name__ == "__main__":
    asyncio.run(test_mcp_client())