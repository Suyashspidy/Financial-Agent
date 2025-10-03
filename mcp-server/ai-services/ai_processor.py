"""
AI Processor Service
Core AI processing engine for financial document analysis.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
import json
import re

import numpy as np
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class AIProcessor:
    """AI processing engine for financial document analysis."""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.named_entity_recognizer = None
        self.text_classifier = None
        self.anomaly_detector = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize AI models for processing."""
        try:
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Initialize NER for financial entities
            self.named_entity_recognizer = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            
            # Initialize text classification for document types
            self.text_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium"
            )
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize some AI models: {str(e)}")
    
    async def analyze_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis on document data.
        
        Args:
            document_data: Converted document data
            
        Returns:
            Dict containing analysis results
        """
        try:
            analysis_results = {
                "document_id": document_data.get("document_id"),
                "analysis_timestamp": pd.Timestamp.now().isoformat(),
                "document_type": document_data.get("document_type"),
                "processing_status": "completed"
            }
            
            # Extract text for analysis
            text_content = await self._extract_text_content(document_data)
            
            if text_content:
                # Perform various AI analyses
                analysis_results.update({
                    "sentiment_analysis": await self._analyze_sentiment(text_content),
                    "entity_extraction": await self._extract_entities(text_content),
                    "document_classification": await self._classify_document(text_content),
                    "anomaly_detection": await self._detect_anomalies(document_data),
                    "risk_indicators": await self._identify_risk_indicators(text_content),
                    "compliance_check": await self._check_compliance(text_content),
                    "text_analysis": await self._analyze_text_patterns(text_content)
                })
            
            # Analyze structured data if available
            if "structured_data" in document_data:
                analysis_results["structured_analysis"] = await self._analyze_structured_data(
                    document_data["structured_data"]
                )
            
            # Calculate overall risk score
            analysis_results["overall_risk_score"] = await self._calculate_overall_risk(analysis_results)
            
            logger.info(f"Document analysis completed: {document_data.get('document_id')}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise
    
    async def _extract_text_content(self, document_data: Dict[str, Any]) -> str:
        """Extract text content from document data."""
        text_content = ""
        
        if document_data.get("document_type") == "pdf":
            text_content = document_data.get("full_text", "")
        elif document_data.get("document_type") == "csv":
            # Convert CSV records to text
            records = document_data.get("records", [])
            text_content = " ".join([str(record) for record in records])
        elif document_data.get("document_type") == "excel":
            # Convert Excel sheets to text
            sheets = document_data.get("sheets", {})
            for sheet_name, sheet_data in sheets.items():
                records = sheet_data.get("records", [])
                text_content += f"Sheet {sheet_name}: " + " ".join([str(record) for record in records])
        elif document_data.get("document_type") == "json":
            text_content = json.dumps(document_data.get("data", {}))
        elif document_data.get("document_type") == "image_ocr":
            text_content = document_data.get("extracted_text", "")
        
        return text_content
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text content."""
        try:
            if not self.sentiment_analyzer or not text.strip():
                return {"sentiment": "neutral", "confidence": 0.0, "error": "No analyzer or empty text"}
            
            # Split text into chunks for processing
            chunks = [text[i:i+512] for i in range(0, len(text), 512)]
            sentiments = []
            
            for chunk in chunks:
                if chunk.strip():
                    result = self.sentiment_analyzer(chunk)
                    sentiments.append(result[0])
            
            # Aggregate sentiments
            if sentiments:
                avg_confidence = np.mean([s["score"] for s in sentiments])
                most_common_label = max(set([s["label"] for s in sentiments]), 
                                      key=[s["label"] for s in sentiments].count)
                
                return {
                    "sentiment": most_common_label.lower(),
                    "confidence": float(avg_confidence),
                    "sentiment_distribution": {
                        s["label"]: len([x for x in sentiments if x["label"] == s["label"]])
                        for s in sentiments
                    }
                }
            
            return {"sentiment": "neutral", "confidence": 0.0}
            
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.0, "error": str(e)}
    
    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text."""
        try:
            if not self.named_entity_recognizer or not text.strip():
                return {"entities": [], "error": "No NER model or empty text"}
            
            # Process text in chunks
            chunks = [text[i:i+512] for i in range(0, len(text), 512)]
            all_entities = []
            
            for chunk in chunks:
                if chunk.strip():
                    entities = self.named_entity_recognizer(chunk)
                    all_entities.extend(entities)
            
            # Group entities by type
            entity_groups = {}
            for entity in all_entities:
                entity_type = entity["entity_group"]
                if entity_type not in entity_groups:
                    entity_groups[entity_type] = []
                entity_groups[entity_type].append({
                    "text": entity["word"],
                    "confidence": entity["score"]
                })
            
            return {
                "entities": all_entities,
                "entity_groups": entity_groups,
                "total_entities": len(all_entities)
            }
            
        except Exception as e:
            logger.warning(f"Entity extraction failed: {str(e)}")
            return {"entities": [], "error": str(e)}
    
    async def _classify_document(self, text: str) -> Dict[str, Any]:
        """Classify document type and content."""
        try:
            # Financial document classification patterns
            patterns = {
                "bank_statement": [r"account\s+balance", r"transaction\s+history", r"statement\s+period"],
                "invoice": [r"invoice\s+number", r"amount\s+due", r"payment\s+terms"],
                "receipt": [r"receipt\s+number", r"total\s+amount", r"date\s+of\s+purchase"],
                "contract": [r"agreement", r"terms\s+and\s+conditions", r"signature"],
                "tax_document": [r"tax\s+id", r"filing\s+status", r"deductions"],
                "loan_application": [r"loan\s+amount", r"interest\s+rate", r"repayment\s+terms"]
            }
            
            document_type_scores = {}
            for doc_type, pattern_list in patterns.items():
                score = 0
                for pattern in pattern_list:
                    matches = len(re.findall(pattern, text.lower()))
                    score += matches
                document_type_scores[doc_type] = score
            
            # Determine most likely document type
            most_likely_type = max(document_type_scores, key=document_type_scores.get)
            confidence = document_type_scores[most_likely_type] / max(sum(document_type_scores.values()), 1)
            
            return {
                "document_type": most_likely_type,
                "confidence": confidence,
                "type_scores": document_type_scores
            }
            
        except Exception as e:
            logger.warning(f"Document classification failed: {str(e)}")
            return {"document_type": "unknown", "confidence": 0.0, "error": str(e)}
    
    async def _detect_anomalies(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in document data."""
        try:
            anomalies = []
            
            # Check for suspicious patterns in text
            text_content = await self._extract_text_content(document_data)
            
            # Detect unusual amounts
            amounts = re.findall(r'\$[\d,]+\.?\d*', text_content)
            if amounts:
                amount_values = [float(amount.replace('$', '').replace(',', '')) for amount in amounts]
                if amount_values:
                    mean_amount = np.mean(amount_values)
                    std_amount = np.std(amount_values)
                    
                    for amount in amount_values:
                        if abs(amount - mean_amount) > 3 * std_amount:
                            anomalies.append({
                                "type": "unusual_amount",
                                "value": amount,
                                "severity": "high" if abs(amount - mean_amount) > 5 * std_amount else "medium"
                            })
            
            # Detect unusual dates
            dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text_content)
            if len(dates) > 10:  # Suspicious number of dates
                anomalies.append({
                    "type": "excessive_dates",
                    "count": len(dates),
                    "severity": "medium"
                })
            
            # Detect suspicious keywords
            suspicious_keywords = ["urgent", "immediate", "confidential", "wire transfer", "bitcoin"]
            for keyword in suspicious_keywords:
                if keyword.lower() in text_content.lower():
                    anomalies.append({
                        "type": "suspicious_keyword",
                        "keyword": keyword,
                        "severity": "medium"
                    })
            
            return {
                "anomalies": anomalies,
                "anomaly_count": len(anomalies),
                "risk_level": "high" if len(anomalies) > 5 else "medium" if len(anomalies) > 2 else "low"
            }
            
        except Exception as e:
            logger.warning(f"Anomaly detection failed: {str(e)}")
            return {"anomalies": [], "error": str(e)}
    
    async def _identify_risk_indicators(self, text: str) -> Dict[str, Any]:
        """Identify risk indicators in the text."""
        risk_indicators = {
            "high_risk": [],
            "medium_risk": [],
            "low_risk": []
        }
        
        # High-risk indicators
        high_risk_patterns = [
            r"wire\s+transfer", r"bitcoin", r"cryptocurrency", r"offshore",
            r"shell\s+company", r"money\s+laundering", r"tax\s+evasion"
        ]
        
        # Medium-risk indicators
        medium_risk_patterns = [
            r"urgent", r"immediate", r"confidential", r"private",
            r"unusual\s+activity", r"suspicious", r"irregular"
        ]
        
        # Low-risk indicators
        low_risk_patterns = [
            r"routine", r"standard", r"normal", r"regular"
        ]
        
        for pattern in high_risk_patterns:
            if re.search(pattern, text.lower()):
                risk_indicators["high_risk"].append(pattern)
        
        for pattern in medium_risk_patterns:
            if re.search(pattern, text.lower()):
                risk_indicators["medium_risk"].append(pattern)
        
        for pattern in low_risk_patterns:
            if re.search(pattern, text.lower()):
                risk_indicators["low_risk"].append(pattern)
        
        return risk_indicators
    
    async def _check_compliance(self, text: str) -> Dict[str, Any]:
        """Check compliance with financial regulations."""
        compliance_checks = {
            "aml_compliance": False,
            "kyc_compliance": False,
            "tax_compliance": False,
            "regulatory_compliance": False,
            "issues": []
        }
        
        # AML (Anti-Money Laundering) checks
        aml_keywords = ["source of funds", "beneficial owner", "transaction purpose"]
        if any(keyword in text.lower() for keyword in aml_keywords):
            compliance_checks["aml_compliance"] = True
        else:
            compliance_checks["issues"].append("Missing AML documentation")
        
        # KYC (Know Your Customer) checks
        kyc_keywords = ["identification", "address verification", "customer due diligence"]
        if any(keyword in text.lower() for keyword in kyc_keywords):
            compliance_checks["kyc_compliance"] = True
        else:
            compliance_checks["issues"].append("Missing KYC documentation")
        
        # Tax compliance checks
        tax_keywords = ["tax id", "filing status", "deductions", "income"]
        if any(keyword in text.lower() for keyword in tax_keywords):
            compliance_checks["tax_compliance"] = True
        
        return compliance_checks
    
    async def _analyze_text_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze text patterns and linguistic features."""
        patterns = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "sentence_count": len(re.findall(r'[.!?]+', text)),
            "average_word_length": np.mean([len(word) for word in text.split()]) if text.split() else 0,
            "readability_score": 0,  # Could implement Flesch-Kincaid or similar
            "language_complexity": "medium"  # Could implement more sophisticated analysis
        }
        
        return patterns
    
    async def _analyze_structured_data(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze structured data patterns."""
        analysis = {
            "data_quality": "good",
            "completeness_score": 0.0,
            "consistency_score": 0.0,
            "issues": []
        }
        
        # Analyze dates
        if "dates" in structured_data:
            dates = structured_data["dates"]
            if len(dates) > 0:
                analysis["date_analysis"] = {
                    "count": len(dates),
                    "date_range": f"{min(dates)} to {max(dates)}" if len(dates) > 1 else dates[0]
                }
        
        # Analyze amounts
        if "amounts" in structured_data:
            amounts = structured_data["amounts"]
            if len(amounts) > 0:
                amount_values = [float(amount.replace('$', '').replace(',', '')) for amount in amounts]
                analysis["amount_analysis"] = {
                    "count": len(amounts),
                    "total": sum(amount_values),
                    "average": np.mean(amount_values),
                    "max": max(amount_values),
                    "min": min(amount_values)
                }
        
        return analysis
    
    async def _calculate_overall_risk(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall risk score based on all analyses."""
        risk_score = 0.0
        
        # Sentiment risk
        sentiment = analysis_results.get("sentiment_analysis", {})
        if sentiment.get("sentiment") == "negative":
            risk_score += 0.2
        
        # Anomaly risk
        anomalies = analysis_results.get("anomaly_detection", {})
        anomaly_count = anomalies.get("anomaly_count", 0)
        risk_score += min(anomaly_count * 0.1, 0.3)
        
        # Risk indicators
        risk_indicators = analysis_results.get("risk_indicators", {})
        high_risk_count = len(risk_indicators.get("high_risk", []))
        medium_risk_count = len(risk_indicators.get("medium_risk", []))
        risk_score += high_risk_count * 0.15 + medium_risk_count * 0.05
        
        # Compliance issues
        compliance = analysis_results.get("compliance_check", {})
        compliance_issues = len(compliance.get("issues", []))
        risk_score += compliance_issues * 0.1
        
        return min(risk_score, 1.0)  # Cap at 1.0
    
    async def get_analysis_results(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis results for a document."""
        # In production, this would query a database
        # For now, return None as we don't have persistent storage
        return None
