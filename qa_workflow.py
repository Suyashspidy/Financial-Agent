"""
Q&A workflow module for Due Diligence Copilot
Handles natural language queries and provides answers with citations
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from document_extractor import DocumentExtractor
from document_ingestion import DocumentIngestionPipeline
from config import Config


class DueDiligenceQA:
    """Handles Q&A workflow for due diligence tasks"""
    
    def __init__(self, pipeline: DocumentIngestionPipeline):
        """
        Initialize QA workflow
        
        Args:
            pipeline: Document ingestion pipeline with indexed data
        """
        self.pipeline = pipeline
        self.extractor = DocumentExtractor()
        self.index_records = []
    
    def load_index(self):
        """Load the current index from pipeline or disk"""
        # Try to load from disk first
        self.index_records = self.pipeline.load_index_from_disk()
        
        # If no index on disk, scan directory
        if not self.index_records:
            print("No index found, scanning directory...")
            self.index_records = self.pipeline.scan_and_process_directory()
            if self.index_records:
                self.pipeline.save_index_to_disk(self.index_records)
        
        return len(self.index_records)
    
    def refresh_index(self) -> int:
        """
        Refresh the index by scanning for new/changed documents
        
        Returns:
            Number of records in updated index
        """
        print("Refreshing index...")
        self.index_records = self.pipeline.scan_and_process_directory()
        if self.index_records:
            self.pipeline.save_index_to_disk(self.index_records)
        return len(self.index_records)
    
    def search_documents(
        self,
        query: str,
        top_k: int = 5,
        doc_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search indexed documents for relevant content
        
        Args:
            query: Search query
            top_k: Number of results to return
            doc_filter: Optional document name to filter results
            
        Returns:
            List of relevant chunks with metadata
        """
        if not self.index_records:
            self.load_index()
        
        # Filter by document if specified
        search_records = self.index_records
        if doc_filter:
            search_records = [r for r in self.index_records if doc_filter.lower() in r["doc_name"].lower()]
        
        # Search using the pipeline's search method
        results = self.pipeline.search_index(query, search_records, top_k)
        
        return results
    
    def answer_question(
        self,
        question: str,
        doc_name: Optional[str] = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using the indexed documents
        
        Args:
            question: Natural language question
            doc_name: Optional specific document to query
            use_llm: Whether to use LLM for answer generation (requires parsed doc)
            
        Returns:
            Answer with citations
        """
        # Search for relevant chunks
        results = self.search_documents(question, top_k=8, doc_filter=doc_name)
        
        if not results:
            return {
                "question": question,
                "answer": "No relevant information found in the indexed documents.",
                "citations": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # If LLM answer requested and we have a specific document
        if use_llm and doc_name and results:
            doc_path = results[0]["doc_path"]
            try:
                # Use LandingAI ADE to generate detailed answer
                llm_answer = self.extractor.extract_and_answer(doc_path, question)
                return llm_answer
            except Exception as e:
                print(f"Warning: LLM answer failed, falling back to search results: {str(e)}")
        
        # Otherwise, return search results as answer
        answer_parts = []
        citations = []
        
        for idx, result in enumerate(results[:5]):
            answer_parts.append(f"[{idx+1}] {result['citation_text']}")
            citations.append({
                "citation_number": idx + 1,
                "doc_name": result["doc_name"],
                "page": result["page"],
                "chunk_index": result["chunk_index"],
                "text": result["citation_text"],
                "relevance_score": result.get("relevance_score", 0)
            })
        
        answer = "\n\n".join(answer_parts)
        
        return {
            "question": question,
            "answer": answer,
            "citations": citations,
            "timestamp": datetime.now().isoformat()
        }
    
    def find_contracts_with_clause(
        self,
        clause_type: str,
        date_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find contracts containing specific clause types
        
        Args:
            clause_type: Type of clause to search for (e.g., "indemnity", "termination")
            date_filter: Optional date filter (e.g., "today", "2025-01-03")
            
        Returns:
            List of matching documents with relevant excerpts
        """
        # Search for the clause type
        query = f"{clause_type} clause"
        results = self.search_documents(query, top_k=20)
        
        # Group by document
        docs_with_clause = {}
        for result in results:
            doc_name = result["doc_name"]
            if doc_name not in docs_with_clause:
                docs_with_clause[doc_name] = {
                    "doc_name": doc_name,
                    "doc_path": result["doc_path"],
                    "upload_timestamp": result["upload_timestamp"],
                    "matches": []
                }
            
            docs_with_clause[doc_name]["matches"].append({
                "page": result["page"],
                "text": result["citation_text"],
                "relevance": result.get("relevance_score", 0)
            })
        
        # Apply date filter if specified
        if date_filter:
            if date_filter.lower() == "today":
                today = datetime.now().date().isoformat()
                docs_with_clause = {
                    k: v for k, v in docs_with_clause.items()
                    if v["upload_timestamp"].startswith(today)
                }
            else:
                docs_with_clause = {
                    k: v for k, v in docs_with_clause.items()
                    if v["upload_timestamp"].startswith(date_filter)
                }
        
        return list(docs_with_clause.values())
    
    def flag_risks_in_documents(
        self,
        doc_filter: Optional[str] = None,
        risk_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Flag potential risks across documents
        
        Args:
            doc_filter: Optional document name filter
            risk_keywords: Optional list of risk keywords to check
            
        Returns:
            Dictionary with flagged risks by document
        """
        if not self.index_records:
            self.load_index()
        
        # Get unique documents
        docs = set(r["doc_path"] for r in self.index_records)
        if doc_filter:
            docs = {d for d in docs if doc_filter.lower() in Path(d).name.lower()}
        
        all_risks = {}
        
        for doc_path in docs:
            doc_name = Path(doc_path).name
            print(f"Scanning {doc_name} for risks...")
            
            try:
                risks = self.extractor.extract_risk_indicators(doc_path, risk_keywords)
                if risks:
                    all_risks[doc_name] = risks
            except Exception as e:
                print(f"Warning: Could not scan {doc_name}: {str(e)}")
        
        return {
            "total_documents_scanned": len(docs),
            "documents_with_risks": len(all_risks),
            "flagged_risks": all_risks,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_document_overview(self, doc_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get overview of indexed documents or a specific document
        
        Args:
            doc_name: Optional specific document name
            
        Returns:
            Overview information
        """
        if not self.index_records:
            self.load_index()
        
        if doc_name:
            return self.pipeline.get_document_summary(doc_name, self.index_records)
        
        # Get all documents overview
        unique_docs = {}
        for record in self.index_records:
            doc = record["doc_name"]
            if doc not in unique_docs:
                unique_docs[doc] = {
                    "doc_name": doc,
                    "chunk_count": 0,
                    "upload_timestamp": record["upload_timestamp"]
                }
            unique_docs[doc]["chunk_count"] += 1
        
        return {
            "total_documents": len(unique_docs),
            "total_chunks": len(self.index_records),
            "documents": list(unique_docs.values())
        }
    
    def ask_with_evidence(
        self,
        question: str,
        require_evidence: bool = True
    ) -> Dict[str, Any]:
        """
        Answer question and ensure evidence is provided
        
        Args:
            question: Natural language question
            require_evidence: Whether to require citations
            
        Returns:
            Answer with mandatory evidence citations
        """
        answer_data = self.answer_question(question)
        
        # Validate evidence is present
        if require_evidence and not answer_data.get("citations"):
            answer_data["warning"] = "No evidence/citations found for this answer"
        
        # Add evidence summary
        if answer_data.get("citations"):
            evidence_summary = []
            for cite in answer_data["citations"]:
                evidence_summary.append(
                    f"Document: {cite.get('doc_name', 'Unknown')}, "
                    f"Page: {cite.get('page', 'N/A')}"
                )
            answer_data["evidence_summary"] = evidence_summary
        
        return answer_data
