"""
Test file for Financial Agent MCP Server
Simple tests to verify the basic functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import tempfile
import os

from document_ingestion.ingestion_service import DocumentIngestionService
from document_conversion.conversion_service import DocumentConversionService
from ai_services.ai_processor import AIProcessor
from fraud_detection.fraud_analyzer import FraudAnalyzer

class TestDocumentIngestion:
    """Test cases for document ingestion service."""
    
    @pytest.fixture
    def ingestion_service(self):
        """Create ingestion service instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = DocumentIngestionService(storage_path=temp_dir)
            yield service
    
    @pytest.mark.asyncio
    async def test_process_document(self, ingestion_service):
        """Test document processing."""
        # Mock file object
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read.return_value = b"test content"
        
        # Process document
        document_id = await ingestion_service.process_document(mock_file)
        
        # Verify document was processed
        assert document_id is not None
        assert len(document_id) == 36  # UUID length
        
        # Verify metadata was stored
        document = await ingestion_service.get_document(document_id)
        assert document is not None
        assert document["filename"] == "test.pdf"
        assert document["content_type"] == "application/pdf"

class TestDocumentConversion:
    """Test cases for document conversion service."""
    
    @pytest.fixture
    def conversion_service(self):
        """Create conversion service instance."""
        return DocumentConversionService()
    
    @pytest.mark.asyncio
    async def test_convert_csv(self, conversion_service):
        """Test CSV conversion."""
        csv_content = b"name,amount,date\nJohn,100,2023-01-01\nJane,200,2023-01-02"
        
        document_data = {
            "content_type": "text/csv",
            "content": csv_content,
            "document_id": "test-123"
        }
        
        result = await conversion_service.convert_document(document_data)
        
        assert result["document_type"] == "csv"
        assert result["row_count"] == 2
        assert result["column_count"] == 3
        assert "name" in result["columns"]
        assert "amount" in result["columns"]
        assert "date" in result["columns"]

class TestFraudAnalyzer:
    """Test cases for fraud analyzer."""
    
    @pytest.fixture
    def fraud_analyzer(self):
        """Create fraud analyzer instance."""
        return FraudAnalyzer()
    
    @pytest.mark.asyncio
    async def test_calculate_fraud_score(self, fraud_analyzer):
        """Test fraud score calculation."""
        analysis_results = {
            "sentiment_analysis": {"sentiment": "negative", "confidence": 0.8},
            "anomaly_detection": {"anomaly_count": 3},
            "risk_indicators": {"high_risk": ["wire_transfer"], "medium_risk": []},
            "compliance_check": {"issues": ["missing_kyc"]}
        }
        
        fraud_score = await fraud_analyzer.calculate_fraud_score(analysis_results)
        
        assert 0.0 <= fraud_score <= 1.0
        assert fraud_score > 0.5  # Should be high due to negative sentiment and anomalies
    
    @pytest.mark.asyncio
    async def test_analyze_transaction(self, fraud_analyzer):
        """Test transaction analysis."""
        transaction_data = {
            "amount": 100000,
            "timestamp": "2023-01-01T02:00:00Z",
            "type": "wire_transfer",
            "user_id": "user123"
        }
        
        indicators = await fraud_analyzer.analyze_transaction(transaction_data)
        
        assert "amount_indicators" in indicators
        assert "timing_indicators" in indicators
        assert "pattern_indicators" in indicators
        assert "behavioral_indicators" in indicators
        assert "document_indicators" in indicators

class TestAIServices:
    """Test cases for AI services."""
    
    @pytest.mark.asyncio
    async def test_ai_processor_initialization(self):
        """Test AI processor initialization."""
        processor = AIProcessor()
        
        # Should initialize without errors
        assert processor is not None
        # Note: Some models might not be available in test environment
    
    @pytest.mark.asyncio
    async def test_extract_text_content(self):
        """Test text extraction from different document types."""
        processor = AIProcessor()
        
        # Test PDF document
        pdf_data = {
            "document_type": "pdf",
            "full_text": "This is a test PDF document."
        }
        
        text = await processor._extract_text_content(pdf_data)
        assert text == "This is a test PDF document."
        
        # Test CSV document
        csv_data = {
            "document_type": "csv",
            "records": [{"name": "John", "amount": 100}]
        }
        
        text = await processor._extract_text_content(csv_data)
        assert "John" in text
        assert "100" in text

if __name__ == "__main__":
    # Run basic tests
    print("Running basic tests...")
    
    # Test fraud analyzer
    analyzer = FraudAnalyzer()
    print("✓ FraudAnalyzer initialized")
    
    # Test document ingestion
    with tempfile.TemporaryDirectory() as temp_dir:
        ingestion = DocumentIngestionService(storage_path=temp_dir)
        print("✓ DocumentIngestionService initialized")
    
    # Test document conversion
    conversion = DocumentConversionService()
    print("✓ DocumentConversionService initialized")
    
    # Test AI processor
    processor = AIProcessor()
    print("✓ AIProcessor initialized")
    
    print("\nAll basic tests passed!")
