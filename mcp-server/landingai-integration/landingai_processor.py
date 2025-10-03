"""
LandingAI ADE Integration Module
Integrates LandingAI's Automated Document Extraction with the MCP server
for enhanced document processing and fraud detection.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
import asyncio
import logging

from landingai_ade import LandingAIADE
from landingai_ade.types import ParseResponse, ExtractResponse
from landingai_ade.lib import pydantic_to_json_schema
from pydantic import BaseModel, Field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class FinancialDocumentSchema(BaseModel):
    """Schema for financial document extraction."""
    
    # Invoice fields
    invoice_number: Optional[str] = Field(
        description="The invoice number or reference",
        title="Invoice Number"
    )
    invoice_date: Optional[str] = Field(
        description="The invoice date",
        title="Invoice Date"
    )
    due_date: Optional[str] = Field(
        description="The payment due date",
        title="Due Date"
    )
    
    # Amount fields
    subtotal: Optional[float] = Field(
        description="The subtotal amount before taxes",
        title="Subtotal"
    )
    tax_amount: Optional[float] = Field(
        description="The tax amount",
        title="Tax Amount"
    )
    total_amount: Optional[float] = Field(
        description="The total amount due",
        title="Total Amount"
    )
    
    # Party information
    vendor_name: Optional[str] = Field(
        description="The vendor or supplier name",
        title="Vendor Name"
    )
    vendor_address: Optional[str] = Field(
        description="The vendor address",
        title="Vendor Address"
    )
    customer_name: Optional[str] = Field(
        description="The customer or buyer name",
        title="Customer Name"
    )
    customer_address: Optional[str] = Field(
        description="The customer address",
        title="Customer Address"
    )
    
    # Line items
    line_items: Optional[List[Dict[str, Any]]] = Field(
        description="List of line items with quantity, description, rate, and amount",
        title="Line Items"
    )
    
    # Risk indicators
    risk_indicators: Optional[List[str]] = Field(
        description="Potential risk indicators found in the document",
        title="Risk Indicators"
    )

class BankStatementSchema(BaseModel):
    """Schema for bank statement extraction."""
    
    account_number: Optional[str] = Field(
        description="The bank account number",
        title="Account Number"
    )
    statement_period: Optional[str] = Field(
        description="The statement period (e.g., 'January 2024')",
        title="Statement Period"
    )
    opening_balance: Optional[float] = Field(
        description="The opening balance",
        title="Opening Balance"
    )
    closing_balance: Optional[float] = Field(
        description="The closing balance",
        title="Closing Balance"
    )
    
    transactions: Optional[List[Dict[str, Any]]] = Field(
        description="List of transactions with date, description, amount, and balance",
        title="Transactions"
    )
    
    # Risk indicators
    unusual_transactions: Optional[List[str]] = Field(
        description="Unusual or suspicious transactions",
        title="Unusual Transactions"
    )

class ReceiptSchema(BaseModel):
    """Schema for receipt extraction."""
    
    merchant_name: Optional[str] = Field(
        description="The merchant or store name",
        title="Merchant Name"
    )
    transaction_date: Optional[str] = Field(
        description="The transaction date",
        title="Transaction Date"
    )
    total_amount: Optional[float] = Field(
        description="The total amount paid",
        title="Total Amount"
    )
    payment_method: Optional[str] = Field(
        description="The payment method used",
        title="Payment Method"
    )
    
    items: Optional[List[Dict[str, Any]]] = Field(
        description="List of purchased items",
        title="Items"
    )
    
    # Risk indicators
    risk_flags: Optional[List[str]] = Field(
        description="Risk flags for this transaction",
        title="Risk Flags"
    )

class LandingAIIntegration:
    """Integration class for LandingAI ADE with MCP server."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LandingAI integration.
        
        Args:
            api_key: LandingAI API key. If None, will try to load from environment.
        """
        load_dotenv()
        
        if api_key is None:
            api_key = os.getenv("VISION_AGENT_API_KEY")
        
        if not api_key:
            raise ValueError(
                "LandingAI API key not found. Please set VISION_AGENT_API_KEY environment variable."
            )
        
        # Set endpoint
        os.environ["ENDPOINT_HOST"] = "https://api.va.landing.ai"
        
        self.client = LandingAIADE(apikey=api_key)
        self.supported_models = ["dpt-2-latest", "dpt-1-latest"]
        self.default_model = "dpt-2-latest"
        
        logger.info("LandingAI ADE client initialized successfully")
    
    async def parse_document(self, document_path: Union[str, Path], 
                           model: str = None) -> ParseResponse:
        """
        Parse a document using LandingAI ADE.
        
        Args:
            document_path: Path to the document file
            model: Model to use for parsing (default: dpt-2-latest)
            
        Returns:
            ParseResponse object with parsed content
        """
        if model is None:
            model = self.default_model
        
        try:
            document_path = Path(document_path)
            if not document_path.exists():
                raise FileNotFoundError(f"Document not found: {document_path}")
            
            # Parse document
            response = self.client.parse(
                document=document_path,
                model=model
            )
            
            logger.info(f"Document parsed successfully: {document_path}")
            return response
            
        except Exception as e:
            logger.error(f"Error parsing document {document_path}: {str(e)}")
            raise
    
    async def extract_financial_data(self, parse_response: ParseResponse, 
                                   document_type: str = "invoice") -> ExtractResponse:
        """
        Extract structured financial data from parsed document.
        
        Args:
            parse_response: Parsed document response
            document_type: Type of financial document (invoice, bank_statement, receipt)
            
        Returns:
            ExtractResponse with structured data
        """
        try:
            # Choose schema based on document type
            if document_type == "invoice":
                schema_class = FinancialDocumentSchema
            elif document_type == "bank_statement":
                schema_class = BankStatementSchema
            elif document_type == "receipt":
                schema_class = ReceiptSchema
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Convert schema to JSON schema
            json_schema = pydantic_to_json_schema(schema_class)
            
            # Extract structured data
            response = self.client.extract(
                schema=json_schema,
                parsed=parse_response
            )
            
            logger.info(f"Financial data extracted successfully for {document_type}")
            return response
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {str(e)}")
            raise
    
    async def analyze_document_for_fraud(self, parse_response: ParseResponse) -> Dict[str, Any]:
        """
        Analyze document for potential fraud indicators.
        
        Args:
            parse_response: Parsed document response
            
        Returns:
            Dictionary with fraud analysis results
        """
        try:
            fraud_analysis = {
                "document_id": str(datetime.now().timestamp()),
                "analysis_timestamp": datetime.now().isoformat(),
                "risk_score": 0.0,
                "fraud_indicators": [],
                "recommendations": []
            }
            
            # Extract text content
            text_content = parse_response.markdown.lower()
            
            # Check for suspicious patterns
            suspicious_patterns = [
                "urgent payment",
                "wire transfer",
                "bitcoin",
                "cryptocurrency",
                "offshore account",
                "shell company",
                "money laundering",
                "tax evasion",
                "confidential",
                "immediate action"
            ]
            
            for pattern in suspicious_patterns:
                if pattern in text_content:
                    fraud_analysis["fraud_indicators"].append(pattern)
                    fraud_analysis["risk_score"] += 0.1
            
            # Check for unusual amounts
            amounts = self._extract_amounts(text_content)
            if amounts:
                fraud_analysis["amount_analysis"] = self._analyze_amounts(amounts)
            
            # Check for unusual dates
            dates = self._extract_dates(text_content)
            if dates:
                fraud_analysis["date_analysis"] = self._analyze_dates(dates)
            
            # Generate recommendations
            fraud_analysis["recommendations"] = self._generate_recommendations(fraud_analysis)
            
            # Cap risk score at 1.0
            fraud_analysis["risk_score"] = min(fraud_analysis["risk_score"], 1.0)
            
            logger.info(f"Fraud analysis completed. Risk score: {fraud_analysis['risk_score']}")
            return fraud_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing document for fraud: {str(e)}")
            raise
    
    def _extract_amounts(self, text: str) -> List[float]:
        """Extract monetary amounts from text."""
        import re
        
        # Pattern for monetary amounts
        amount_pattern = r'\$[\d,]+\.?\d*'
        amounts = re.findall(amount_pattern, text)
        
        # Convert to float
        numeric_amounts = []
        for amount in amounts:
            try:
                numeric_amount = float(amount.replace('$', '').replace(',', ''))
                numeric_amounts.append(numeric_amount)
            except ValueError:
                continue
        
        return numeric_amounts
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        import re
        
        # Pattern for dates
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{2,4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{2,4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return dates
    
    def _analyze_amounts(self, amounts: List[float]) -> Dict[str, Any]:
        """Analyze amounts for suspicious patterns."""
        if not amounts:
            return {}
        
        analysis = {
            "count": len(amounts),
            "total": sum(amounts),
            "average": sum(amounts) / len(amounts),
            "max": max(amounts),
            "min": min(amounts),
            "suspicious_patterns": []
        }
        
        # Check for round numbers (suspicious)
        round_amounts = [a for a in amounts if a % 100 == 0 and a > 1000]
        if len(round_amounts) > len(amounts) * 0.5:
            analysis["suspicious_patterns"].append("excessive_round_numbers")
        
        # Check for unusually large amounts
        if analysis["max"] > 100000:
            analysis["suspicious_patterns"].append("unusually_large_amount")
        
        return analysis
    
    def _analyze_dates(self, dates: List[str]) -> Dict[str, Any]:
        """Analyze dates for suspicious patterns."""
        if not dates:
            return {}
        
        analysis = {
            "count": len(dates),
            "unique_dates": len(set(dates)),
            "suspicious_patterns": []
        }
        
        # Check for too many dates (suspicious)
        if len(dates) > 20:
            analysis["suspicious_patterns"].append("excessive_dates")
        
        # Check for future dates
        from datetime import datetime
        current_year = datetime.now().year
        future_dates = [d for d in dates if any(str(year) in d for year in range(current_year + 1, current_year + 10))]
        if future_dates:
            analysis["suspicious_patterns"].append("future_dates")
        
        return analysis
    
    def _generate_recommendations(self, fraud_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on fraud analysis."""
        recommendations = []
        
        risk_score = fraud_analysis.get("risk_score", 0.0)
        fraud_indicators = fraud_analysis.get("fraud_indicators", [])
        
        if risk_score > 0.7:
            recommendations.extend([
                "High fraud risk detected - immediate manual review required",
                "Consider freezing account temporarily",
                "Contact customer for verification",
                "Escalate to fraud investigation team"
            ])
        elif risk_score > 0.4:
            recommendations.extend([
                "Medium fraud risk detected - manual review recommended",
                "Request additional documentation",
                "Monitor account for suspicious activity",
                "Consider enhanced verification"
            ])
        else:
            recommendations.extend([
                "Low fraud risk - standard processing recommended",
                "Continue monitoring",
                "Document analysis for future reference"
            ])
        
        # Specific recommendations based on indicators
        if "wire transfer" in fraud_indicators:
            recommendations.append("Verify wire transfer details with customer")
        
        if "bitcoin" in fraud_indicators or "cryptocurrency" in fraud_indicators:
            recommendations.append("Enhanced verification required for cryptocurrency transactions")
        
        return recommendations
    
    async def process_document_pipeline(self, document_path: Union[str, Path], 
                                      document_type: str = "invoice") -> Dict[str, Any]:
        """
        Complete document processing pipeline.
        
        Args:
            document_path: Path to the document
            document_type: Type of document to process
            
        Returns:
            Complete processing results
        """
        try:
            # Step 1: Parse document
            parse_response = await self.parse_document(document_path)
            
            # Step 2: Extract structured data
            extract_response = await self.extract_financial_data(parse_response, document_type)
            
            # Step 3: Analyze for fraud
            fraud_analysis = await self.analyze_document_for_fraud(parse_response)
            
            # Combine results
            results = {
                "document_path": str(document_path),
                "document_type": document_type,
                "processing_timestamp": datetime.now().isoformat(),
                "parse_response": {
                    "markdown": parse_response.markdown[:1000] + "..." if len(parse_response.markdown) > 1000 else parse_response.markdown,
                    "chunks_count": len(parse_response.chunks) if parse_response.chunks else 0,
                    "grounding_count": len(parse_response.grounding) if parse_response.grounding else 0
                },
                "extracted_data": extract_response.extraction if extract_response else {},
                "fraud_analysis": fraud_analysis,
                "status": "completed"
            }
            
            logger.info(f"Document processing pipeline completed: {document_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error in document processing pipeline: {str(e)}")
            return {
                "document_path": str(document_path),
                "document_type": document_type,
                "processing_timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }

# Example usage
async def test_landingai_integration():
    """Test LandingAI integration functionality."""
    try:
        # Initialize integration
        integration = LandingAIIntegration()
        
        # Test with a sample document (you would need to provide a real document)
        # sample_doc = "path/to/sample/document.pdf"
        # results = await integration.process_document_pipeline(sample_doc, "invoice")
        # print(f"Processing results: {results}")
        
        print("LandingAI integration test completed successfully!")
        
    except Exception as e:
        print(f"LandingAI integration test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_landingai_integration())
