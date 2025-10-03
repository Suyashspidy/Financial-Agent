"""
Claims Triage API Server
FastAPI server for the Claims Triage Agent frontend
"""

import asyncio
import logging
import os
import uuid
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

# Initialize FastAPI app
app = FastAPI(
    title="Claims Triage API",
    description="API server for Claims Triage Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URL
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
    flags: List[str] = Field(description="Risk flags")
    upload_date: str = Field(description="Upload date")
    status: str = Field(description="Processing status")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    processing_time: float = Field(description="Processing time in seconds")

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str

# Mock data storage
claims_db: Dict[str, Dict] = {}

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="claims-triage-api",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

# Document upload endpoint
@app.post("/upload/claim")
async def upload_claim(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload a claims document for analysis."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported"
            )
        
        # Generate claim ID
        claim_id = f"CL-{int(datetime.now().timestamp() * 1000)}"
        
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{claim_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Store claim info
        claims_db[claim_id] = {
            "id": claim_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "upload_date": datetime.now().isoformat(),
            "status": "uploaded",
            "processed": False
        }
        
        # Process document in background
        if background_tasks:
            background_tasks.add_task(
                process_claim_background,
                claim_id
            )
        
        return {
            "claim_id": claim_id,
            "status": "uploaded",
            "message": "Claim uploaded successfully and processing started",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading claim: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analyze claim endpoint
@app.post("/analyze/claim", response_model=ClaimAnalysisResponse)
async def analyze_claim(request: ClaimAnalysisRequest):
    """Analyze a claims document."""
    try:
        start_time = datetime.now()
        
        # Check if claim exists
        if request.document_id not in claims_db:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        claim_info = claims_db[request.document_id]
        
        # Simulate AI analysis
        analysis_result = await simulate_ai_analysis(claim_info)
        
        # Update claim info
        claims_db[request.document_id].update({
            "processed": True,
            "analysis": analysis_result
        })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ClaimAnalysisResponse(
            claim_id=request.document_id,
            severity=analysis_result["severity"],
            complexity=analysis_result["complexity"],
            suggested_team=analysis_result["suggested_team"],
            flags=analysis_result["flags"],
            upload_date=claim_info["upload_date"],
            status="completed",
            confidence=analysis_result["confidence"],
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error analyzing claim: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get all claims endpoint
@app.get("/claims")
async def get_all_claims():
    """Get all processed claims."""
    try:
        processed_claims = []
        
        for claim_id, claim_info in claims_db.items():
            if claim_info.get("processed", False) and "analysis" in claim_info:
                analysis = claim_info["analysis"]
                processed_claims.append({
                    "id": claim_id,
                    "severity": analysis["severity"],
                    "complexity": analysis["complexity"],
                    "suggested_team": analysis["suggested_team"],
                    "flags": analysis["flags"],
                    "upload_date": claim_info["upload_date"],
                    "status": "completed"
                })
        
        return {
            "claims": processed_claims,
            "total": len(processed_claims)
        }
        
    except Exception as e:
        logger.error(f"Error getting claims: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get specific claim endpoint
@app.get("/claims/{claim_id}")
async def get_claim(claim_id: str):
    """Get a specific claim by ID."""
    try:
        if claim_id not in claims_db:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        claim_info = claims_db[claim_id]
        
        if not claim_info.get("processed", False):
            return {
                "id": claim_id,
                "status": "processing",
                "upload_date": claim_info["upload_date"],
                "filename": claim_info["filename"]
            }
        
        analysis = claim_info["analysis"]
        return {
            "id": claim_id,
            "severity": analysis["severity"],
            "complexity": analysis["complexity"],
            "suggested_team": analysis["suggested_team"],
            "flags": analysis["flags"],
            "upload_date": claim_info["upload_date"],
            "status": "completed",
            "confidence": analysis["confidence"]
        }
        
    except Exception as e:
        logger.error(f"Error getting claim: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Reassign claim endpoint
@app.post("/claims/{claim_id}/reassign")
async def reassign_claim(claim_id: str, request_data: dict):
    """Reassign a claim to a different team."""
    try:
        if claim_id not in claims_db:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        if not claims_db[claim_id].get("processed", False):
            raise HTTPException(status_code=400, detail="Claim not yet processed")
        
        new_team = request_data.get("new_team")
        if not new_team:
            raise HTTPException(status_code=400, detail="new_team is required")
        
        # Update suggested team
        claims_db[claim_id]["analysis"]["suggested_team"] = new_team
        
        return {
            "claim_id": claim_id,
            "new_team": new_team,
            "status": "reassigned",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error reassigning claim: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility functions
async def simulate_ai_analysis(claim_info: Dict) -> Dict[str, Any]:
    """Simulate AI analysis of a claims document."""
    # Simulate processing time
    await asyncio.sleep(2)
    
    # Generate mock analysis results
    import random
    
    # Severity score (1-10)
    severity = random.randint(1, 10)
    
    # Complexity level
    complexity_levels = ["Low", "Medium", "High"]
    complexity = random.choice(complexity_levels)
    
    # Suggested team based on severity and complexity
    if severity >= 8:
        suggested_team = "Major Incidents Unit"
    elif severity >= 5:
        suggested_team = "Fraud Investigation"
    elif complexity == "High":
        suggested_team = "Legal Review"
    else:
        suggested_team = "General Claims"
    
    # Risk flags
    all_flags = [
        "Litigation Risk",
        "Fraudulent Activity Suspected", 
        "High Value",
        "Urgent Review",
        "Policy Violation",
        "Coverage Dispute"
    ]
    
    # Generate 1-3 random flags
    num_flags = random.randint(1, 3)
    flags = random.sample(all_flags, num_flags)
    
    # Confidence score
    confidence = random.uniform(0.7, 0.95)
    
    return {
        "severity": severity,
        "complexity": complexity,
        "suggested_team": suggested_team,
        "flags": flags,
        "confidence": confidence
    }

async def process_claim_background(claim_id: str):
    """Background task for processing claims."""
    try:
        logger.info(f"Processing claim {claim_id} in background")
        
        # Simulate processing time
        await asyncio.sleep(3)
        
        # Auto-analyze the claim
        if claim_id in claims_db:
            claim_info = claims_db[claim_id]
            analysis_result = await simulate_ai_analysis(claim_info)
            
            claims_db[claim_id].update({
                "processed": True,
                "analysis": analysis_result
            })
            
            logger.info(f"Background processing completed for claim {claim_id}")
        
    except Exception as e:
        logger.error(f"Error in background processing for claim {claim_id}: {str(e)}")

# Main execution
if __name__ == "__main__":
    # Create necessary directories
    Path("uploads").mkdir(parents=True, exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "claims_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
