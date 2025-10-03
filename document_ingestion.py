"""
Document ingestion module using Pathway for live indexing
Monitors folder for new/changed files and triggers extraction
"""
import pathway as pw
from typing import List, Dict, Any
from pathlib import Path
import json
from datetime import datetime

from config import Config
from document_extractor import DocumentExtractor


class DocumentIndexSchema(pw.Schema):
    """Schema for document index in Pathway"""
    doc_name: str
    doc_path: str
    chunk_index: int
    content: str
    page: int
    citation_text: str
    upload_timestamp: str
    metadata: str  # JSON string of metadata


class DocumentIngestionPipeline:
    """Handles document ingestion and live indexing with Pathway"""
    
    def __init__(self):
        """Initialize the ingestion pipeline"""
        self.extractor = DocumentExtractor()
        self.docs_folder = Config.DOCS_FOLDER
        self.index_data = []
        self.processed_files = set()
    
    def process_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a single document and extract structured data
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of extracted data dictionaries
        """
        print(f"Processing document: {file_path.name}")
        
        try:
            # Extract structured data with citations
            extracted_items = self.extractor.extract_structured_data(
                str(file_path),
                doc_name=file_path.name
            )
            
            # Convert to dictionaries for indexing
            index_records = []
            for item in extracted_items:
                record = {
                    "doc_name": item.doc_name,
                    "doc_path": item.doc_path,
                    "chunk_index": item.chunk_index or 0,
                    "content": item.value,
                    "page": item.page or 0,
                    "citation_text": item.citation_text or "",
                    "upload_timestamp": item.upload_timestamp,
                    "metadata": json.dumps(item.extraction_metadata)
                }
                index_records.append(record)
            
            print(f"Extracted {len(index_records)} chunks from {file_path.name}")
            return index_records
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {str(e)}")
            return []
    
    def scan_and_process_directory(self) -> List[Dict[str, Any]]:
        """
        Scan directory for documents and process new/changed files
        
        Returns:
            List of all indexed records
        """
        print(f"Scanning directory: {self.docs_folder}")
        
        all_records = []
        
        # Get all PDF and DOCX files
        supported_extensions = ['.pdf', '.docx', '.doc']
        files = []
        for ext in supported_extensions:
            files.extend(self.docs_folder.glob(f"*{ext}"))
        
        if not files:
            print("No documents found in the directory")
            return all_records
        
        print(f"Found {len(files)} documents to process")
        
        for file_path in files:
            # Check if already processed (basic version - could use file hash for changes)
            if str(file_path) not in self.processed_files:
                records = self.process_document(file_path)
                all_records.extend(records)
                self.processed_files.add(str(file_path))
        
        return all_records
    
    def create_pathway_index(self, records: List[Dict[str, Any]]) -> pw.Table:
        """
        Create a Pathway table from extracted records
        
        Args:
            records: List of extracted data records
            
        Returns:
            Pathway Table with indexed data
        """
        if not records:
            print("No records to index")
            return None
        
        # Convert records to Pathway table
        table = pw.debug.table_from_rows(
            schema=DocumentIndexSchema,
            rows=[
                (
                    r["doc_name"],
                    r["doc_path"],
                    r["chunk_index"],
                    r["content"],
                    r["page"],
                    r["citation_text"],
                    r["upload_timestamp"],
                    r["metadata"]
                )
                for r in records
            ]
        )
        
        return table
    
    def search_index(
        self,
        query: str,
        records: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the index for relevant chunks (simple text matching)
        
        Args:
            query: Search query
            records: List of indexed records
            top_k: Number of top results to return
            
        Returns:
            List of relevant records with scores
        """
        query_lower = query.lower()
        results = []
        
        for record in records:
            content_lower = record["content"].lower()
            
            # Simple relevance score based on keyword matches
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in content_lower)
            
            if matches > 0:
                results.append({
                    **record,
                    "relevance_score": matches / len(query_words)
                })
        
        # Sort by relevance and return top K
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]
    
    def get_document_summary(
        self,
        doc_name: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a specific document
        
        Args:
            doc_name: Name of the document
            records: List of all indexed records
            
        Returns:
            Dictionary with document statistics
        """
        doc_records = [r for r in records if r["doc_name"] == doc_name]
        
        if not doc_records:
            return {"error": f"Document {doc_name} not found"}
        
        pages = set(r["page"] for r in doc_records)
        total_chunks = len(doc_records)
        total_chars = sum(len(r["content"]) for r in doc_records)
        
        return {
            "doc_name": doc_name,
            "total_chunks": total_chunks,
            "total_pages": len(pages),
            "total_characters": total_chars,
            "upload_timestamp": doc_records[0]["upload_timestamp"],
            "pages": sorted(list(pages))
        }
    
    def save_index_to_disk(self, records: List[Dict[str, Any]], filename: str = "index.json"):
        """
        Save the index to disk for persistence
        
        Args:
            records: List of indexed records
            filename: Name of the file to save
        """
        output_path = Config.INDEX_FOLDER / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_records": len(records),
                "records": records
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Index saved to {output_path}")
    
    def load_index_from_disk(self, filename: str = "index.json") -> List[Dict[str, Any]]:
        """
        Load index from disk
        
        Args:
            filename: Name of the file to load
            
        Returns:
            List of indexed records
        """
        input_path = Config.INDEX_FOLDER / filename
        
        if not input_path.exists():
            print(f"Index file not found: {input_path}")
            return []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {data['total_records']} records from {input_path}")
        return data["records"]
