"""
Fraud Detection Package for Due Diligence Copilot
"""

from .fraud_detector import (
    EnhancedFraudDetector,
    FraudPatternDetector,
    BehavioralAnalyzer,
    create_fraud_detector,
    detect_fraud_in_document
)

__all__ = [
    "EnhancedFraudDetector",
    "FraudPatternDetector", 
    "BehavioralAnalyzer",
    "create_fraud_detector",
    "detect_fraud_in_document"
]
