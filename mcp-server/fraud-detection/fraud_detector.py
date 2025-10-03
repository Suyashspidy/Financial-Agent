"""
Enhanced Fraud Detection Module
Integrates BDH architecture with traditional fraud detection for Due Diligence Copilot
"""

import logging
import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class FraudDetectionConfig:
    """Configuration for fraud detection system."""
    risk_threshold_low: float = 0.3
    risk_threshold_medium: float = 0.6
    risk_threshold_high: float = 0.8
    amount_threshold: float = 100000
    suspicious_pattern_threshold: float = 0.7
    enable_bdh_analysis: bool = True
    enable_pattern_detection: bool = True
    enable_behavioral_analysis: bool = True

class FraudPatternDetector:
    """Detects fraud patterns in financial documents."""
    
    def __init__(self, config: FraudDetectionConfig = None):
        self.config = config or FraudDetectionConfig()
        self.fraud_patterns = self._initialize_fraud_patterns()
        self.risk_keywords = self._initialize_risk_keywords()
        
    def _initialize_fraud_patterns(self) -> Dict[str, List[str]]:
        """Initialize known fraud patterns."""
        return {
            "transaction_patterns": [
                r"round\s+number",  # Round numbers often indicate fabricated amounts
                r"multiple\s+of\s+100",  # Suspicious round amounts
                r"exact\s+amount",  # Exact amounts without cents
                r"wire\s+transfer",  # Wire transfer requests
                r"bitcoin",  # Cryptocurrency mentions
                r"offshore",  # Offshore account references
            ],
            "behavioral_patterns": [
                r"urgent\s+request",  # Urgent payment requests
                r"immediate\s+action",  # Immediate action required
                r"confidential",  # Confidentiality claims
                r"private\s+transaction",  # Private transaction claims
                r"unusual\s+timing",  # Unusual timing patterns
                r"rapid\s+succession",  # Rapid succession of transactions
            ],
            "document_patterns": [
                r"forged\s+signature",  # Signature anomalies
                r"altered\s+document",  # Document tampering
                r"missing\s+information",  # Incomplete documentation
                r"inconsistent\s+dates",  # Date inconsistencies
                r"duplicate\s+entries",  # Duplicate entries
            ],
            "legal_patterns": [
                r"indemnity\s+clause",  # Broad indemnity clauses
                r"liability\s+cap",  # Liability limitations
                r"force\s+majeure",  # Force majeure clauses
                r"arbitration\s+clause",  # Arbitration requirements
                r"governing\s+law",  # Governing law clauses
            ]
        }
    
    def _initialize_risk_keywords(self) -> Dict[str, List[str]]:
        """Initialize risk keywords for different categories."""
        return {
            "high_risk": [
                "fraud", "money laundering", "tax evasion", "shell company",
                "offshore", "cryptocurrency", "bitcoin", "wire transfer",
                "urgent", "confidential", "immediate"
            ],
            "medium_risk": [
                "unusual", "irregular", "anomaly", "suspicious", "private",
                "indemnity", "liability", "penalty", "breach"
            ],
            "low_risk": [
                "routine", "standard", "normal", "regular", "standard",
                "compliance", "verification", "audit"
            ]
        }
    
    def detect_patterns(self, text: str) -> Dict[str, Any]:
        """
        Detect fraud patterns in text.
        
        Args:
            text: Document text to analyze
            
        Returns:
            Dictionary with detected patterns and risk scores
        """
        text_lower = text.lower()
        detected_patterns = {
            "transaction_patterns": [],
            "behavioral_patterns": [],
            "document_patterns": [],
            "legal_patterns": [],
            "risk_keywords": [],
            "overall_risk_score": 0.0
        }
        
        # Detect patterns in each category
        for category, patterns in self.fraud_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected_patterns[category].append(pattern)
        
        # Detect risk keywords
        for risk_level, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_patterns["risk_keywords"].append({
                        "keyword": keyword,
                        "risk_level": risk_level
                    })
        
        # Calculate overall risk score
        detected_patterns["overall_risk_score"] = self._calculate_pattern_risk_score(detected_patterns)
        
        return detected_patterns
    
    def _calculate_pattern_risk_score(self, patterns: Dict[str, Any]) -> float:
        """Calculate risk score based on detected patterns."""
        risk_score = 0.0
        
        # Weight different pattern categories
        weights = {
            "transaction_patterns": 0.3,
            "behavioral_patterns": 0.25,
            "document_patterns": 0.2,
            "legal_patterns": 0.15,
            "risk_keywords": 0.1
        }
        
        for category, weight in weights.items():
            if category in patterns:
                pattern_count = len(patterns[category])
                risk_score += min(pattern_count * 0.1, 1.0) * weight
        
        # Add risk keyword scoring
        if "risk_keywords" in patterns:
            high_risk_count = len([kw for kw in patterns["risk_keywords"] if kw["risk_level"] == "high_risk"])
            medium_risk_count = len([kw for kw in patterns["risk_keywords"] if kw["risk_level"] == "medium_risk"])
            
            risk_score += high_risk_count * 0.1 + medium_risk_count * 0.05
        
        return min(risk_score, 1.0)

class BehavioralAnalyzer:
    """Analyzes behavioral patterns for fraud detection."""
    
    def __init__(self, config: FraudDetectionConfig = None):
        self.config = config or FraudDetectionConfig()
        
    def analyze_transaction_behavior(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transaction behavior patterns.
        
        Args:
            transaction_data: Transaction information
            
        Returns:
            Behavioral analysis results
        """
        analysis = {
            "amount_analysis": self._analyze_amount_patterns(transaction_data),
            "timing_analysis": self._analyze_timing_patterns(transaction_data),
            "frequency_analysis": self._analyze_frequency_patterns(transaction_data),
            "location_analysis": self._analyze_location_patterns(transaction_data),
            "behavioral_risk_score": 0.0
        }
        
        # Calculate overall behavioral risk score
        analysis["behavioral_risk_score"] = self._calculate_behavioral_risk(analysis)
        
        return analysis
    
    def _analyze_amount_patterns(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze amount patterns."""
        amount = transaction_data.get("amount", 0)
        
        analysis = {
            "amount": amount,
            "is_round_number": amount % 100 == 0 and amount > 1000,
            "is_large_amount": amount > self.config.amount_threshold,
            "is_exact_amount": amount == int(amount) and amount > 100,
            "suspicious_patterns": []
        }
        
        if analysis["is_round_number"]:
            analysis["suspicious_patterns"].append("round_number_amount")
        
        if analysis["is_large_amount"]:
            analysis["suspicious_patterns"].append("large_amount")
        
        if analysis["is_exact_amount"]:
            analysis["suspicious_patterns"].append("exact_amount")
        
        return analysis
    
    def _analyze_timing_patterns(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze timing patterns."""
        timestamp = transaction_data.get("timestamp")
        
        analysis = {
            "timestamp": timestamp,
            "is_unusual_hour": False,
            "is_weekend": False,
            "is_holiday": False,
            "suspicious_patterns": []
        }
        
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = timestamp
                
                # Check for unusual hours
                hour = dt.hour
                if hour < 6 or hour > 22:
                    analysis["is_unusual_hour"] = True
                    analysis["suspicious_patterns"].append("unusual_hour")
                
                # Check for weekend
                if dt.weekday() >= 5:
                    analysis["is_weekend"] = True
                    analysis["suspicious_patterns"].append("weekend_transaction")
                
                # Check for holidays (simplified)
                if dt.month == 12 and dt.day in [24, 25, 31]:
                    analysis["is_holiday"] = True
                    analysis["suspicious_patterns"].append("holiday_transaction")
                
            except Exception as e:
                logger.warning(f"Error analyzing timing patterns: {str(e)}")
        
        return analysis
    
    def _analyze_frequency_patterns(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze frequency patterns."""
        # This would typically analyze historical transaction data
        # For now, return basic analysis
        return {
            "transaction_count": transaction_data.get("transaction_count", 1),
            "frequency_score": 0.0,
            "suspicious_patterns": []
        }
    
    def _analyze_location_patterns(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze location patterns."""
        location = transaction_data.get("location", "")
        
        analysis = {
            "location": location,
            "is_unusual_location": "unusual" in location.lower(),
            "is_offshore": "offshore" in location.lower(),
            "suspicious_patterns": []
        }
        
        if analysis["is_unusual_location"]:
            analysis["suspicious_patterns"].append("unusual_location")
        
        if analysis["is_offshore"]:
            analysis["suspicious_patterns"].append("offshore_location")
        
        return analysis
    
    def _calculate_behavioral_risk(self, analysis: Dict[str, Any]) -> float:
        """Calculate behavioral risk score."""
        risk_score = 0.0
        
        # Amount risk
        amount_patterns = analysis["amount_analysis"]["suspicious_patterns"]
        risk_score += len(amount_patterns) * 0.1
        
        # Timing risk
        timing_patterns = analysis["timing_analysis"]["suspicious_patterns"]
        risk_score += len(timing_patterns) * 0.1
        
        # Location risk
        location_patterns = analysis["location_analysis"]["suspicious_patterns"]
        risk_score += len(location_patterns) * 0.1
        
        return min(risk_score, 1.0)

class EnhancedFraudDetector:
    """Enhanced fraud detector integrating BDH architecture with traditional methods."""
    
    def __init__(self, config: FraudDetectionConfig = None):
        self.config = config or FraudDetectionConfig()
        self.pattern_detector = FraudPatternDetector(config)
        self.behavioral_analyzer = BehavioralAnalyzer(config)
        
    def detect_fraud(self, 
                    document_text: str,
                    transaction_data: Optional[Dict[str, Any]] = None,
                    bdh_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive fraud detection using multiple methods.
        
        Args:
            document_text: Document text to analyze
            transaction_data: Optional transaction data
            bdh_analysis: Optional BDH analysis results
            
        Returns:
            Comprehensive fraud detection results
        """
        try:
            # Initialize results
            fraud_detection = {
                "timestamp": datetime.now().isoformat(),
                "pattern_analysis": {},
                "behavioral_analysis": {},
                "bdh_analysis": bdh_analysis,
                "combined_risk_score": 0.0,
                "fraud_probability": 0.0,
                "risk_level": "low",
                "fraud_indicators": [],
                "recommendations": []
            }
            
            # Pattern-based detection
            if self.config.enable_pattern_detection:
                fraud_detection["pattern_analysis"] = self.pattern_detector.detect_patterns(document_text)
            
            # Behavioral analysis
            if self.config.enable_behavioral_analysis and transaction_data:
                fraud_detection["behavioral_analysis"] = self.behavioral_analyzer.analyze_transaction_behavior(transaction_data)
            
            # Combine all analyses
            fraud_detection["combined_risk_score"] = self._calculate_combined_risk_score(fraud_detection)
            fraud_detection["fraud_probability"] = fraud_detection["combined_risk_score"]
            fraud_detection["risk_level"] = self._determine_risk_level(fraud_detection["combined_risk_score"])
            fraud_detection["fraud_indicators"] = self._extract_fraud_indicators(fraud_detection)
            fraud_detection["recommendations"] = self._generate_recommendations(fraud_detection)
            
            return fraud_detection
            
        except Exception as e:
            logger.error(f"Error in fraud detection: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "fraud_probability": 0.5,  # Default medium risk on error
                "risk_level": "unknown"
            }
    
    def _calculate_combined_risk_score(self, fraud_detection: Dict[str, Any]) -> float:
        """Calculate combined risk score from all analyses."""
        risk_score = 0.0
        
        # Pattern analysis risk
        if "pattern_analysis" in fraud_detection and fraud_detection["pattern_analysis"]:
            pattern_risk = fraud_detection["pattern_analysis"].get("overall_risk_score", 0.0)
            risk_score += pattern_risk * 0.4
        
        # Behavioral analysis risk
        if "behavioral_analysis" in fraud_detection and fraud_detection["behavioral_analysis"]:
            behavioral_risk = fraud_detection["behavioral_analysis"].get("behavioral_risk_score", 0.0)
            risk_score += behavioral_risk * 0.3
        
        # BDH analysis risk
        if "bdh_analysis" in fraud_detection and fraud_detection["bdh_analysis"]:
            bdh_risk = fraud_detection["bdh_analysis"].get("fraud_probability", 0.0)
            risk_score += bdh_risk * 0.3
        
        return min(risk_score, 1.0)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score."""
        if risk_score >= self.config.risk_threshold_high:
            return "high"
        elif risk_score >= self.config.risk_threshold_medium:
            return "medium"
        elif risk_score >= self.config.risk_threshold_low:
            return "low"
        else:
            return "minimal"
    
    def _extract_fraud_indicators(self, fraud_detection: Dict[str, Any]) -> List[str]:
        """Extract fraud indicators from all analyses."""
        indicators = []
        
        # Pattern-based indicators
        if "pattern_analysis" in fraud_detection:
            pattern_analysis = fraud_detection["pattern_analysis"]
            for category, patterns in pattern_analysis.items():
                if isinstance(patterns, list) and patterns:
                    indicators.extend([f"{category}_{pattern}" for pattern in patterns])
        
        # Behavioral indicators
        if "behavioral_analysis" in fraud_detection:
            behavioral_analysis = fraud_detection["behavioral_analysis"]
            for analysis_type, analysis_data in behavioral_analysis.items():
                if isinstance(analysis_data, dict) and "suspicious_patterns" in analysis_data:
                    indicators.extend([f"{analysis_type}_{pattern}" for pattern in analysis_data["suspicious_patterns"]])
        
        # BDH indicators
        if "bdh_analysis" in fraud_detection and fraud_detection["bdh_analysis"]:
            bdh_analysis = fraud_detection["bdh_analysis"]
            if "risk_level" in bdh_analysis:
                indicators.append(f"bdh_risk_{bdh_analysis['risk_level']}")
        
        return list(set(indicators))  # Remove duplicates
    
    def _generate_recommendations(self, fraud_detection: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on fraud detection results."""
        recommendations = []
        risk_level = fraud_detection.get("risk_level", "low")
        fraud_probability = fraud_detection.get("fraud_probability", 0.0)
        
        # Risk-based recommendations
        if risk_level == "high" or fraud_probability > 0.8:
            recommendations.extend([
                "Immediate manual review required",
                "Consider freezing account temporarily",
                "Contact customer for verification",
                "Escalate to fraud investigation team",
                "Enhanced monitoring required"
            ])
        elif risk_level == "medium" or fraud_probability > 0.5:
            recommendations.extend([
                "Manual review recommended",
                "Request additional documentation",
                "Enhanced verification procedures",
                "Monitor account for suspicious activity",
                "Consider enhanced due diligence"
            ])
        elif risk_level == "low" or fraud_probability > 0.3:
            recommendations.extend([
                "Standard processing recommended",
                "Continue routine monitoring",
                "Document analysis for future reference",
                "Consider periodic review"
            ])
        else:
            recommendations.extend([
                "Low risk - standard processing",
                "Continue routine monitoring"
            ])
        
        # Specific recommendations based on indicators
        indicators = fraud_detection.get("fraud_indicators", [])
        
        if any("wire_transfer" in indicator for indicator in indicators):
            recommendations.append("Verify wire transfer details with customer")
        
        if any("bitcoin" in indicator or "cryptocurrency" in indicator for indicator in indicators):
            recommendations.append("Enhanced verification required for cryptocurrency transactions")
        
        if any("offshore" in indicator for indicator in indicators):
            recommendations.append("Review offshore transaction compliance requirements")
        
        return recommendations

# Integration functions
def create_fraud_detector(config: FraudDetectionConfig = None) -> EnhancedFraudDetector:
    """Create enhanced fraud detector instance."""
    return EnhancedFraudDetector(config)

def detect_fraud_in_document(document_text: str, 
                           transaction_data: Optional[Dict[str, Any]] = None,
                           bdh_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Detect fraud in document using enhanced detection system."""
    detector = create_fraud_detector()
    return detector.detect_fraud(document_text, transaction_data, bdh_analysis)

# Example usage
if __name__ == "__main__":
    # Test fraud detection
    detector = create_fraud_detector()
    
    # Sample document text
    sample_text = """
    Payment shall be made within 30 days of invoice date. 
    Late payments subject to 1.5% monthly interest.
    Wire transfer to offshore account required for immediate processing.
    """
    
    # Sample transaction data
    sample_transaction = {
        "amount": 100000,
        "timestamp": "2024-01-01T02:00:00Z",
        "location": "offshore account"
    }
    
    # Detect fraud
    fraud_results = detector.detect_fraud(sample_text, sample_transaction)
    
    print("Fraud Detection Results:")
    print(f"Risk Level: {fraud_results['risk_level']}")
    print(f"Fraud Probability: {fraud_results['fraud_probability']:.3f}")
    print(f"Fraud Indicators: {fraud_results['fraud_indicators']}")
    print(f"Recommendations: {fraud_results['recommendations']}")
    
    print("\nEnhanced fraud detection test completed successfully!")
