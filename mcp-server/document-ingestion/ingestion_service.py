"""
Document Ingestion Service
Handles incoming financial documents and manages their processing pipeline.
"""

import asyncio
import hashlib
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import aiofiles
from fastapi import UploadFile
import pandas as pd

logger = logging.getLogger(__name__)

class DocumentIngestionService:
    """Service for ingesting and managing financial documents."""
    
    def __init__(self, storage_path: str = "storage/documents"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_db = {}  # In production, use a proper database
        
    async def process_document(self, file: UploadFile) -> str:
        """
        Process an uploaded document and store it with metadata.
        
        Args:
            file: Uploaded file object
            
        Returns:
            str: Unique document ID
        """
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Create document directory
            doc_dir = self.storage_path / document_id
            doc_dir.mkdir(exist_ok=True)
            
            # Save original file
            file_path = doc_dir / f"original_{file.filename}"
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Calculate file hash for integrity
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Extract metadata
            metadata = await self._extract_metadata(file, content, file_hash)
            
            # Store metadata
            self.metadata_db[document_id] = {
                "document_id": document_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": len(content),
                "file_hash": file_hash,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "status": "uploaded",
                "metadata": metadata,
                "file_path": str(file_path)
            }
            
            logger.info(f"Document {document_id} processed successfully")
            return document_id
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def _extract_metadata(self, file: UploadFile, content: bytes, file_hash: str) -> Dict[str, Any]:
        """Extract metadata from the uploaded file."""
        metadata = {
            "original_filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content),
            "file_hash": file_hash,
            "upload_timestamp": datetime.utcnow().isoformat()
        }
        
        # Add content-specific metadata based on file type
        if file.content_type == "application/pdf":
            metadata.update(await self._extract_pdf_metadata(content))
        elif file.content_type == "text/csv":
            metadata.update(await self._extract_csv_metadata(content))
        elif "excel" in file.content_type:
            metadata.update(await self._extract_excel_metadata(content))
        
        return metadata
    
    async def _extract_pdf_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extract metadata from PDF files."""
        try:
            import PyPDF2
            from io import BytesIO
            
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            metadata = {
                "page_count": len(pdf_reader.pages),
                "pdf_info": pdf_reader.metadata or {},
                "is_encrypted": pdf_reader.is_encrypted
            }
            
            # Extract text preview (first 500 characters)
            if pdf_reader.pages:
                first_page_text = pdf_reader.pages[0].extract_text()
                metadata["text_preview"] = first_page_text[:500]
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Could not extract PDF metadata: {str(e)}")
            return {"pdf_extraction_error": str(e)}
    
    async def _extract_csv_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extract metadata from CSV files."""
        try:
            from io import StringIO
            
            csv_content = content.decode('utf-8')
            df = pd.read_csv(StringIO(csv_content))
            
            metadata = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "data_types": df.dtypes.to_dict()
            }
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Could not extract CSV metadata: {str(e)}")
            return {"csv_extraction_error": str(e)}
    
    async def _extract_excel_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extract metadata from Excel files."""
        try:
            from io import BytesIO
            
            excel_file = BytesIO(content)
            df = pd.read_excel(excel_file)
            
            metadata = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "data_types": df.dtypes.to_dict()
            }
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Could not extract Excel metadata: {str(e)}")
            return {"excel_extraction_error": str(e)}
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document metadata and data."""
        if document_id not in self.metadata_db:
            return None
        
        metadata = self.metadata_db[document_id].copy()
        
        # Load file content if needed
        file_path = metadata["file_path"]
        if os.path.exists(file_path):
            async with aiofiles.open(file_path, 'rb') as f:
                metadata["content"] = await f.read()
        
        return metadata
    
    async def list_documents(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all documents with pagination."""
        documents = list(self.metadata_db.values())
        return documents[offset:offset + limit]
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated files."""
        try:
            if document_id not in self.metadata_db:
                return False
            
            metadata = self.metadata_db[document_id]
            file_path = metadata["file_path"]
            
            # Delete file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete directory if empty
            doc_dir = Path(file_path).parent
            if doc_dir.exists() and not any(doc_dir.iterdir()):
                doc_dir.rmdir()
            
            # Remove from metadata
            del self.metadata_db[document_id]
            
            logger.info(f"Document {document_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    async def update_document_status(self, document_id: str, status: str) -> bool:
        """Update the processing status of a document."""
        if document_id not in self.metadata_db:
            return False
        
        self.metadata_db[document_id]["status"] = status
        self.metadata_db[document_id]["last_updated"] = datetime.utcnow().isoformat()
        
        return True
