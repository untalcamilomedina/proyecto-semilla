#!/usr/bin/env python3
"""
Script to run the Proyecto Semilla MCP Server
This server enables LLMs to interact with the SaaS platform
"""

import uvicorn
import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server import mcp_server

if __name__ == "__main__":
    print("🚀 Starting Proyecto Semilla MCP Server")
    print("🤖 Enabling Vibecoding capabilities for LLMs")
    print("📡 Server will be available at http://localhost:8001")
    print("📚 API documentation at http://localhost:8001/docs")
    print("=" * 60)

    uvicorn.run(
        "mcp.server:mcp_server.app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )