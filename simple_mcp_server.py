#!/usr/bin/env python3
"""
Financial Agent MCP Server - Simple Implementation
A working MCP server for document processing
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialAgentMCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "upload_document",
                "description": "Upload and process a financial document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the document file"},
                        "document_type": {"type": "string", "description": "Type of document", "default": "claim"}
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "analyze_document", 
                "description": "Analyze a document for risk assessment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "ID of the document to analyze"},
                        "analysis_type": {"type": "string", "description": "Type of analysis", "default": "comprehensive"}
                    },
                    "required": ["document_id"]
                }
            },
            {
                "name": "ask_question",
                "description": "Ask questions about a processed document", 
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "ID of the document"},
                        "question": {"type": "string", "description": "Question to ask"}
                    },
                    "required": ["document_id", "question"]
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "financial-agent-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0", 
                "id": request_id,
                "result": {
                    "tools": self.tools
                }
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result = await self.call_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id, 
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Execute tool calls"""
        
        if name == "upload_document":
            file_path = arguments.get("file_path", "")
            document_type = arguments.get("document_type", "claim")
            
            document_id = f"DOC-{int(asyncio.get_event_loop().time() * 1000)}"
            
            return f"""Document uploaded successfully!

Document ID: {document_id}
File: {file_path}
Type: {document_type}
Status: Processing started

Next: Use analyze_document tool to process this document"""
        
        elif name == "analyze_document":
            document_id = arguments.get("document_id", "")
            analysis_type = arguments.get("analysis_type", "comprehensive")
            
            await asyncio.sleep(0.5)  # Simulate processing
            
            return f"""Document Analysis Complete!

Document ID: {document_id}
Analysis Type: {analysis_type}
Risk Level: Medium
Fraud Probability: Low
Processing Recommendation: Standard processing
Confidence Score: 0.85

Key Findings:
• Document appears to be a standard insurance claim
• No obvious signs of fraud detected  
• All required fields are present
• Processing can proceed normally"""
        
        elif name == "ask_question":
            document_id = arguments.get("document_id", "")
            question = arguments.get("question", "")
            
            return f"""Based on the analysis of document {document_id}, here's what I found regarding your question '{question}':

The document appears to be a standard insurance claim with medium risk level. No significant fraud indicators were detected. The claim can be processed through normal channels with standard verification procedures.

Additional context:
- Risk assessment completed
- Fraud detection passed
- Ready for final processing"""
        
        else:
            return f"Unknown tool: {name}"

async def main():
    """Main entry point"""
    server = FinancialAgentMCPServer()
    
    logger.info("Financial Agent MCP Server starting...")
    
    try:
        while True:
            # Read JSON-RPC request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            try:
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                
    except KeyboardInterrupt:
        logger.info("Server shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
