"""
Document Conversion Service
Converts documents to standardized formats for AI processing.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json

import pandas as pd
import PyPDF2
import pytesseract
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class DocumentConversionService:
    """Service for converting documents to standardized formats."""
    
    def __init__(self):
        self.supported_formats = ["pdf", "csv", "excel", "json", "xml"]
        self.output_format = "json"  # Standardized output format
        
    async def convert_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a document to standardized format for AI processing.
        
        Args:
            document_data: Document metadata and content
            
        Returns:
            Dict containing converted document data
        """
        try:
            content_type = document_data.get("content_type", "")
            content = document_data.get("content", b"")
            
            # Determine conversion method based on content type
            if "pdf" in content_type:
                converted_data = await self._convert_pdf(content)
            elif "csv" in content_type:
                converted_data = await self._convert_csv(content)
            elif "excel" in content_type:
                converted_data = await self._convert_excel(content)
            elif "json" in content_type:
                converted_data = await self._convert_json(content)
            else:
                # Try OCR for image-based documents
                converted_data = await self._convert_with_ocr(content)
            
            # Add metadata
            converted_data.update({
                "original_format": content_type,
                "conversion_timestamp": pd.Timestamp.now().isoformat(),
                "document_id": document_data.get("document_id"),
                "conversion_method": self._get_conversion_method(content_type)
            })
            
            logger.info(f"Document converted successfully: {document_data.get('document_id')}")
            return converted_data
            
        except Exception as e:
            logger.error(f"Error converting document: {str(e)}")
            raise
    
    async def _convert_pdf(self, content: bytes) -> Dict[str, Any]:
        """Convert PDF to structured data."""
        try:
            from io import BytesIO
            
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            full_text = ""
            page_texts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    page_texts.append({
                        "page_number": page_num + 1,
                        "text": page_text,
                        "word_count": len(page_text.split())
                    })
                    full_text += page_text + "\n"
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                    page_texts.append({
                        "page_number": page_num + 1,
                        "text": "",
                        "error": str(e)
                    })
            
            # Try to extract structured data (tables, forms)
            structured_data = await self._extract_structured_data_from_text(full_text)
            
            return {
                "document_type": "pdf",
                "page_count": len(pdf_reader.pages),
                "full_text": full_text,
                "page_texts": page_texts,
                "structured_data": structured_data,
                "metadata": pdf_reader.metadata or {}
            }
            
        except Exception as e:
            logger.error(f"Error converting PDF: {str(e)}")
            raise
    
    async def _convert_csv(self, content: bytes) -> Dict[str, Any]:
        """Convert CSV to structured data."""
        try:
            from io import StringIO
            
            csv_content = content.decode('utf-8')
            df = pd.read_csv(StringIO(csv_content))
            
            # Convert to records format
            records = df.to_dict('records')
            
            # Analyze data patterns
            data_analysis = await self._analyze_tabular_data(df)
            
            return {
                "document_type": "csv",
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "data_types": df.dtypes.astype(str).to_dict(),
                "records": records,
                "data_analysis": data_analysis,
                "sample_data": df.head(10).to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error converting CSV: {str(e)}")
            raise
    
    async def _convert_excel(self, content: bytes) -> Dict[str, Any]:
        """Convert Excel to structured data."""
        try:
            from io import BytesIO
            
            excel_file = BytesIO(content)
            
            # Read all sheets
            excel_data = pd.read_excel(excel_file, sheet_name=None)
            
            converted_sheets = {}
            for sheet_name, df in excel_data.items():
                converted_sheets[sheet_name] = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": df.columns.tolist(),
                    "data_types": df.dtypes.astype(str).to_dict(),
                    "records": df.to_dict('records'),
                    "sample_data": df.head(10).to_dict('records')
                }
            
            return {
                "document_type": "excel",
                "sheet_count": len(excel_data),
                "sheets": converted_sheets,
                "sheet_names": list(excel_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Error converting Excel: {str(e)}")
            raise
    
    async def _convert_json(self, content: bytes) -> Dict[str, Any]:
        """Convert JSON to structured data."""
        try:
            json_content = content.decode('utf-8')
            data = json.loads(json_content)
            
            return {
                "document_type": "json",
                "data": data,
                "data_type": type(data).__name__,
                "size_estimate": len(json_content)
            }
            
        except Exception as e:
            logger.error(f"Error converting JSON: {str(e)}")
            raise
    
    async def _convert_with_ocr(self, content: bytes) -> Dict[str, Any]:
        """Convert image-based documents using OCR."""
        try:
            # Convert bytes to image
            nparr = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode image")
            
            # Preprocess image for better OCR
            processed_image = await self._preprocess_image_for_ocr(image)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(processed_image)
            
            # Try to extract structured data
            structured_data = await self._extract_structured_data_from_text(extracted_text)
            
            return {
                "document_type": "image_ocr",
                "extracted_text": extracted_text,
                "structured_data": structured_data,
                "ocr_confidence": "medium",  # Could be enhanced with confidence scores
                "image_dimensions": image.shape[:2]
            }
            
        except Exception as e:
            logger.error(f"Error with OCR conversion: {str(e)}")
            raise
    
    async def _preprocess_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image to improve OCR accuracy."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply thresholding
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    async def _extract_structured_data_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured data patterns from text."""
        import re
        
        structured_data = {
            "dates": re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text),
            "amounts": re.findall(r'\$[\d,]+\.?\d*', text),
            "account_numbers": re.findall(r'\b\d{4,}\b', text),
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            "phone_numbers": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        }
        
        # Clean up and deduplicate
        for key, values in structured_data.items():
            structured_data[key] = list(set(values))
        
        return structured_data
    
    async def _analyze_tabular_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze tabular data for patterns and anomalies."""
        analysis = {
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
            "date_columns": []
        }
        
        # Detect potential date columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].dropna().iloc[:5])
                    analysis["date_columns"].append(col)
                except:
                    pass
        
        return analysis
    
    def _get_conversion_method(self, content_type: str) -> str:
        """Get the conversion method used for the content type."""
        if "pdf" in content_type:
            return "pdf_text_extraction"
        elif "csv" in content_type:
            return "csv_parsing"
        elif "excel" in content_type:
            return "excel_parsing"
        elif "json" in content_type:
            return "json_parsing"
        else:
            return "ocr_extraction"
