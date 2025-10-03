#!/usr/bin/env python3
"""
Test script for the Financial Agent MCP Server
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by sending MCP protocol messages"""
    
    print("🧪 Testing Financial Agent MCP Server")
    print("=" * 50)
    
    # Start the MCP server process
    process = subprocess.Popen(
        [sys.executable, "financial_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 Received: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Send list tools request
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("📤 Requesting available tools...")
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        
        # Read tools response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get('result', {}).get('tools', [])
            print(f"🔧 Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  • {tool['name']}: {tool['description']}")
        
        # Test a tool call
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_documents",
                "arguments": {"status_filter": "all"}
            }
        }
        
        print("📤 Testing tool call...")
        process.stdin.write(json.dumps(call_tool_request) + "\n")
        process.stdin.flush()
        
        # Read tool response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            result = response.get('result', {})
            print(f"📥 Tool result: {result.get('content', [{}])[0].get('text', 'No result')[:100]}...")
        
        print("\n✅ MCP Server test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
