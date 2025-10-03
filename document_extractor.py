"""
Document extraction module using LandingAI ADE
Extracts structured fields, tables, and evidence from financial documents
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json

from landingai_ade import LandingAIADE
from landingai_ade.types import ParseResponse
from pydantic import BaseModel

from config import Config


class ExtractedData(BaseModel):
    """Schema for extracted document data"""
    doc_name: str
    doc_path: str
    field_name: str
    value: str
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    citation_text: Optional[str] = None
    score: Optional[float] = None
    upload_timestamp: str
    extraction_metadata: Dict[str, Any] = {}


class DocumentExtractor:
    """Handles document extraction using LandingAI ADE"""
    
    def __init__(self):
        """Initialize the document extractor"""
        Config.get_env_setup()
        self.client = LandingAIADE(apikey=Config.VISION_AGENT_API_KEY)
        self.model = Config.MODEL_NAME
    
    def parse_document(self, document_path: str) -> ParseResponse:
        """
        Parse a document using LandingAI ADE
        
        Args:
            document_path: Path to the document file
            
        Returns:
            ParseResponse object containing parsed content
        """
        if not Path(document_path).exists():
            raise FileNotFoundError(f"Document not found at {document_path}")
        
        response = self.client.parse(
            document_url=document_path,
            model=self.model
        )
        
        return response
    
    def extract_structured_data(
        self, 
        document_path: str,
        doc_name: Optional[str] = None
    ) -> List[ExtractedData]:
        """
        Extract structured data from a document with citations
        
        Args:
            document_path: Path to the document
            doc_name: Optional document name (defaults to filename)
            
        Returns:
            List of ExtractedData objects with fields, values, and citations
        """
        if doc_name is None:
            doc_name = Path(document_path).name
        
        # Parse the document
        parsed = self.parse_document(document_path)
        
        extracted_items = []
        timestamp = datetime.now().isoformat()
        
        # Extract data from chunks with metadata
        for idx, chunk in enumerate(parsed.chunks):
            # Create an entry for each chunk
            extracted_data = ExtractedData(
                doc_name=doc_name,
                doc_path=str(document_path),
                field_name=f"chunk_{idx}",
                value=chunk.text,
                page=getattr(chunk, 'page_index', None),
                chunk_index=idx,
                citation_text=chunk.text[:200] if len(chunk.text) > 200 else chunk.text,
                upload_timestamp=timestamp,
                extraction_metadata={
                    "chunk_type": getattr(chunk, 'type', 'text'),
                    "full_text_length": len(chunk.text)
                }
            )
            extracted_items.append(extracted_data)
        
        return extracted_items
    
    def answer_question(
        self,
        question: str,
        parsed_response: ParseResponse,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Answer a question based on parsed document content
        
        Args:
            question: Natural language question
            parsed_response: Previously parsed document
            top_k: Number of chunks to consider (default from config)
            
        Returns:
            Dictionary with answer and citations
        """
        if top_k is None:
            top_k = Config.TOP_K_CHUNKS
        
        answer_resp = self.client.answer(
            question=question,
            parsed=parsed_response,
            top_k=top_k,
            with_citations=True,
            with_spans=True
        )
        
        # Format the response with citations
        citations = []
        for cite in answer_resp.citations:
            citations.append({
                "page": getattr(cite, 'page_index', None),
                "score": cite.score if hasattr(cite, 'score') else None,
                "text": cite.text[:200] if len(cite.text) > 200 else cite.text,
                "full_text": cite.text
            })
        
        return {
            "question": question,
            "answer": answer_resp.answer_text,
            "citations": citations,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_and_answer(
        self,
        document_path: str,
        question: str,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        One-shot: Parse document and answer question
        
        Args:
            document_path: Path to document
            question: Question to answer
            top_k: Number of chunks to consider
            
        Returns:
            Answer with citations
        """
        parsed = self.parse_document(document_path)
        return self.answer_question(question, parsed, top_k)
    
    def extract_risk_indicators(
        self,
        document_path: str,
        risk_keywords: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract potential risk indicators from document
        
        Args:
            document_path: Path to document
            risk_keywords: List of keywords to flag (default: common risk terms)
            
        Returns:
            List of flagged risks with citations
        """
        if risk_keywords is None:
            risk_keywords = [
                "indemnity", "liability", "breach", "termination",
                "penalty", "default", "force majeure", "warranty",
                "compliance", "regulatory", "audit", "material adverse"
            ]
        
        parsed = self.parse_document(document_path)
        flagged_risks = []
        
        for keyword in risk_keywords:
            question = f"Are there any clauses related to {keyword}? If yes, provide the specific text."
            try:
                answer = self.answer_question(question, parsed, top_k=5)
                
                # Only include if there's actual content (not just "no" or empty)
                if answer["answer"] and len(answer["answer"]) > 10:
                    if not any(phrase in answer["answer"].lower() for phrase in ["no", "not found", "none"]):
                        flagged_risks.append({
                            "risk_type": keyword,
                            "answer": answer["answer"],
                            "citations": answer["citations"],
                            "document": Path(document_path).name
                        })
            except Exception as e:
                print(f"Warning: Could not check for {keyword}: {str(e)}")
                continue
        
        return flagged_risks
