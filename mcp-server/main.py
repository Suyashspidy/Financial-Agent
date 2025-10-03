"""
Due Diligence Copilot MCP Server
Enhanced with BDH Architecture and Advanced Fraud Detection

This MCP server integrates the existing Due Diligence Copilot system with:
- BDH (Dragon Hatchling) architecture for enhanced neural processing
- Advanced fraud detection capabilities
- FastAPI-based REST endpoints
- Real-time document analysis and Q&A enhancement
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import MCP server components
from mcp_server.api_endpoints.api_endpoints import app
from mcp_server.bdh_architecture import create_bdh_processor
from mcp_server.fraud_detection import create_fraud_detector

# Import existing Due Diligence components
from document_extractor import DocumentExtractor
from document_ingestion import DocumentIngestionPipeline
from qa_workflow import DueDiligenceQA
from audit_logger import AuditLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_services():
    """Initialize all MCP server services."""
    try:
        logger.info("Initializing Due Diligence Copilot MCP Server...")
        
        # Initialize BDH processor
        bdh_processor = create_bdh_processor()
        logger.info("✓ BDH processor initialized")
        
        # Initialize fraud detector
        fraud_detector = create_fraud_detector()
        logger.info("✓ Fraud detector initialized")
        
        # Initialize existing Due Diligence components
        document_extractor = DocumentExtractor()
        logger.info("✓ Document extractor initialized")
        
        document_pipeline = DocumentIngestionPipeline()
        logger.info("✓ Document pipeline initialized")
        
        qa_workflow = DueDiligenceQA(document_pipeline)
        logger.info("✓ QA workflow initialized")
        
        audit_logger = AuditLogger()
        logger.info("✓ Audit logger initialized")
        
        logger.info("All services initialized successfully!")
        
        return {
            "bdh_processor": bdh_processor,
            "fraud_detector": fraud_detector,
            "document_extractor": document_extractor,
            "document_pipeline": document_pipeline,
            "qa_workflow": qa_workflow,
            "audit_logger": audit_logger
        }
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise

def create_directories():
    """Create necessary directories for the MCP server."""
    directories = [
        "data/financial_docs",
        "logs",
        "uploads",
        "index_data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")

def main():
    """Main entry point for the MCP server."""
    try:
        # Create necessary directories
        create_directories()
        
        # Initialize services
        services = initialize_services()
        
        # Store services globally for API access
        app.state.services = services
        
        logger.info("Due Diligence Copilot MCP Server ready!")
        logger.info("Access API documentation at: http://localhost:8000/docs")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to start MCP server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Start the server
    import uvicorn
    
    # Initialize the app
    app_instance = main()
    
    # Run the server
    uvicorn.run(
        app_instance,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )