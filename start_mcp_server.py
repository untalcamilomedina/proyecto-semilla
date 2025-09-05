#!/usr/bin/env python3
"""
Startup script for Proyecto Semilla MCP Server
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project paths to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

def main():
    """Main entry point for MCP Server"""
    try:
        from mcp.server import ProyectoSemillaMCPServer
        
        # Get configuration from environment
        instance_url = os.getenv("PROYECTO_SEMILLA_URL", "http://localhost:7777")
        api_key = os.getenv("PROYECTO_SEMILLA_API_KEY")
        
        # Create and run server
        server = ProyectoSemillaMCPServer(
            instance_url=instance_url,
            api_key=api_key,
            auto_auth=True
        )
        
        # Run the server
        asyncio.run(server.run())
        
    except Exception as e:
        print(f"Error starting MCP Server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()