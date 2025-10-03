#!/usr/bin/env python3
"""
Financial Agent MCP Server
Main entry point for the MCP server providing financial fraud detection services.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from document_ingestion.ingestion_service import DocumentIngestionService
from document_conversion.conversion_service import DocumentConversionService
from ai_services.ai_processor import AIProcessor
from fraud_detection.fraud_analyzer import FraudAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Agent MCP Server",
    description="AI-powered financial fraud detection and document processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ingestion_service = DocumentIngestionService()
conversion_service = DocumentConversionService()
ai_processor = AIProcessor()
fraud_analyzer = FraudAnalyzer()

# Pydantic models
class DocumentAnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str = "comprehensive"

class FraudDetectionRequest(BaseModel):
    transaction_data: Dict[str, Any]
    user_context: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    document_id: str
    status: str
    results: Dict[str, Any]
    confidence_score: float
    recommendations: List[str]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "financial-agent-mcp-server"}

# Document ingestion endpoint
@app.post("/ingest/document")
async def ingest_document(file: UploadFile = File(...)):
    """Upload and process a financial document."""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/csv", "application/vnd.ms-excel", 
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
        
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Process document
        document_id = await ingestion_service.process_document(file)
        
        return {
            "document_id": document_id,
            "status": "success",
            "message": "Document processed successfully"
        }
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Document analysis endpoint
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(request: DocumentAnalysisRequest):
    """Analyze a processed document for fraud indicators."""
    try:
        # Get document data
        document_data = await ingestion_service.get_document(request.document_id)
        
        if not document_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Convert document if needed
        processed_data = await conversion_service.convert_document(document_data)
        
        # Run AI analysis
        analysis_results = await ai_processor.analyze_document(processed_data)
        
        # Generate fraud detection score
        fraud_score = await fraud_analyzer.calculate_fraud_score(analysis_results)
        
        # Generate recommendations
        recommendations = await fraud_analyzer.generate_recommendations(analysis_results, fraud_score)
        
        return AnalysisResponse(
            document_id=request.document_id,
            status="completed",
            results=analysis_results,
            confidence_score=fraud_score,
            recommendations=recommendations
        )
    
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fraud detection endpoint
@app.post("/detect/fraud")
async def detect_fraud(request: FraudDetectionRequest):
    """Run fraud detection on transaction data."""
    try:
        # Process transaction data
        fraud_indicators = await fraud_analyzer.analyze_transaction(request.transaction_data)
        
        # Calculate risk score
        risk_score = await fraud_analyzer.calculate_risk_score(fraud_indicators, request.user_context)
        
        # Generate alerts if needed
        alerts = await fraud_analyzer.generate_alerts(fraud_indicators, risk_score)
        
        return {
            "transaction_id": request.transaction_data.get("id", "unknown"),
            "risk_score": risk_score,
            "fraud_indicators": fraud_indicators,
            "alerts": alerts,
            "recommendation": "approve" if risk_score < 0.3 else "review" if risk_score < 0.7 else "decline"
        }
    
    except Exception as e:
        logger.error(f"Error detecting fraud: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get analysis results endpoint
@app.get("/analyze/{document_id}")
async def get_analysis_results(document_id: str):
    """Get analysis results for a specific document."""
    try:
        results = await ai_processor.get_analysis_results(document_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        return results
    
    except Exception as e:
        logger.error(f"Error retrieving analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
