"""
Enhanced Financial Agent MCP Server
Integrates BDH (Dragon Hatchling) architecture with LandingAI ADE
for advanced financial document processing and fraud detection.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Import our custom modules
from bdh_architecture.bdh_model import BDHModel, BDHConfig, BDHProcessor
from landingai_integration.landingai_processor import (
    LandingAIIntegration, 
    FinancialDocumentSchema,
    BankStatementSchema,
    ReceiptSchema
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Financial Agent MCP Server",
    description="AI-powered financial fraud detection with BDH architecture and LandingAI ADE",
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
bdh_processor: Optional[BDHProcessor] = None
landingai_integration: Optional[LandingAIIntegration] = None

# Pydantic models
class DocumentAnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")
    document_type: str = Field(default="invoice", description="Type of financial document")
    use_bdh: bool = Field(default=True, description="Use BDH architecture for analysis")
    use_landingai: bool = Field(default=True, description="Use LandingAI ADE for parsing")

class FraudDetectionRequest(BaseModel):
    transaction_data: Dict[str, Any]
    user_context: Optional[Dict[str, Any]] = None
    analysis_depth: str = Field(default="standard", description="Depth of fraud analysis")

class AnalysisResponse(BaseModel):
    document_id: str
    status: str
    bdh_analysis: Optional[Dict[str, Any]] = None
    landingai_analysis: Optional[Dict[str, Any]] = None
    combined_analysis: Dict[str, Any]
    confidence_score: float
    risk_score: float
    recommendations: List[str]
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    bdh_available: bool
    landingai_available: bool
    timestamp: str

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global bdh_processor, landingai_integration
    
    try:
        # Initialize BDH processor
        bdh_config = BDHConfig(
            vocab_size=256,
            d_model=256,
            n_heads=4,
            n_neurons=32768,
            n_layers=6,
            dropout=0.05
        )
        bdh_processor = BDHProcessor(bdh_config)
        logger.info("BDH processor initialized successfully")
        
        # Initialize LandingAI integration
        landingai_integration = LandingAIIntegration()
        logger.info("LandingAI integration initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        # Continue without failing startup

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Enhanced Financial Agent MCP Server")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        service="enhanced-financial-agent-mcp-server",
        version="2.0.0",
        bdh_available=bdh_processor is not None,
        landingai_available=landingai_integration is not None,
        timestamp=datetime.now().isoformat()
    )

# Document upload and processing endpoint
@app.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "invoice",
    background_tasks: BackgroundTasks = None
):
    """Upload and process a financial document."""
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "text/csv",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/json",
            "image/jpeg",
            "image/png",
            "image/tiff"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / f"{document_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document in background
        if background_tasks:
            background_tasks.add_task(
                process_document_background,
                document_id,
                str(file_path),
                document_type
            )
        
        return {
            "document_id": document_id,
            "status": "uploaded",
            "message": "Document uploaded successfully and processing started",
            "file_path": str(file_path),
            "document_type": document_type
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Document analysis endpoint
@app.post("/analyze/document", response_model=AnalysisResponse)
async def analyze_document(request: DocumentAnalysisRequest):
    """Analyze a document using BDH and LandingAI."""
    try:
        start_time = datetime.now()
        
        # Check if services are available
        if not bdh_processor and not landingai_integration:
            raise HTTPException(
                status_code=503,
                detail="No analysis services available"
            )
        
        # Find document file
        upload_dir = Path("uploads")
        document_files = list(upload_dir.glob(f"{request.document_id}_*"))
        
        if not document_files:
            raise HTTPException(
                status_code=404,
                detail=f"Document {request.document_id} not found"
            )
        
        document_path = document_files[0]
        
        # Initialize results
        results = {
            "document_id": request.document_id,
            "status": "processing",
            "bdh_analysis": None,
            "landingai_analysis": None,
            "combined_analysis": {},
            "confidence_score": 0.0,
            "risk_score": 0.0,
            "recommendations": [],
            "processing_time": 0.0
        }
        
        # Run BDH analysis if requested and available
        if request.use_bdh and bdh_processor:
            try:
                # For BDH, we need text content
                # In a real implementation, you'd extract text from the document
                sample_text = f"Financial document analysis for {request.document_type}"
                bdh_results = bdh_processor.analyze_financial_document(sample_text)
                results["bdh_analysis"] = bdh_results
                logger.info("BDH analysis completed")
            except Exception as e:
                logger.error(f"BDH analysis failed: {str(e)}")
                results["bdh_analysis"] = {"error": str(e)}
        
        # Run LandingAI analysis if requested and available
        if request.use_landingai and landingai_integration:
            try:
                landingai_results = await landingai_integration.process_document_pipeline(
                    document_path, request.document_type
                )
                results["landingai_analysis"] = landingai_results
                logger.info("LandingAI analysis completed")
            except Exception as e:
                logger.error(f"LandingAI analysis failed: {str(e)}")
                results["landingai_analysis"] = {"error": str(e)}
        
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

# Fraud detection endpoint
@app.post("/detect/fraud")
async def detect_fraud(request: FraudDetectionRequest):
    """Run fraud detection on transaction data."""
    try:
        # Use LandingAI for fraud detection if available
        if landingai_integration:
            # Create a mock parse response for fraud analysis
            class MockParseResponse:
                def __init__(self, text):
                    self.markdown = text
                    self.chunks = []
                    self.grounding = {}
            
            # Convert transaction data to text
            transaction_text = json.dumps(request.transaction_data, indent=2)
            mock_response = MockParseResponse(transaction_text)
            
            # Analyze for fraud
            fraud_analysis = await landingai_integration.analyze_document_for_fraud(mock_response)
            
            return {
                "transaction_id": request.transaction_data.get("id", "unknown"),
                "risk_score": fraud_analysis.get("risk_score", 0.0),
                "fraud_indicators": fraud_analysis.get("fraud_indicators", []),
                "recommendations": fraud_analysis.get("recommendations", []),
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "landingai_ade"
            }
        else:
            # Fallback to basic analysis
            return {
                "transaction_id": request.transaction_data.get("id", "unknown"),
                "risk_score": 0.5,
                "fraud_indicators": ["service_unavailable"],
                "recommendations": ["Manual review recommended"],
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "fallback"
            }
        
    except Exception as e:
        logger.error(f"Error detecting fraud: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get analysis results endpoint
@app.get("/analysis/{document_id}")
async def get_analysis_results(document_id: str):
    """Get analysis results for a specific document."""
    try:
        # In a real implementation, you'd store results in a database
        # For now, return a placeholder
        return {
            "document_id": document_id,
            "status": "not_found",
            "message": "Analysis results not found. Please run analysis first."
        }
        
    except Exception as e:
        logger.error(f"Error retrieving analysis results: {str(e)}")
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
    if bdh_analysis and "risk_indicators" in bdh_analysis:
        combined["combined_risk_indicators"].extend(bdh_analysis["risk_indicators"])
    
    if landingai_analysis and "fraud_analysis" in landingai_analysis:
        fraud_analysis = landingai_analysis["fraud_analysis"]
        if "fraud_indicators" in fraud_analysis:
            combined["combined_risk_indicators"].extend(fraud_analysis["fraud_indicators"])
    
    # Remove duplicates
    combined["combined_risk_indicators"] = list(set(combined["combined_risk_indicators"]))
    
    return combined

def calculate_confidence_score(results: Dict[str, Any]) -> float:
    """Calculate overall confidence score."""
    confidence = 0.0
    
    if results["bdh_analysis"] and "confidence_score" in results["bdh_analysis"]:
        confidence += results["bdh_analysis"]["confidence_score"] * 0.5
    
    if results["landingai_analysis"] and "fraud_analysis" in results["landingai_analysis"]:
        fraud_analysis = results["landingai_analysis"]["fraud_analysis"]
        if "risk_score" in fraud_analysis:
            # Convert risk score to confidence (inverse relationship)
            confidence += (1.0 - fraud_analysis["risk_score"]) * 0.5
    
    return min(confidence, 1.0)

def calculate_risk_score(results: Dict[str, Any]) -> float:
    """Calculate overall risk score."""
    risk = 0.0
    
    if results["bdh_analysis"] and "risk_indicators" in results["bdh_analysis"]:
        risk += len(results["bdh_analysis"]["risk_indicators"]) * 0.1
    
    if results["landingai_analysis"] and "fraud_analysis" in results["landingai_analysis"]:
        fraud_analysis = results["landingai_analysis"]["fraud_analysis"]
        if "risk_score" in fraud_analysis:
            risk += fraud_analysis["risk_score"] * 0.5
    
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

async def process_document_background(document_id: str, file_path: str, document_type: str):
    """Background task for document processing."""
    try:
        logger.info(f"Processing document {document_id} in background")
        
        # Here you would implement background processing
        # For now, just log the task
        await asyncio.sleep(1)  # Simulate processing time
        
        logger.info(f"Background processing completed for document {document_id}")
        
    except Exception as e:
        logger.error(f"Error in background processing for document {document_id}: {str(e)}")

# Main execution
if __name__ == "__main__":
    # Create uploads directory
    Path("uploads").mkdir(exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
