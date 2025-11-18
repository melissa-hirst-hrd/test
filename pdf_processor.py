"""
PDF processing utilities for extracting text from contract documents.
"""
import logging
from typing import Optional
from io import BytesIO
import PyPDF2
import pdfplumber

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Processor for extracting text from PDF files."""
    
    @staticmethod
    def extract_text_pypdf2(pdf_content: BytesIO) -> str:
        """
        Extract text from PDF using PyPDF2.
        
        Args:
            pdf_content: BytesIO object containing PDF content
            
        Returns:
            Extracted text as string
        """
        try:
            pdf_content.seek(0)
            reader = PyPDF2.PdfReader(pdf_content)
            text = ""
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            raise
    
    @staticmethod
    def extract_text_pdfplumber(pdf_content: BytesIO) -> str:
        """
        Extract text from PDF using pdfplumber (better for complex layouts).
        
        Args:
            pdf_content: BytesIO object containing PDF content
            
        Returns:
            Extracted text as string
        """
        try:
            pdf_content.seek(0)
            text = ""
            
            with pdfplumber.open(pdf_content) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            raise
    
    @staticmethod
    def extract_text(pdf_content: BytesIO, method: str = "pdfplumber") -> str:
        """
        Extract text from PDF using the specified method.
        
        Args:
            pdf_content: BytesIO object containing PDF content
            method: Extraction method ("pdfplumber" or "pypdf2")
            
        Returns:
            Extracted text as string
        """
        if method == "pdfplumber":
            try:
                return PDFProcessor.extract_text_pdfplumber(pdf_content)
            except Exception as e:
                logger.warning(f"pdfplumber failed, falling back to PyPDF2: {e}")
                return PDFProcessor.extract_text_pypdf2(pdf_content)
        elif method == "pypdf2":
            return PDFProcessor.extract_text_pypdf2(pdf_content)
        else:
            raise ValueError(f"Unknown extraction method: {method}")
    
    @staticmethod
    def get_pdf_info(pdf_content: BytesIO) -> dict:
        """
        Get PDF metadata and information.
        
        Args:
            pdf_content: BytesIO object containing PDF content
            
        Returns:
            Dictionary with PDF information
        """
        try:
            pdf_content.seek(0)
            reader = PyPDF2.PdfReader(pdf_content)
            
            info = {
                'num_pages': len(reader.pages),
                'metadata': {}
            }
            
            if reader.metadata:
                info['metadata'] = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': reader.metadata.get('/CreationDate', ''),
                }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info: {e}")
            return {'num_pages': 0, 'metadata': {}}
