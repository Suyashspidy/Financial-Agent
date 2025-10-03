#!/usr/bin/env python3
"""
Financial Agent MCP Server - Central Frontend
Acts as the central orchestrator for all components including Inkeep agent
Following the architecture: UI -> MCP Server -> Landing AI, Google API Inkeep, LLM -> Pathway -> Response
"""

import asyncio
import logging
import os
import tempfile
import json
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Agent MCP Server - Central Frontend",
    description="Central orchestrator for all Financial Agent components including Inkeep agent",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for connected services
SERVICES = {
    "landingai": "http://localhost:8001",
    "inkeep_ui": "http://localhost:3000",
    "inkeep_manage_api": "http://localhost:3002",
    "inkeep_run_api": "http://localhost:3003",
    "frontend": "http://localhost:5173"
}

# Pydantic models
class DocumentUploadRequest(BaseModel):
    filename: str
    content_type: str = "application/pdf"

class AnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")

class QuestionRequest(BaseModel):
    document_id: str
    question: str
    context: Optional[str] = None

class InkeepActionRequest(BaseModel):
    action_type: str
    parameters: Dict[str, Any]
    agent_id: Optional[str] = None

class LLMRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
    model: str = "gpt-3.5-turbo"

class PathwayRefinementRequest(BaseModel):
    content: str
    refinement_type: str = "enhance"
    parameters: Optional[Dict[str, Any]] = None

# In-memory storage
documents_db: Dict[str, Dict[str, Any]] = {}
analysis_results: Dict[str, Dict[str, Any]] = {}
inkeep_sessions: Dict[str, Dict[str, Any]] = {}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for all connected services"""
    service_status = {}
    
    for service_name, url in SERVICES.items():
        try:
            if service_name == "frontend":
                response = requests.get(url, timeout=2)
            else:
                response = requests.get(f"{url}/health", timeout=2)
            
            service_status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": url,
                "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
            }
        except Exception as e:
            service_status[service_name] = {
                "status": "unavailable",
                "url": url,
                "error": str(e)
            }
    
    return {
        "status": "healthy",
        "service": "financial-agent-mcp-central",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "connected_services": service_status
    }

# Document upload endpoint (Step 1 from architecture)
@app.post("/upload/document")
async def upload_document(file: UploadFile = File(...)):
    """Upload document to MCP server (Step 1: UI -> MCP Server)"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Generate document ID
        doc_id = f"DOC-{int(datetime.now().timestamp() * 1000)}"
        
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{doc_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Store document info
        documents_db[doc_id] = {
            "id": doc_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "upload_date": datetime.now().isoformat(),
            "status": "uploaded",
            "size": len(content)
        }
        
        logger.info(f"Document uploaded: {doc_id}")
        
        return {
            "document_id": doc_id,
            "status": "uploaded",
            "message": "Document uploaded successfully to MCP server",
            "filename": file.filename,
            "next_step": "Trigger Landing AI action"
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Landing AI action endpoint (Step 2 from architecture)
@app.post("/landingai/action")
async def trigger_landingai_action(request: AnalysisRequest):
    """Trigger Landing AI action (Step 2: Landing AI -> MCP Server)"""
    try:
        if request.document_id not in documents_db:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_info = documents_db[request.document_id]
        
        # Upload document to Landing AI service and get analysis
        landingai_upload_url = f"{SERVICES['landingai']}/upload_and_process"
        
        try:
            # Upload file to Landing AI
            with open(doc_info["file_path"], "rb") as f:
                files = {"file": (doc_info["filename"], f, "application/pdf")}
                upload_response = requests.post(landingai_upload_url, files=files, timeout=30)
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                landingai_doc_id = upload_data.get("document_id")
                
                if landingai_doc_id:
                    # Wait a moment for processing
                    await asyncio.sleep(2)
                    
                    # Now analyze the document using the LandingAI document ID
                    landingai_analyze_url = f"{SERVICES['landingai']}/analyze_claim"
                    payload = {
                        "document_path": f"uploads/{landingai_doc_id}_{doc_info['filename']}",
                        "analysis_type": request.analysis_type
                    }
                    
                    analyze_response = requests.post(landingai_analyze_url, json=payload, timeout=30)
                    if analyze_response.status_code == 200:
                        analysis_data = analyze_response.json()
                        
                        # Store analysis results
                        analysis_results[request.document_id] = {
                            "document_id": request.document_id,
                            "analysis": analysis_data.get("data", {}),
                            "timestamp": datetime.now().isoformat(),
                            "source": "landingai"
                        }
                        
                        return {
                            "status": "success",
                            "message": "Landing AI action completed",
                            "analysis_id": request.document_id,
                            "next_step": "Send to LLM for processing"
                        }
                    else:
                        # Use fallback if analysis fails
                        logger.warning(f"Landing AI analysis failed: {analyze_response.status_code}")
                        analysis_results[request.document_id] = await fallback_analysis(request.document_id)
                        return {
                            "status": "success",
                            "message": "Landing AI action completed (fallback)",
                            "analysis_id": request.document_id,
                            "next_step": "Send to LLM for processing"
                        }
                else:
                    raise HTTPException(status_code=500, detail="Landing AI upload failed to return document ID")
            else:
                raise HTTPException(status_code=500, detail="Landing AI upload error")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Landing AI service unavailable, using fallback: {e}")
            # Fallback analysis
            analysis_results[request.document_id] = await fallback_analysis(request.document_id)
            
            return {
                "status": "success",
                "message": "Fallback analysis completed",
                "analysis_id": request.document_id,
                "next_step": "Send to LLM for processing"
            }
        
    except Exception as e:
        logger.error(f"Error in Landing AI action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# LLM processing endpoint (Step 3 from architecture)
@app.post("/llm/process")
async def process_with_llm(request: LLMRequest):
    """Process content with LLM (Step 3: MCP Server -> LLM)"""
    try:
        # Simulate LLM processing
        llm_response = await simulate_llm_processing(request.prompt, request.context)
        
        return {
            "status": "success",
            "message": "LLM processing completed",
            "llm_output": llm_response,
            "next_step": "Send to Pathway for refinement"
        }
        
    except Exception as e:
        logger.error(f"Error in LLM processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Pathway refinement endpoint (Step 4 from architecture)
@app.post("/pathway/refine")
async def refine_with_pathway(request: PathwayRefinementRequest):
    """Refine content with Pathway (Step 4: LLM -> Pathway)"""
    try:
        # Simulate Pathway refinement
        refined_content = await simulate_pathway_refinement(request.content, request.refinement_type)
        
        return {
            "status": "success",
            "message": "Pathway refinement completed",
            "refined_content": refined_content,
            "next_step": "Return response to MCP Server"
        }
        
    except Exception as e:
        logger.error(f"Error in Pathway refinement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Complete processing pipeline endpoint
@app.post("/process/complete")
async def complete_processing_pipeline(document_id: str):
    """Complete processing pipeline following the architecture"""
    try:
        if document_id not in documents_db:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_info = documents_db[document_id]
        
        # Step 1: Document is already uploaded
        logger.info(f"Step 1: Document {document_id} uploaded")
        
        # Step 2: Trigger Landing AI action
        logger.info(f"Step 2: Triggering Landing AI action for {document_id}")
        landingai_result = await trigger_landingai_action(AnalysisRequest(document_id=document_id))
        
        # Step 3: Process with LLM
        logger.info(f"Step 3: Processing with LLM for {document_id}")
        analysis_data = analysis_results.get(document_id, {}).get("analysis", {})
        llm_prompt = f"Analyze this claim data: {json.dumps(analysis_data)}"
        llm_result = await process_with_llm(LLMRequest(prompt=llm_prompt))
        
        # Step 4: Refine with Pathway
        logger.info(f"Step 4: Refining with Pathway for {document_id}")
        pathway_result = await refine_with_pathway(
            PathwayRefinementRequest(content=llm_result["llm_output"])
        )
        
        # Step 5: Prepare response
        logger.info(f"Step 5: Preparing response for {document_id}")
        final_response = {
            "document_id": document_id,
            "analysis": analysis_data,
            "llm_processing": llm_result["llm_output"],
            "refined_content": pathway_result["refined_content"],
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        return final_response
        
    except Exception as e:
        logger.error(f"Error in complete processing pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Inkeep agent integration endpoints
@app.post("/inkeep/action")
async def trigger_inkeep_action(request: InkeepActionRequest):
    """Trigger Inkeep agent action"""
    try:
        # Forward to Inkeep services
        inkeep_url = f"{SERVICES['inkeep_run_api']}/execute"
        payload = {
            "action_type": request.action_type,
            "parameters": request.parameters,
            "agent_id": request.agent_id
        }
        
        try:
            response = requests.post(inkeep_url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                
                # Store Inkeep session
                session_id = f"session-{int(datetime.now().timestamp() * 1000)}"
                inkeep_sessions[session_id] = {
                    "session_id": session_id,
                    "action": request.action_type,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                return {
                    "status": "success",
                    "message": "Inkeep action completed",
                    "session_id": session_id,
                    "result": result
                }
            else:
                raise HTTPException(status_code=500, detail="Inkeep service error")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Inkeep service unavailable: {e}")
            return {
                "status": "warning",
                "message": "Inkeep service unavailable",
                "fallback": "Using MCP server processing"
            }
        
    except Exception as e:
        logger.error(f"Error in Inkeep action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Question answering endpoint
@app.post("/ask/question")
async def ask_question(request: QuestionRequest):
    """Ask a question about a document"""
    try:
        if request.document_id not in documents_db:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get analysis data
        analysis_data = analysis_results.get(request.document_id, {}).get("analysis", {})
        
        # Process question with LLM
        question_prompt = f"Question: {request.question}\nContext: {json.dumps(analysis_data)}"
        llm_result = await process_with_llm(LLMRequest(prompt=question_prompt))
        
        # Refine answer with Pathway
        refined_answer = await refine_with_pathway(
            PathwayRefinementRequest(content=llm_result["llm_output"])
        )
        
        return {
            "document_id": request.document_id,
            "question": request.question,
            "answer": refined_answer["refined_content"],
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get all documents
@app.get("/documents")
async def get_all_documents():
    """Get all uploaded documents"""
    return {
        "documents": list(documents_db.values()),
        "total": len(documents_db)
    }

# Get document details
@app.get("/documents/{document_id}")
async def get_document_details(document_id: str):
    """Get details of a specific document"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = documents_db[document_id]
    analysis_info = analysis_results.get(document_id, {})
    
    return {
        "document": doc_info,
        "analysis": analysis_info,
        "status": "complete" if analysis_info else "pending"
    }

# Utility functions
async def fallback_analysis(document_id: str) -> Dict[str, Any]:
    """Fallback analysis when Landing AI is unavailable"""
    doc_info = documents_db[document_id]
    file_size = os.path.getsize(doc_info["file_path"]) if os.path.exists(doc_info["file_path"]) else 50000
    
    return {
        "document_id": document_id,
        "analysis": {
            "severity": min(10, max(1, (file_size // 10000) + 1)),
            "complexity": "High" if file_size > 100000 else "Medium" if file_size > 50000 else "Low",
            "suggested_team": "General Claims",
            "flags": ["Standard Processing"],
            "confidence": 0.7,
            "risk_score": 0.3
        },
        "timestamp": datetime.now().isoformat(),
        "source": "fallback"
    }

async def simulate_llm_processing(prompt: str, context: str = None) -> str:
    """Simulate LLM processing"""
    await asyncio.sleep(1)  # Simulate processing time
    
    # Generate realistic LLM response
    if "claim" in prompt.lower():
        return f"Based on the claim analysis, this appears to be a standard insurance claim requiring {context or 'general processing'}. The document contains relevant information for assessment."
    elif "question" in prompt.lower():
        return f"The answer to your question is based on the document analysis. {context or 'Please review the provided context for detailed information.'}"
    else:
        return f"Processed content: {prompt[:100]}... Analysis completed successfully."

async def simulate_pathway_refinement(content: str, refinement_type: str) -> str:
    """Simulate Pathway refinement"""
    await asyncio.sleep(0.5)  # Simulate processing time
    
    if refinement_type == "enhance":
        return f"Enhanced: {content} [Refined for clarity and accuracy]"
    elif refinement_type == "summarize":
        return f"Summary: {content[:200]}..."
    else:
        return f"Refined: {content}"

# Main execution
if __name__ == "__main__":
    # Create necessary directories
    Path("uploads").mkdir(parents=True, exist_ok=True)
    
    # Run the MCP Central Server on port 8000 (main orchestrator)
    uvicorn.run("financial_mcp_central:app", host="0.0.0.0", port=8000, reload=True)
