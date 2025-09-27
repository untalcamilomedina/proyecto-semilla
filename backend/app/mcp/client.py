"""
MCP Client for Proyecto Semilla modules
Enables modules to communicate with the MCP server and access system resources
"""

import asyncio
import json
import aiohttp
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .protocol import (
    MCPMessage, MCPInitializeRequest, MCPInitializeResponse,
    MCPListToolsRequest, MCPListToolsResponse,
    MCPListResourcesRequest, MCPListResourcesResponse,
    MCPListPromptsRequest, MCPListPromptsResponse,
    MCPCallToolRequest, MCPCallToolResponse,
    MCPReadResourceRequest, MCPReadResourceResponse,
    MCPGetPromptRequest, MCPGetPromptResponse,
    MCPError
)


class MCPClient:
    """
    MCP Client for module-to-server communication
    Provides a clean interface for modules to interact with MCP capabilities
    """

    def __init__(self, server_url: str = "http://localhost:8001", module_name: str = "unknown"):
        self.server_url = server_url.rstrip('/')
        self.module_name = module_name
        self.session: Optional[aiohttp.ClientSession] = None
        self.protocol_version = "2024-11-05"
        self.initialized = False
        self.client_info = {
            "name": f"Proyecto Semilla Module: {module_name}",
            "version": "1.0.0"
        }
        self.server_capabilities = {}

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Establish connection to MCP server"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

        # Initialize connection
        await self.initialize()

    async def disconnect(self):
        """Close connection to MCP server"""
        if self.session:
            await self.session.close()
            self.session = None
        self.initialized = False

    async def initialize(self) -> MCPInitializeResponse:
        """Initialize MCP connection"""
        if not self.session:
            raise RuntimeError("Client not connected")

        request = MCPInitializeRequest(
            protocolVersion=self.protocol_version,
            capabilities={
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            clientInfo=self.client_info
        )

        response = await self._send_request("initialize", {
            "protocolVersion": request.protocolVersion,
            "capabilities": request.capabilities,
            "clientInfo": request.clientInfo
        })

        if "error" in response:
            raise RuntimeError(f"MCP initialization failed: {response['error']}")

        init_response = MCPInitializeResponse(
            protocolVersion=response["result"]["protocolVersion"],
            capabilities=response["result"]["capabilities"],
            serverInfo=response["result"]["serverInfo"],
            instructions=response["result"].get("instructions")
        )

        self.initialized = True
        self.server_capabilities = init_response.capabilities

        return init_response

    async def list_tools(self, cursor: Optional[str] = None) -> MCPListToolsResponse:
        """List available MCP tools"""
        self._ensure_initialized()

        params = {}
        if cursor:
            params["cursor"] = cursor

        response = await self._send_request("tools/list", params)

        if "error" in response:
            raise RuntimeError(f"Failed to list tools: {response['error']}")

        tools_data = response["result"]["tools"]
        tools = []
        for tool_data in tools_data:
            # Convert back to MCPTool objects if needed
            tools.append(tool_data)  # For now, keep as dict

        return MCPListToolsResponse(
            tools=tools,
            nextCursor=response["result"].get("nextCursor")
        )

    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> MCPCallToolResponse:
        """Call an MCP tool"""
        self._ensure_initialized()

        params = {
            "name": name
        }
        if arguments:
            params["arguments"] = arguments

        response = await self._send_request("tools/call", params)

        if "error" in response:
            raise RuntimeError(f"Tool call failed: {response['error']}")

        result = response["result"]
        return MCPCallToolResponse(
            content=result["content"],
            isError=result.get("isError", False)
        )

    async def list_resources(self, cursor: Optional[str] = None) -> MCPListResourcesResponse:
        """List available MCP resources"""
        self._ensure_initialized()

        params = {}
        if cursor:
            params["cursor"] = cursor

        response = await self._send_request("resources/list", params)

        if "error" in response:
            raise RuntimeError(f"Failed to list resources: {response['error']}")

        resources_data = response["result"]["resources"]
        return MCPListResourcesResponse(
            resources=resources_data,
            nextCursor=response["result"].get("nextCursor")
        )

    async def read_resource(self, uri: str) -> MCPReadResourceResponse:
        """Read an MCP resource"""
        self._ensure_initialized()

        params = {"uri": uri}
        response = await self._send_request("resources/read", params)

        if "error" in response:
            raise RuntimeError(f"Failed to read resource: {response['error']}")

        result = response["result"]
        return MCPReadResourceResponse(contents=result["contents"])

    async def list_prompts(self, cursor: Optional[str] = None) -> MCPListPromptsResponse:
        """List available MCP prompts"""
        self._ensure_initialized()

        params = {}
        if cursor:
            params["cursor"] = cursor

        response = await self._send_request("prompts/list", params)

        if "error" in response:
            raise RuntimeError(f"Failed to list prompts: {response['error']}")

        prompts_data = response["result"]["prompts"]
        return MCPListPromptsResponse(
            prompts=prompts_data,
            nextCursor=response["result"].get("nextCursor")
        )

    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> MCPGetPromptResponse:
        """Get an MCP prompt"""
        self._ensure_initialized()

        params = {"name": name}
        if arguments:
            params["arguments"] = arguments

        response = await self._send_request("prompts/get", params)

        if "error" in response:
            raise RuntimeError(f"Failed to get prompt: {response['error']}")

        result = response["result"]
        return MCPGetPromptResponse(
            description=result["description"],
            messages=result["messages"]
        )

    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server"""
        if not self.session:
            raise RuntimeError("Client not connected")

        message = MCPMessage(method=method, params=params or {})
        payload = json.loads(message.to_json())

        try:
            async with self.session.post(
                f"{self.server_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}: {await resp.text()}")

                response_data = await resp.json()
                return response_data

        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error: {e}")

    def _ensure_initialized(self):
        """Ensure the client is initialized"""
        if not self.initialized:
            raise RuntimeError("MCP client not initialized. Call initialize() first.")

    # Convenience methods for common operations

    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information via MCP"""
        try:
            resource = await self.read_resource("proyecto-semilla://system/info")
            return resource.contents[0]["text"] if resource.contents else {}
        except:
            return {}

    async def list_modules(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List modules for a tenant"""
        try:
            result = await self.call_tool("modules_list", {"tenant_id": tenant_id})
            return result.content[0]["text"] if result.content else []
        except:
            return []

    async def install_module(self, tenant_id: str, name: str, version: str) -> Dict[str, Any]:
        """Install a module"""
        try:
            result = await self.call_tool("modules_install", {
                "tenant_id": tenant_id,
                "name": name,
                "version": version
            })
            return result.content[0]["text"] if result.content else {}
        except Exception as e:
            return {"error": str(e)}

    async def activate_module(self, tenant_id: str, module_id: str) -> Dict[str, Any]:
        """Activate a module"""
        try:
            result = await self.call_tool("modules_activate", {
                "tenant_id": tenant_id,
                "module_id": module_id
            })
            return result.content[0]["text"] if result.content else {}
        except Exception as e:
            return {"error": str(e)}

    async def get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information"""
        try:
            resource = await self.read_resource(f"proyecto-semilla://tenants/{tenant_id}")
            return resource.contents[0]["text"] if resource.contents else {}
        except:
            return {}


class ModuleMCPClient(MCPClient):
    """
    Specialized MCP client for modules with module-specific functionality
    """

    def __init__(self, server_url: str = "http://localhost:8001", module_name: str = "unknown", module_id: str = None):
        super().__init__(server_url, module_name)
        self.module_id = module_id

    async def register_module(self, tenant_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Register this module with the system"""
        try:
            result = await self.call_tool("modules_register", {
                "tenant_id": tenant_id,
                "module_name": self.module_name,
                "module_id": self.module_id,
                "config": config
            })
            return result.content[0]["text"] if result.content else {}
        except Exception as e:
            return {"error": str(e)}

    async def update_module_status(self, tenant_id: str, status: str) -> Dict[str, Any]:
        """Update module status"""
        try:
            result = await self.call_tool("modules_update_status", {
                "tenant_id": tenant_id,
                "module_id": self.module_id,
                "status": status
            })
            return result.content[0]["text"] if result.content else {}
        except Exception as e:
            return {"error": str(e)}

    async def get_module_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get module configuration"""
        try:
            result = await self.call_tool("modules_get_config", {
                "tenant_id": tenant_id,
                "module_id": self.module_id
            })
            return result.content[0]["text"] if result.content else {}
        except Exception as e:
            return {"error": str(e)}