"""
MCP Server API Endpoints
FastAPI-based endpoints that integrate BDH architecture with Due Diligence Copilot
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Import existing Due Diligence Copilot modules
import sys
sys.path.append('..')
from document_extractor import DocumentExtractor
from document_ingestion import DocumentIngestionPipeline
from qa_workflow import DueDiligenceQA
from audit_logger import AuditLogger

# Import BDH architecture
from bdh_architecture.bdh_processor import (
    DueDiligenceBDHProcessor, 
    create_bdh_processor,
    analyze_document_with_bdh,
    enhance_qa_with_bdh
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Due Diligence Copilot MCP Server",
    description="Enhanced Due Diligence system with BDH architecture and fraud detection",
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

# Global variables for services
bdh_processor: Optional[DueDiligenceBDHProcessor] = None
document_extractor: Optional[DocumentExtractor] = None
document_pipeline: Optional[DocumentIngestionPipeline] = None
qa_workflow: Optional[DueDiligenceQA] = None
audit_logger: Optional[AuditLogger] = None

# Pydantic models
class DocumentAnalysisRequest(BaseModel):
    document_path: str
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")
    use_bdh: bool = Field(default=True, description="Use BDH architecture")
    use_landingai: bool = Field(default=True, description="Use LandingAI ADE")

class QARequest(BaseModel):
    question: str
    document_context: Optional[str] = None
    enhance_with_bdh: bool = Field(default=True, description="Enhance with BDH analysis")

class FraudDetectionRequest(BaseModel):
    document_text: str
    document_type: str = Field(default="contract", description="Type of document")
    risk_threshold: float = Field(default=0.7, description="Risk threshold")

class AnalysisResponse(BaseModel):
    document_path: str
    status: str
    bdh_analysis: Optional[Dict[str, Any]] = None
    landingai_analysis: Optional[Dict[str, Any]] = None
    combined_analysis: Dict[str, Any]
    confidence_score: float
    risk_score: float
    recommendations: List[str]
    processing_time: float

class QAResponse(BaseModel):
    question: str
    answer: str
    bdh_enhancement: Optional[Dict[str, Any]] = None
    citations: List[Dict[str, Any]]
    confidence: float
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    bdh_available: bool
    landingai_available: bool
    pathway_available: bool
    timestamp: str

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global bdh_processor, document_extractor, document_pipeline, qa_workflow, audit_logger
    
    try:
        # Initialize BDH processor
        bdh_processor = create_bdh_processor()
        logger.info("BDH processor initialized successfully")
        
        # Initialize existing Due Diligence components
        document_extractor = DocumentExtractor()
        document_pipeline = DocumentIngestionPipeline()
        qa_workflow = DueDiligenceQA(document_pipeline)
        audit_logger = AuditLogger()
        
        logger.info("Due Diligence Copilot components initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        # Continue without failing startup

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Due Diligence Copilot MCP Server")

# Dependency injection
def get_bdh_processor() -> DueDiligenceBDHProcessor:
    """Get BDH processor instance."""
    if bdh_processor is None:
        raise HTTPException(status_code=503, detail="BDH processor not available")
    return bdh_processor

def get_document_extractor() -> DocumentExtractor:
    """Get document extractor instance."""
    if document_extractor is None:
        raise HTTPException(status_code=503, detail="Document extractor not available")
    return document_extractor

def get_qa_workflow() -> DueDiligenceQA:
    """Get QA workflow instance."""
    if qa_workflow is None:
        raise HTTPException(status_code=503, detail="QA workflow not available")
    return qa_workflow

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        service="due-diligence-copilot-mcp-server",
        version="2.0.0",
        bdh_available=bdh_processor is not None,
        landingai_available=document_extractor is not None,
        pathway_available=document_pipeline is not None,
        timestamp=datetime.now().isoformat()
    )

# Document analysis endpoint
@app.post("/analyze/document", response_model=AnalysisResponse)
async def analyze_document(
    request: DocumentAnalysisRequest,
    bdh_proc: DueDiligenceBDHProcessor = Depends(get_bdh_processor),
    doc_extractor: DocumentExtractor = Depends(get_document_extractor)
):
    """Analyze a document using BDH and LandingAI."""
    try:
        start_time = datetime.now()
        
        # Check if document exists
        document_path = Path(request.document_path)
        if not document_path.exists():
            raise HTTPException(status_code=404, detail=f"Document not found: {request.document_path}")
        
        # Initialize results
        results = {
            "document_path": request.document_path,
            "status": "processing",
            "bdh_analysis": None,
            "landingai_analysis": None,
            "combined_analysis": {},
            "confidence_score": 0.0,
            "risk_score": 0.0,
            "recommendations": [],
            "processing_time": 0.0
        }
        
        # Run LandingAI analysis if requested
        if request.use_landingai and doc_extractor:
            try:
                # Extract document content
                extraction_result = doc_extractor.extract_document(str(document_path))
                
                # Generate answer for analysis
                analysis_question = "Analyze this document for risks, clauses, and potential issues"
                answer_result = doc_extractor.generate_answer(
                    question=analysis_question,
                    parsed=extraction_result
                )
                
                results["landingai_analysis"] = {
                    "extraction": extraction_result.model_dump() if hasattr(extraction_result, 'model_dump') else str(extraction_result),
                    "analysis_answer": answer_result.answer_text if hasattr(answer_result, 'answer_text') else str(answer_result),
                    "citations": answer_result.citations if hasattr(answer_result, 'citations') else []
                }
                
                logger.info("LandingAI analysis completed")
            except Exception as e:
                logger.error(f"LandingAI analysis failed: {str(e)}")
                results["landingai_analysis"] = {"error": str(e)}
        
        # Run BDH analysis if requested
        if request.use_bdh and bdh_proc:
            try:
                # Read document text for BDH analysis
                with open(document_path, 'r', encoding='utf-8') as f:
                    document_text = f.read()
                
                # Analyze with BDH
                bdh_results = analyze_document_with_bdh(
                    bdh_proc, 
                    document_text, 
                    request.analysis_type
                )
                
                results["bdh_analysis"] = bdh_results
                logger.info("BDH analysis completed")
            except Exception as e:
                logger.error(f"BDH analysis failed: {str(e)}")
                results["bdh_analysis"] = {"error": str(e)}
        
        # Combine analyses
        results["combined_analysis"] = combine_analyses(
            results["bdh_analysis"],
            results["landingai_analysis"]
        )
        
        # Calculate final scores
        results["confidence_score"] = calculate_confidence_score(results)
        results["risk_score"] = calculate_risk_score(results)
        results["recommendations"] = generate_recommendations(results)
        
        # Update status and processing time
        results["status"] = "completed"
        results["processing_time"] = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResponse(**results)
        
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Q&A endpoint
@app.post("/qa/enhanced", response_model=QAResponse)
async def enhanced_qa(
    request: QARequest,
    bdh_proc: DueDiligenceBDHProcessor = Depends(get_bdh_processor),
    qa_work: DueDiligenceQA = Depends(get_qa_workflow)
):
    """Enhanced Q&A with BDH analysis."""
    try:
        start_time = datetime.now()
        
        # Get standard answer from existing QA workflow
        standard_answer = qa_work.ask_question(request.question)
        
        # Extract answer text and citations
        answer_text = standard_answer.get("answer", "No answer found")
        citations = standard_answer.get("citations", [])
        
        # Enhance with BDH if requested
        bdh_enhancement = None
        if request.enhance_with_bdh and bdh_proc:
            try:
                # Get context from citations
                context = " ".join([cite.get("text", "") for cite in citations])
                
                # Enhance with BDH
                bdh_enhancement = enhance_qa_with_bdh(
                    bdh_proc,
                    request.question,
                    answer_text,
                    context
                )
                
                logger.info("BDH enhancement completed")
            except Exception as e:
                logger.error(f"BDH enhancement failed: {str(e)}")
                bdh_enhancement = {"error": str(e)}
        
        # Calculate confidence
        confidence = calculate_qa_confidence(answer_text, citations, bdh_enhancement)
        
        # Log query for audit
        if audit_logger:
            audit_logger.log_query(
                query=request.question,
                answer=answer_text,
                documents_accessed=[cite.get("document", "") for cite in citations],
                confidence=confidence
            )
        
        return QAResponse(
            question=request.question,
            answer=answer_text,
            bdh_enhancement=bdh_enhancement,
            citations=citations,
            confidence=confidence,
            processing_time=(datetime.now() - start_time).total_seconds()
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced QA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fraud detection endpoint
@app.post("/detect/fraud")
async def detect_fraud(
    request: FraudDetectionRequest,
    bdh_proc: DueDiligenceBDHProcessor = Depends(get_bdh_processor)
):
    """Detect fraud using BDH analysis."""
    try:
        # Analyze document with BDH
        analysis = analyze_document_with_bdh(
            bdh_proc,
            request.document_text,
            request.document_type
        )
        
        # Extract fraud indicators
        fraud_probability = analysis.get("fraud_probability", 0.0)
        risk_level = analysis.get("risk_level", "unknown")
        confidence = analysis.get("confidence", 0.0)
        
        # Determine if fraud is detected
        fraud_detected = fraud_probability > request.risk_threshold
        
        # Generate recommendations
        recommendations = []
        if fraud_detected:
            recommendations.extend([
                "High fraud risk detected - immediate review required",
                "Consider enhanced verification procedures",
                "Escalate to fraud investigation team"
            ])
        elif fraud_probability > 0.3:
            recommendations.extend([
                "Medium fraud risk - manual review recommended",
                "Request additional documentation",
                "Enhanced monitoring advised"
            ])
        else:
            recommendations.extend([
                "Low fraud risk - standard processing recommended",
                "Continue routine monitoring"
            ])
        
        return {
            "fraud_detected": fraud_detected,
            "fraud_probability": fraud_probability,
            "risk_level": risk_level,
            "confidence": confidence,
            "recommendations": recommendations,
            "analysis_details": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error detecting fraud: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Document upload endpoint
@app.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload a document for processing."""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "application/msword"]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Save uploaded file
        upload_dir = Path("data/financial_docs")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{document_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document in background
        if background_tasks:
            background_tasks.add_task(
                process_document_background,
                str(file_path)
            )
        
        return {
            "document_id": document_id,
            "status": "uploaded",
            "message": "Document uploaded successfully and processing started",
            "file_path": str(file_path)
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility functions
def combine_analyses(bdh_analysis: Optional[Dict], landingai_analysis: Optional[Dict]) -> Dict[str, Any]:
    """Combine BDH and LandingAI analyses."""
    combined = {
        "analysis_timestamp": datetime.now().isoformat(),
        "bdh_available": bdh_analysis is not None,
        "landingai_available": landingai_analysis is not None,
        "combined_risk_indicators": [],
        "combined_confidence": 0.0
    }
    
    # Extract risk indicators from both analyses
    if bdh_analysis and "risk_level" in bdh_analysis:
        combined["combined_risk_indicators"].append(f"bdh_risk_{bdh_analysis['risk_level']}")
    
    if landingai_analysis and "analysis_answer" in landingai_analysis:
        # Extract risk keywords from LandingAI analysis
        answer_text = landingai_analysis["analysis_answer"].lower()
        risk_keywords = ["risk", "liability", "indemnity", "breach", "penalty"]
        for keyword in risk_keywords:
            if keyword in answer_text:
                combined["combined_risk_indicators"].append(f"landingai_{keyword}")
    
    return combined

def calculate_confidence_score(results: Dict[str, Any]) -> float:
    """Calculate overall confidence score."""
    confidence = 0.0
    
    if results["bdh_analysis"] and "confidence" in results["bdh_analysis"]:
        confidence += results["bdh_analysis"]["confidence"] * 0.5
    
    if results["landingai_analysis"] and "analysis_answer" in results["landingai_analysis"]:
        # Simple confidence based on answer length and citations
        answer = results["landingai_analysis"]["analysis_answer"]
        citations = results["landingai_analysis"].get("citations", [])
        
        length_score = min(len(answer) / 100, 1.0)  # Normalize by length
        citation_score = min(len(citations) / 5, 1.0)  # Normalize by citations
        
        confidence += (length_score + citation_score) / 2 * 0.5
    
    return min(confidence, 1.0)

def calculate_risk_score(results: Dict[str, Any]) -> float:
    """Calculate overall risk score."""
    risk = 0.0
    
    if results["bdh_analysis"] and "fraud_probability" in results["bdh_analysis"]:
        risk += results["bdh_analysis"]["fraud_probability"] * 0.5
    
    if results["bdh_analysis"] and "risk_level" in results["bdh_analysis"]:
        risk_level = results["bdh_analysis"]["risk_level"]
        if risk_level == "high":
            risk += 0.3
        elif risk_level == "medium":
            risk += 0.15
    
    return min(risk, 1.0)

def generate_recommendations(results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on analysis results."""
    recommendations = []
    
    risk_score = results.get("risk_score", 0.0)
    
    if risk_score > 0.7:
        recommendations.extend([
            "High risk detected - immediate manual review required",
            "Consider enhanced verification procedures",
            "Monitor account for suspicious activity"
        ])
    elif risk_score > 0.4:
        recommendations.extend([
            "Medium risk detected - manual review recommended",
            "Request additional documentation",
            "Enhanced monitoring advised"
        ])
    else:
        recommendations.extend([
            "Low risk - standard processing recommended",
            "Continue routine monitoring"
        ])
    
    return recommendations

def calculate_qa_confidence(answer: str, citations: List[Dict], bdh_enhancement: Optional[Dict]) -> float:
    """Calculate confidence for Q&A response."""
    confidence = 0.0
    
    # Base confidence from answer length
    if answer and len(answer) > 10:
        confidence += 0.3
    
    # Confidence from citations
    if citations:
        confidence += min(len(citations) * 0.1, 0.4)
    
    # Confidence from BDH enhancement
    if bdh_enhancement and "confidence_score" in bdh_enhancement:
        confidence += bdh_enhancement["confidence_score"] * 0.3
    
    return min(confidence, 1.0)

async def process_document_background(file_path: str):
    """Background task for document processing."""
    try:
        logger.info(f"Processing document {file_path} in background")
        
        # Here you would implement background processing
        # For now, just log the task
        await asyncio.sleep(1)  # Simulate processing time
        
        logger.info(f"Background processing completed for document {file_path}")
        
    except Exception as e:
        logger.error(f"Error in background processing for document {file_path}: {str(e)}")

# Main execution
if __name__ == "__main__":
    # Create necessary directories
    Path("data/financial_docs").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "api_endpoints:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
