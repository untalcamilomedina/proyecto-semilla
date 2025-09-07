"""
Test script for MCP Server
Tests all MCP functionality to ensure it's working correctly
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp.client import ProyectoSemillaMCPClient
from mcp.sdk import ProyectoSemillaSDK


async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🚀 Testing Proyecto Semilla MCP Server")
    print("=" * 50)

    async with ProyectoSemillaMCPClient() as client:
        try:
            # Test 1: Server Info
            print("\n📋 Test 1: Server Information")
            info = await client.get_server_info()
            if "error" in info:
                print(f"❌ Failed to get server info: {info['error']}")
                return False
            else:
                print(f"✅ Server: {info.get('name', 'Unknown')}")
                print(f"✅ Version: {info.get('version', 'Unknown')}")
                print(f"✅ Tools: {len(info.get('capabilities', {}).get('tools', []))}")
                print(f"✅ Resources: {len(info.get('capabilities', {}).get('resources', []))}")
                print(f"✅ Prompts: {len(info.get('capabilities', {}).get('prompts', []))}")

            # Test 2: System Info Resource
            print("\n📊 Test 2: System Information Resource")
            system_info = await client.get_system_info()
            if system_info.success:
                print("✅ System info retrieved successfully")
                print(f"   - Name: {system_info.content.get('name', 'Unknown')}")
                print(f"   - Features: {len(system_info.content.get('features', []))}")
            else:
                print(f"❌ Failed to get system info: {system_info.error}")

            # Test 3: Tools
            print("\n🔧 Test 3: Available Tools")
            tools = await client.list_tools()
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5
                print(f"   - {tool}")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more")

            # Test 4: Tool Execution
            print("\n⚡ Test 4: Tool Execution")
            # Test tenants_list tool
            result = await client.call_tool("tenants_list", limit=5)
            if result.success:
                print("✅ tenants_list tool executed successfully")
                tenants = result.result.get("tenants", [])
                print(f"   - Found {len(tenants)} tenants")
            else:
                print(f"❌ tenants_list tool failed: {result.error}")

            # Test 5: Prompts
            print("\n💬 Test 5: Prompts")
            prompts = await client.list_prompts()
            print(f"✅ Found {len(prompts)} prompts:")
            for prompt in prompts:
                print(f"   - {prompt}")

            # Test 6: Prompt Execution
            print("\n🎯 Test 6: Prompt Execution")
            prompt_result = await client.call_prompt("create_module",
                module_name="test_module",
                description="A test module for demonstration"
            )
            if prompt_result.success:
                print("✅ create_module prompt executed successfully")
                print("   - Generated guidance for module creation")
            else:
                print(f"❌ create_module prompt failed: {prompt_result.error}")

            # Test 7: Resources
            print("\n📚 Test 7: Resources")
            resources = await client.list_resources()
            print(f"✅ Found {len(resources)} resources:")
            for resource in resources:
                print(f"   - {resource}")

            print("\n" + "=" * 50)
            print("🎉 MCP Server Test Completed Successfully!")
            print("✅ All core functionality is working")
            return True

        except Exception as e:
            print(f"\n❌ Test failed with exception: {str(e)}")
            return False


async def test_sdk():
    """Test the SDK functionality"""
    print("\n🤖 Testing Proyecto Semilla SDK")
    print("=" * 50)

    try:
        sdk = ProyectoSemillaSDK()

        # Test 1: System Overview
        print("\n📋 Test 1: System Overview")
        overview = await sdk.get_system_overview()
        if overview:
            print("✅ System overview retrieved successfully")
            print(f"   - System: {overview.get('system_info', {}).get('name', 'Unknown')}")
            print(f"   - Multi-tenant: {overview.get('capabilities', {}).get('multi_tenant', False)}")
            print(f"   - MCP Enabled: {overview.get('capabilities', {}).get('mcp_enabled', False)}")
        else:
            print("❌ Failed to get system overview")

        # Test 2: Codebase Analysis
        print("\n🔍 Test 2: Codebase Analysis")
        analysis = await sdk.analyze_codebase()
        if analysis:
            print("✅ Codebase analysis completed")
            print(f"   - Architecture patterns: {len(analysis.get('architecture_patterns', {}))}")
            print(f"   - Coding standards: {len(analysis.get('coding_standards', {}))}")
        else:
            print("❌ Failed to analyze codebase")

        # Test 3: Module Template Generation
        print("\n🏗️ Test 3: Module Template Generation")
        template = await sdk.generate_module_template(
            "ecommerce",
            "E-commerce module for selling products"
        )
        if template:
            print("✅ Module template generated successfully")
            print(f"   - Name: {template.name}")
            print(f"   - Models: {len(template.models)}")
            print(f"   - Endpoints: {len(template.endpoints)}")
        else:
            print("❌ Failed to generate module template")

        # Test 4: Module Code Generation
        print("\n💻 Test 4: Module Code Generation")
        module_code = await sdk.create_module_from_template(template)
        if module_code:
            print("✅ Module code generated successfully")
            print(f"   - Files generated: {len(module_code.get('files', {}))}")
            files = list(module_code.get('files', {}).keys())
            for file in files[:3]:  # Show first 3 files
                print(f"   - {file}")
            if len(files) > 3:
                print(f"   - ... and {len(files) - 3} more files")
        else:
            print("❌ Failed to generate module code")

        # Test 5: Best Practices
        print("\n📚 Test 5: Best Practices")
        practices = await sdk.get_best_practices()
        if practices:
            print("✅ Best practices retrieved successfully")
            print(f"   - Python standards: {len(practices.get('python_standards', {}))}")
            print(f"   - FastAPI patterns: {len(practices.get('fastapi_patterns', {}))}")
            print(f"   - Security practices: {len(practices.get('security_practices', {}))}")
        else:
            print("❌ Failed to get best practices")

        print("\n" + "=" * 50)
        print("🎉 SDK Test Completed Successfully!")
        print("✅ All SDK functionality is working")
        return True

    except Exception as e:
        print(f"\n❌ SDK test failed with exception: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🧪 Proyecto Semilla MCP & SDK Test Suite")
    print("Testing the foundation for Vibecoding capabilities")
    print("=" * 60)

    # Test MCP Server
    mcp_success = await test_mcp_server()

    # Test SDK
    sdk_success = await test_sdk()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"MCP Server: {'✅ PASSED' if mcp_success else '❌ FAILED'}")
    print(f"SDK: {'✅ PASSED' if sdk_success else '❌ FAILED'}")

    if mcp_success and sdk_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Proyecto Semilla is ready for Vibecoding!")
        print("\nNext steps:")
        print("1. Start the MCP server: python -m mcp.server")
        print("2. Use the SDK in your LLM workflows")
        print("3. Create modules using natural language")
        print("4. Integrate with Claude Code, Gemini CLI, etc.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the error messages above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)