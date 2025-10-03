"""
LandingAI Integration Package
Integration with LandingAI's Automated Document Extraction service.
"""

from .landingai_processor import (
    LandingAIIntegration,
    FinancialDocumentSchema,
    BankStatementSchema,
    ReceiptSchema
)

__all__ = [
    "LandingAIIntegration",
    "FinancialDocumentSchema", 
    "BankStatementSchema",
    "ReceiptSchema"
]
