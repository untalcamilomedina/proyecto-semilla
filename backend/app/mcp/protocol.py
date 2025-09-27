"""
MCP Protocol definitions for Proyecto Semilla
Implements the Model Context Protocol standard for tool and resource management
"""

import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class MCPTool:
    """MCP Tool definition following the standard protocol"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    handler: Optional[callable] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP protocol format"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema
        }


@dataclass
class MCPResource:
    """MCP Resource definition following the standard protocol"""
    uri: str
    name: str
    description: str
    mimeType: str = "application/json"
    handler: Optional[callable] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP protocol format"""
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mimeType
        }


@dataclass
class MCPPrompt:
    """MCP Prompt definition following the standard protocol"""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)
    handler: Optional[callable] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP protocol format"""
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments
        }


@dataclass
class MCPMessage:
    """MCP protocol message following JSON-RPC 2.0"""
    jsonrpc: str = "2.0"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        """Convert message to JSON string"""
        data = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.method:
            data["method"] = self.method
        if self.params:
            data["params"] = self.params
        if self.result is not None:
            data["result"] = self.result
        if self.error:
            data["error"] = self.error
        return json.dumps(data, default=str)

    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class MCPInitializeRequest:
    """MCP Initialize request"""
    protocolVersion: str
    capabilities: Dict[str, Any]
    clientInfo: Dict[str, str]

    @classmethod
    def from_params(cls, params: Dict[str, Any]) -> 'MCPInitializeRequest':
        return cls(
            protocolVersion=params.get("protocolVersion", "2024-11-05"),
            capabilities=params.get("capabilities", {}),
            clientInfo=params.get("clientInfo", {})
        )


@dataclass
class MCPInitializeResponse:
    """MCP Initialize response"""
    protocolVersion: str
    capabilities: Dict[str, Any]
    serverInfo: Dict[str, str]
    instructions: Optional[str] = None

    def to_result(self) -> Dict[str, Any]:
        result = {
            "protocolVersion": self.protocolVersion,
            "capabilities": self.capabilities,
            "serverInfo": self.serverInfo
        }
        if self.instructions:
            result["instructions"] = self.instructions
        return result


@dataclass
class MCPListToolsRequest:
    """MCP List Tools request"""
    cursor: Optional[str] = None

    @classmethod
    def from_params(cls, params: Optional[Dict[str, Any]] = None) -> 'MCPListToolsRequest':
        if not params:
            return cls()
        return cls(cursor=params.get("cursor"))


@dataclass
class MCPListToolsResponse:
    """MCP List Tools response"""
    tools: List[MCPTool]
    nextCursor: Optional[str] = None

    def to_result(self) -> Dict[str, Any]:
        result = {
            "tools": [tool.to_dict() for tool in self.tools]
        }
        if self.nextCursor:
            result["nextCursor"] = self.nextCursor
        return result


@dataclass
class MCPListResourcesRequest:
    """MCP List Resources request"""
    cursor: Optional[str] = None

    @classmethod
    def from_params(cls, params: Optional[Dict[str, Any]] = None) -> 'MCPListResourcesRequest':
        if not params:
            return cls()
        return cls(cursor=params.get("cursor"))


@dataclass
class MCPListResourcesResponse:
    """MCP List Resources response"""
    resources: List[MCPResource]
    nextCursor: Optional[str] = None

    def to_result(self) -> Dict[str, Any]:
        result = {
            "resources": [resource.to_dict() for resource in self.resources]
        }
        if self.nextCursor:
            result["nextCursor"] = self.nextCursor
        return result


@dataclass
class MCPListPromptsRequest:
    """MCP List Prompts request"""
    cursor: Optional[str] = None

    @classmethod
    def from_params(cls, params: Optional[Dict[str, Any]] = None) -> 'MCPListPromptsRequest':
        if not params:
            return cls()
        return cls(cursor=params.get("cursor"))


@dataclass
class MCPListPromptsResponse:
    """MCP List Prompts response"""
    prompts: List[MCPPrompt]
    nextCursor: Optional[str] = None

    def to_result(self) -> Dict[str, Any]:
        result = {
            "prompts": [prompt.to_dict() for prompt in self.prompts]
        }
        if self.nextCursor:
            result["nextCursor"] = self.nextCursor
        return result


@dataclass
class MCPCallToolRequest:
    """MCP Call Tool request"""
    name: str
    arguments: Optional[Dict[str, Any]] = None

    @classmethod
    def from_params(cls, params: Dict[str, Any]) -> 'MCPCallToolRequest':
        return cls(
            name=params["name"],
            arguments=params.get("arguments", {})
        )


@dataclass
class MCPCallToolResponse:
    """MCP Call Tool response"""
    content: List[Dict[str, Any]]
    isError: bool = False

    def to_result(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "isError": self.isError
        }


@dataclass
class MCPReadResourceRequest:
    """MCP Read Resource request"""
    uri: str

    @classmethod
    def from_params(cls, params: Dict[str, Any]) -> 'MCPReadResourceRequest':
        return cls(uri=params["uri"])


@dataclass
class MCPReadResourceResponse:
    """MCP Read Resource response"""
    contents: List[Dict[str, Any]]

    def to_result(self) -> Dict[str, Any]:
        return {
            "contents": self.contents
        }


@dataclass
class MCPGetPromptRequest:
    """MCP Get Prompt request"""
    name: str
    arguments: Optional[Dict[str, Any]] = None

    @classmethod
    def from_params(cls, params: Dict[str, Any]) -> 'MCPGetPromptRequest':
        return cls(
            name=params["name"],
            arguments=params.get("arguments", {})
        )


@dataclass
class MCPGetPromptResponse:
    """MCP Get Prompt response"""
    description: str
    messages: List[Dict[str, Any]]

    def to_result(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "messages": self.messages
        }


class MCPError:
    """MCP Error codes and messages"""

    # Standard JSON-RPC errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # MCP-specific errors
    INVALID_PROTOCOL_VERSION = -32001
    TOOL_NOT_FOUND = -32002
    RESOURCE_NOT_FOUND = -32003
    PROMPT_NOT_FOUND = -32004
    MODULE_NOT_FOUND = -32005
    MODULE_ALREADY_EXISTS = -32006
    INVALID_MODULE_CONFIG = -32007

    @staticmethod
    def create_error(code: int, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
        """Create an MCP error response"""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data
        return error


class MCPProtocol:
    """
    MCP Protocol handler for Proyecto Semilla
    Manages the complete MCP communication lifecycle
    """

    def __init__(self):
        self.protocol_version = "2024-11-05"
        self.initialized = False
        self.client_capabilities = {}
        self.server_capabilities = {
            "tools": {
                "listChanged": True
            },
            "resources": {
                "listChanged": True,
                "subscribe": True
            },
            "prompts": {
                "listChanged": True
            },
            "logging": {}
        }

    def handle_initialize(self, request: MCPInitializeRequest) -> MCPInitializeResponse:
        """Handle initialize request"""
        self.initialized = True
        self.client_capabilities = request.capabilities

        return MCPInitializeResponse(
            protocolVersion=self.protocol_version,
            capabilities=self.server_capabilities,
            serverInfo={
                "name": "Proyecto Semilla MCP Server",
                "version": "1.0.0"
            },
            instructions="MCP server for Proyecto Semilla module management and system interaction"
        )

    def validate_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Validate incoming request parameters"""
        if not self.initialized and method != "initialize":
            return MCPError.create_error(
                MCPError.INVALID_REQUEST,
                "Server not initialized. Call 'initialize' first."
            )
        return None

    def create_success_response(self, request_id: str, result: Any) -> MCPMessage:
        """Create a successful response message"""
        return MCPMessage(
            id=request_id,
            result=result
        )

    def create_error_response(self, request_id: str, error: Dict[str, Any]) -> MCPMessage:
        """Create an error response message"""
        return MCPMessage(
            id=request_id,
            error=error
        )