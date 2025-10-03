"""
Enhanced Claims Triage API Server
Integrates with LandingAI MCP Server for real document processing
"""

import asyncio
import logging
import os
import uuid
import requests
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
LANDINGAI_MCP_SERVER_URL = "http://localhost:8001"  # Our LandingAI MCP server
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Claims Triage API",
    description="API server for Claims Triage Agent with LandingAI integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ClaimAnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")

class ClaimAnalysisResponse(BaseModel):
    claim_id: str
    severity: int = Field(ge=1, le=10, description="Severity score 1-10")
    complexity: str = Field(description="Complexity level")
    suggested_team: str = Field(description="Suggested team assignment")
    flags: List[str] = Field(description="Risk flags and indicators")
    confidence: float = Field(ge=0.0, le=1.0, description="Analysis confidence")
    risk_score: float = Field(ge=0.0, le=1.0, description="Overall risk score")
    recommendations: List[str] = Field(description="Recommended actions")
    extracted_data: Optional[List[Dict[str, Any]]] = Field(description="Extracted document data")
    citations: Optional[List[Dict[str, Any]]] = Field(description="Source citations")

class ClaimResponse(BaseModel):
    id: str
    severity: int
    complexity: str
    suggested_team: str
    flags: List[str]
    upload_date: datetime
    status: str
    confidence: Optional[float] = None
    risk_score: Optional[float] = None

class ClaimsListResponse(BaseModel):
    claims: List[ClaimResponse]
    total: int

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime
    landingai_available: bool

class ReassignRequest(BaseModel):
    new_team: str

# In-memory database for claims
claims_db: Dict[str, Dict[str, Any]] = {}

def check_landingai_server():
    """Check if LandingAI MCP server is available"""
    try:
        response = requests.get(f"{LANDINGAI_MCP_SERVER_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    landingai_available = check_landingai_server()
    return HealthResponse(
        status="healthy",
        service="enhanced-claims-triage-api",
        version="2.0.0",
        timestamp=datetime.now(),
        landingai_available=landingai_available
    )

@app.post("/upload/claim")
async def upload_claim(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Upload a claim document for processing"""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    claim_id = f"CL-{int(datetime.now().timestamp() * 1000)}"
    
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{claim_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        # Store claim metadata
        claims_db[claim_id] = {
            "id": claim_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "content_type": file.content_type,
            "upload_date": datetime.now(),
            "status": "uploaded",
            "processed": False,
            "analysis": None
        }

        # Process with LandingAI in background
        if background_tasks:
            background_tasks.add_task(process_claim_with_landingai, claim_id, str(file_path))

        return {
            "claim_id": claim_id,
            "status": "uploaded",
            "message": "Claim uploaded successfully and processing started",
            "filename": file.filename,
            "landingai_processing": True
        }
    except Exception as e:
        logger.error(f"Error uploading claim: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_claim_with_landingai(claim_id: str, file_path: str):
    """Process claim using LandingAI MCP server"""
    try:
        logger.info(f"Processing claim {claim_id} with LandingAI...")
        
        # Check if LandingAI server is available
        if not check_landingai_server():
            logger.warning("LandingAI server not available, using fallback analysis")
            await fallback_claim_analysis(claim_id, file_path)
            return
        
        # Send file to LandingAI MCP server for analysis
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "application/pdf")}
            response = requests.post(f"{LANDINGAI_MCP_SERVER_URL}/upload_and_process", files=files)
            
        if response.status_code != 200:
            logger.error(f"LandingAI processing failed: {response.status_code}")
            await fallback_claim_analysis(claim_id, file_path)
            return
        
        # Wait a moment for processing
        await asyncio.sleep(3)
        
        # Get analysis results
        analysis_response = requests.post(f"{LANDINGAI_MCP_SERVER_URL}/analyze_claim", 
                                        json={"document_path": file_path, "analysis_type": "comprehensive"})
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()
            analysis_result = analysis_data["data"]
            
            # Update claim with real analysis
            claims_db[claim_id]["analysis"] = {
                "severity": analysis_result["severity"],
                "complexity": analysis_result["complexity"],
                "suggested_team": analysis_result["suggested_team"],
                "flags": analysis_result["flags"],
                "confidence": analysis_result["confidence"],
                "risk_score": analysis_result["risk_score"],
                "recommendations": analysis_result["recommendations"],
                "extracted_data": analysis_result.get("extracted_data", []),
                "citations": analysis_result.get("citations", [])
            }
            
            logger.info(f"LandingAI analysis completed for claim {claim_id}")
        else:
            logger.error(f"Failed to get analysis results: {analysis_response.status_code}")
            await fallback_claim_analysis(claim_id, file_path)
            
    except Exception as e:
        logger.error(f"Error processing claim {claim_id} with LandingAI: {e}")
        await fallback_claim_analysis(claim_id, file_path)
    
    finally:
        claims_db[claim_id]["status"] = "completed"
        claims_db[claim_id]["processed"] = True

async def fallback_claim_analysis(claim_id: str, file_path: str):
    """Fallback analysis when LandingAI is not available"""
    logger.info(f"Using fallback analysis for claim {claim_id}")
    
    # Simple file-based analysis
    file_size = os.path.getsize(file_path)
    
    # Mock analysis based on file characteristics
    analysis_result = {
        "severity": min(8, (file_size // 10000) + 1),
        "complexity": "High" if file_size > 100000 else "Medium" if file_size > 50000 else "Low",
        "suggested_team": "General Claims",
        "flags": ["Standard Processing"],
        "confidence": 0.7,
        "risk_score": 0.3,
        "recommendations": ["Review document", "Contact claimant if needed"]
    }
    
    claims_db[claim_id]["analysis"] = analysis_result

@app.get("/claims", response_model=ClaimsListResponse)
async def get_claims():
    """Get all processed claims"""
    processed_claims = []
    for claim_id, claim_data in claims_db.items():
        if claim_data.get("processed") and claim_data["analysis"]:
            processed_claims.append(ClaimResponse(
                id=claim_id,
                severity=claim_data["analysis"]["severity"],
                complexity=claim_data["analysis"]["complexity"],
                suggested_team=claim_data["analysis"]["suggested_team"],
                flags=claim_data["analysis"]["flags"],
                upload_date=claim_data["upload_date"],
                status=claim_data["status"],
                confidence=claim_data["analysis"].get("confidence"),
                risk_score=claim_data["analysis"].get("risk_score")
            ))
    return ClaimsListResponse(claims=processed_claims, total=len(processed_claims))

@app.get("/claims/{claim_id}", response_model=ClaimResponse)
async def get_claim_details(claim_id: str):
    """Get details of a specific claim"""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim_data = claims_db[claim_id]
    if not claim_data.get("processed") or not claim_data["analysis"]:
        raise HTTPException(status_code=404, detail="Claim not yet processed")
    
    return ClaimResponse(
        id=claim_id,
        severity=claim_data["analysis"]["severity"],
        complexity=claim_data["analysis"]["complexity"],
        suggested_team=claim_data["analysis"]["suggested_team"],
        flags=claim_data["analysis"]["flags"],
        upload_date=claim_data["upload_date"],
        status=claim_data["status"],
        confidence=claim_data["analysis"].get("confidence"),
        risk_score=claim_data["analysis"].get("risk_score")
    )

@app.post("/claims/{claim_id}/reassign")
async def reassign_claim(claim_id: str, request: ReassignRequest):
    """Reassign a claim to a different team"""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if not claims_db[claim_id].get("processed", False):
        raise HTTPException(status_code=400, detail="Claim not yet processed")
    
    new_team = request.new_team
    if not new_team:
        raise HTTPException(status_code=400, detail="new_team is required")
    
    claims_db[claim_id]["analysis"]["suggested_team"] = new_team
    
    return {
        "claim_id": claim_id,
        "new_team": new_team,
        "status": "reassigned",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/claims/{claim_id}/analysis")
async def get_claim_analysis(claim_id: str):
    """Get detailed analysis for a claim"""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim_data = claims_db[claim_id]
    if not claim_data.get("processed") or not claim_data["analysis"]:
        raise HTTPException(status_code=404, detail="Claim not yet processed")
    
    return {
        "claim_id": claim_id,
        "analysis": claim_data["analysis"],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/claims/{claim_id}/ask_question")
async def ask_question_about_claim(claim_id: str, question_data: Dict[str, str]):
    """Ask a question about a specific claim document"""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim_data = claims_db[claim_id]
    if not claim_data.get("processed"):
        raise HTTPException(status_code=400, detail="Claim not yet processed")
    
    question = question_data.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    try:
        # Send question to LandingAI MCP server
        response = requests.post(f"{LANDINGAI_MCP_SERVER_URL}/answer_question", 
                               json={
                                   "document_path": claim_data["file_path"],
                                   "question": question,
                                   "top_k": 5
                               })
        
        if response.status_code == 200:
            answer_data = response.json()
            return {
                "claim_id": claim_id,
                "question": question,
                "answer": answer_data["data"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to get answer from LandingAI")
            
    except Exception as e:
        logger.error(f"Error asking question about claim {claim_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

@app.get("/landingai/status")
async def get_landingai_status():
    """Check LandingAI MCP server status"""
    try:
        response = requests.get(f"{LANDINGAI_MCP_SERVER_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                "available": True,
                "status": data["status"],
                "extractor_available": data.get("extractor_available", False),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "available": False,
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run("enhanced_claims_api:app", host="0.0.0.0", port=8000, reload=True)
