"""
Fraud Analyzer Service
Specialized fraud detection algorithms for financial transactions.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import re
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)

class FraudAnalyzer:
    """Specialized fraud detection and analysis service."""
    
    def __init__(self):
        self.fraud_patterns = self._initialize_fraud_patterns()
        self.risk_weights = self._initialize_risk_weights()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
    def _initialize_fraud_patterns(self) -> Dict[str, List[str]]:
        """Initialize known fraud patterns."""
        return {
            "transaction_patterns": [
                r"round\s+number",  # Round numbers often indicate fabricated amounts
                r"multiple\s+of\s+100",  # Suspicious round amounts
                r"exact\s+amount",  # Exact amounts without cents
            ],
            "behavioral_patterns": [
                r"unusual\s+timing",  # Transactions at odd hours
                r"rapid\s+succession",  # Multiple transactions in short time
                r"large\s+amount",  # Unusually large amounts
            ],
            "communication_patterns": [
                r"urgent\s+request",  # Urgent payment requests
                r"confidential",  # Confidentiality claims
                r"wire\s+transfer",  # Wire transfer requests
                r"bitcoin",  # Cryptocurrency mentions
            ],
            "document_patterns": [
                r"forged\s+signature",  # Signature anomalies
                r"altered\s+document",  # Document tampering
                r"missing\s+information",  # Incomplete documentation
            ]
        }
    
    def _initialize_risk_weights(self) -> Dict[str, float]:
        """Initialize risk weights for different factors."""
        return {
            "amount_risk": 0.3,
            "timing_risk": 0.2,
            "pattern_risk": 0.25,
            "behavioral_risk": 0.15,
            "document_risk": 0.1
        }
    
    async def calculate_fraud_score(self, analysis_results: Dict[str, Any]) -> float:
        """
        Calculate comprehensive fraud score based on analysis results.
        
        Args:
            analysis_results: Results from AI analysis
            
        Returns:
            float: Fraud score between 0.0 and 1.0
        """
        try:
            fraud_score = 0.0
            
            # Analyze sentiment risk
            sentiment = analysis_results.get("sentiment_analysis", {})
            if sentiment.get("sentiment") == "negative":
                fraud_score += 0.1
            
            # Analyze anomaly risk
            anomalies = analysis_results.get("anomaly_detection", {})
            anomaly_count = anomalies.get("anomaly_count", 0)
            fraud_score += min(anomaly_count * 0.05, 0.2)
            
            # Analyze risk indicators
            risk_indicators = analysis_results.get("risk_indicators", {})
            high_risk_count = len(risk_indicators.get("high_risk", []))
            medium_risk_count = len(risk_indicators.get("medium_risk", []))
            fraud_score += high_risk_count * 0.1 + medium_risk_count * 0.03
            
            # Analyze compliance issues
            compliance = analysis_results.get("compliance_check", {})
            compliance_issues = len(compliance.get("issues", []))
            fraud_score += compliance_issues * 0.05
            
            # Analyze document type risk
            doc_classification = analysis_results.get("document_classification", {})
            doc_type = doc_classification.get("document_type", "unknown")
            fraud_score += self._get_document_type_risk(doc_type)
            
            return min(fraud_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating fraud score: {str(e)}")
            return 0.5  # Default medium risk
    
    async def analyze_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transaction data for fraud indicators.
        
        Args:
            transaction_data: Transaction information
            
        Returns:
            Dict containing fraud indicators
        """
        try:
            indicators = {
                "amount_indicators": [],
                "timing_indicators": [],
                "pattern_indicators": [],
                "behavioral_indicators": [],
                "document_indicators": []
            }
            
            # Analyze amount patterns
            amount = transaction_data.get("amount", 0)
            if amount > 0:
                amount_indicators = await self._analyze_amount_patterns(amount)
                indicators["amount_indicators"] = amount_indicators
            
            # Analyze timing patterns
            timestamp = transaction_data.get("timestamp")
            if timestamp:
                timing_indicators = await self._analyze_timing_patterns(timestamp)
                indicators["timing_indicators"] = timing_indicators
            
            # Analyze transaction patterns
            pattern_indicators = await self._analyze_transaction_patterns(transaction_data)
            indicators["pattern_indicators"] = pattern_indicators
            
            # Analyze behavioral patterns
            behavioral_indicators = await self._analyze_behavioral_patterns(transaction_data)
            indicators["behavioral_indicators"] = behavioral_indicators
            
            # Analyze document patterns
            document_indicators = await self._analyze_document_patterns(transaction_data)
            indicators["document_indicators"] = document_indicators
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error analyzing transaction: {str(e)}")
            return {"error": str(e)}
    
    async def calculate_risk_score(self, fraud_indicators: Dict[str, Any], 
                                user_context: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate risk score based on fraud indicators.
        
        Args:
            fraud_indicators: Fraud indicators from analysis
            user_context: Additional user context
            
        Returns:
            float: Risk score between 0.0 and 1.0
        """
        try:
            risk_score = 0.0
            
            # Calculate amount risk
            amount_indicators = fraud_indicators.get("amount_indicators", [])
            amount_risk = len(amount_indicators) * 0.1
            risk_score += amount_risk * self.risk_weights["amount_risk"]
            
            # Calculate timing risk
            timing_indicators = fraud_indicators.get("timing_indicators", [])
            timing_risk = len(timing_indicators) * 0.1
            risk_score += timing_risk * self.risk_weights["timing_risk"]
            
            # Calculate pattern risk
            pattern_indicators = fraud_indicators.get("pattern_indicators", [])
            pattern_risk = len(pattern_indicators) * 0.1
            risk_score += pattern_risk * self.risk_weights["pattern_risk"]
            
            # Calculate behavioral risk
            behavioral_indicators = fraud_indicators.get("behavioral_indicators", [])
            behavioral_risk = len(behavioral_indicators) * 0.1
            risk_score += behavioral_risk * self.risk_weights["behavioral_risk"]
            
            # Calculate document risk
            document_indicators = fraud_indicators.get("document_indicators", [])
            document_risk = len(document_indicators) * 0.1
            risk_score += document_risk * self.risk_weights["document_risk"]
            
            # Apply user context adjustments
            if user_context:
                risk_score = await self._apply_user_context_adjustments(risk_score, user_context)
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 0.5
    
    async def generate_alerts(self, fraud_indicators: Dict[str, Any], 
                            risk_score: float) -> List[Dict[str, Any]]:
        """
        Generate alerts based on fraud indicators and risk score.
        
        Args:
            fraud_indicators: Fraud indicators
            risk_score: Calculated risk score
            
        Returns:
            List of alert objects
        """
        alerts = []
        
        # High-risk alerts
        if risk_score > 0.7:
            alerts.append({
                "level": "high",
                "type": "fraud_risk",
                "message": "High fraud risk detected",
                "recommendation": "Immediate review required",
                "risk_score": risk_score
            })
        
        # Medium-risk alerts
        elif risk_score > 0.4:
            alerts.append({
                "level": "medium",
                "type": "fraud_risk",
                "message": "Medium fraud risk detected",
                "recommendation": "Manual review recommended",
                "risk_score": risk_score
            })
        
        # Specific pattern alerts
        for indicator_type, indicators in fraud_indicators.items():
            if len(indicators) > 2:  # Multiple indicators of same type
                alerts.append({
                    "level": "medium",
                    "type": f"{indicator_type}_pattern",
                    "message": f"Multiple {indicator_type} detected",
                    "recommendation": "Review transaction patterns",
                    "indicator_count": len(indicators)
                })
        
        return alerts
    
    async def generate_recommendations(self, analysis_results: Dict[str, Any], 
                                     fraud_score: float) -> List[str]:
        """
        Generate recommendations based on analysis results.
        
        Args:
            analysis_results: Analysis results
            fraud_score: Calculated fraud score
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # High fraud score recommendations
        if fraud_score > 0.7:
            recommendations.extend([
                "Immediate manual review required",
                "Consider freezing account temporarily",
                "Contact customer for verification",
                "Escalate to fraud investigation team"
            ])
        
        # Medium fraud score recommendations
        elif fraud_score > 0.4:
            recommendations.extend([
                "Manual review recommended",
                "Request additional documentation",
                "Monitor account for suspicious activity",
                "Consider enhanced verification"
            ])
        
        # Low fraud score recommendations
        else:
            recommendations.extend([
                "Transaction appears normal",
                "Continue monitoring",
                "Standard processing recommended"
            ])
        
        # Compliance-based recommendations
        compliance = analysis_results.get("compliance_check", {})
        if compliance.get("issues"):
            recommendations.append("Address compliance issues before processing")
        
        # Anomaly-based recommendations
        anomalies = analysis_results.get("anomaly_detection", {})
        if anomalies.get("anomaly_count", 0) > 3:
            recommendations.append("Investigate detected anomalies")
        
        return recommendations
    
    async def _analyze_amount_patterns(self, amount: float) -> List[str]:
        """Analyze amount patterns for fraud indicators."""
        indicators = []
        
        # Round number check
        if amount % 100 == 0 and amount > 1000:
            indicators.append("round_number_amount")
        
        # Suspiciously large amount
        if amount > 100000:
            indicators.append("large_amount")
        
        # Exact amount without cents
        if amount == int(amount) and amount > 100:
            indicators.append("exact_amount")
        
        return indicators
    
    async def _analyze_timing_patterns(self, timestamp: str) -> List[str]:
        """Analyze timing patterns for fraud indicators."""
        indicators = []
        
        try:
            # Parse timestamp
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            # Check for unusual hours (late night/early morning)
            hour = dt.hour
            if hour < 6 or hour > 22:
                indicators.append("unusual_hour")
            
            # Check for weekend transactions
            if dt.weekday() >= 5:  # Saturday or Sunday
                indicators.append("weekend_transaction")
            
            # Check for holiday transactions (simplified)
            if dt.month == 12 and dt.day in [24, 25, 31]:
                indicators.append("holiday_transaction")
            
        except Exception as e:
            logger.warning(f"Error analyzing timing patterns: {str(e)}")
        
        return indicators
    
    async def _analyze_transaction_patterns(self, transaction_data: Dict[str, Any]) -> List[str]:
        """Analyze transaction patterns for fraud indicators."""
        indicators = []
        
        # Check for rapid succession (would need historical data)
        # This is a simplified version
        transaction_id = transaction_data.get("id", "")
        if "rapid" in transaction_id.lower():
            indicators.append("rapid_succession")
        
        # Check for unusual transaction types
        transaction_type = transaction_data.get("type", "").lower()
        suspicious_types = ["wire", "crypto", "offshore"]
        if any(suspicious_type in transaction_type for suspicious_type in suspicious_types):
            indicators.append("suspicious_transaction_type")
        
        return indicators
    
    async def _analyze_behavioral_patterns(self, transaction_data: Dict[str, Any]) -> List[str]:
        """Analyze behavioral patterns for fraud indicators."""
        indicators = []
        
        # Check for unusual user behavior
        user_id = transaction_data.get("user_id", "")
        if not user_id:
            indicators.append("missing_user_id")
        
        # Check for unusual location
        location = transaction_data.get("location", "")
        if location and "unusual" in location.lower():
            indicators.append("unusual_location")
        
        return indicators
    
    async def _analyze_document_patterns(self, transaction_data: Dict[str, Any]) -> List[str]:
        """Analyze document patterns for fraud indicators."""
        indicators = []
        
        # Check for missing documentation
        required_docs = ["identification", "proof_of_address", "source_of_funds"]
        provided_docs = transaction_data.get("documents", [])
        
        for doc in required_docs:
            if doc not in provided_docs:
                indicators.append(f"missing_{doc}")
        
        # Check for document quality
        doc_quality = transaction_data.get("document_quality", "unknown")
        if doc_quality == "poor":
            indicators.append("poor_document_quality")
        
        return indicators
    
    def _get_document_type_risk(self, doc_type: str) -> float:
        """Get risk score for document type."""
        risk_scores = {
            "bank_statement": 0.1,
            "invoice": 0.2,
            "receipt": 0.05,
            "contract": 0.3,
            "tax_document": 0.4,
            "loan_application": 0.5,
            "unknown": 0.3
        }
        return risk_scores.get(doc_type, 0.3)
    
    async def _apply_user_context_adjustments(self, risk_score: float, 
                                            user_context: Dict[str, Any]) -> float:
        """Apply user context adjustments to risk score."""
        adjusted_score = risk_score
        
        # Adjust based on user history
        user_history = user_context.get("history", {})
        if user_history.get("fraud_history"):
            adjusted_score += 0.2
        
        # Adjust based on account age
        account_age_days = user_context.get("account_age_days", 0)
        if account_age_days < 30:
            adjusted_score += 0.1
        
        # Adjust based on verification level
        verification_level = user_context.get("verification_level", "basic")
        if verification_level == "enhanced":
            adjusted_score -= 0.1
        elif verification_level == "basic":
            adjusted_score += 0.05
        
        return max(0.0, min(adjusted_score, 1.0))
