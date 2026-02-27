import hashlib
import io
from datetime import datetime
from typing import Dict, Any, Optional

from pypdf import PdfReader
from PIL import Image, ExifTags


def calculate_file_hashes(file_content: bytes) -> Dict[str, str]:
    """
    Calculate MD5 and SHA-256 hashes of file content.
    
    Args:
        file_content: Bytes of the file content
        
    Returns:
        Dictionary containing MD5 and SHA-256 hashes
    """
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    md5_hash.update(file_content)
    sha256_hash.update(file_content)
    
    return {
        'md5': md5_hash.hexdigest(),
        'sha256': sha256_hash.hexdigest()
    }


def extract_pdf_metadata(file_content: bytes) -> Dict[str, Any]:
    """
    Extract metadata from PDF files.
    
    Args:
        file_content: Bytes of the PDF file content
        
    Returns:
        Dictionary containing PDF metadata
    """
    metadata = {
        'author': None,
        'creator': None,
        'creation_date': None,
        'modification_date': None,
        'title': None,
        'producer': None,
        'page_count': 0
    }
    
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        
        # Get document information
        if pdf_reader.metadata:
            info = pdf_reader.metadata
            
            metadata['author'] = getattr(info, 'author', None)
            metadata['creator'] = getattr(info, 'creator', None)
            metadata['title'] = getattr(info, 'title', None)
            metadata['producer'] = getattr(info, 'producer', None)
            
            # Handle dates
            creation_date = getattr(info, 'creation_date', None)
            if creation_date:
                metadata['creation_date'] = _format_pdf_date(creation_date)
            
            modification_date = getattr(info, 'modification_date', None)
            if modification_date:
                metadata['modification_date'] = _format_pdf_date(modification_date)
        
        metadata['page_count'] = len(pdf_reader.pages)
        
    except Exception as e:
        metadata['error'] = f"Error reading PDF metadata: {str(e)}"
    
    return metadata


def extract_image_metadata(file_content: bytes) -> Dict[str, Any]:
    """
    Extract EXIF metadata from image files.
    
    Args:
        file_content: Bytes of the image file content
        
    Returns:
        Dictionary containing image EXIF metadata
    """
    metadata = {
        'format': None,
        'size': None,
        'mode': None,
        'exif_data': {}
    }
    
    try:
        image = Image.open(io.BytesIO(file_content))
        
        metadata['format'] = image.format
        metadata['size'] = image.size
        metadata['mode'] = image.mode
        
        # Extract EXIF data
        exif_data = {}
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)
                    exif_data[tag] = value
        
        metadata['exif_data'] = exif_data
        
    except Exception as e:
        metadata['error'] = f"Error reading image metadata: {str(e)}"
    
    return metadata


def _format_pdf_date(pdf_date: Any) -> Optional[str]:
    """
    Format PDF date object to readable string.
    
    Args:
        pdf_date: PDF date object
        
    Returns:
        Formatted date string or None
    """
    try:
        if hasattr(pdf_date, 'strftime'):
            return pdf_date.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(pdf_date, str):
            # Handle PDF date strings like "D:20231201120000+00'00'"
            if pdf_date.startswith('D:'):
                date_str = pdf_date[2:16]  # Extract YYYYMMDDHHMMSS
                if len(date_str) >= 8:
                    year = date_str[:4]
                    month = date_str[4:6]
                    day = date_str[6:8]
                    hour = date_str[8:10] if len(date_str) >= 10 else '00'
                    minute = date_str[10:12] if len(date_str) >= 12 else '00'
                    second = date_str[12:14] if len(date_str) >= 14 else '00'
                    return f"{year}-{month}-{day} {hour}:{minute}:{second}"
        return str(pdf_date)
    except:
        return None


def get_file_type(file_content: bytes, file_name: str = "") -> str:
    """
    Determine file type based on content and extension.
    
    Args:
        file_content: Bytes of the file content
        file_name: Original file name (optional)
        
    Returns:
        String indicating file type: 'pdf', 'image', or 'unknown'
    """
    # Check file extension first
    if file_name.lower().endswith('.pdf'):
        return 'pdf'
    elif any(file_name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']):
        return 'image'
    
    # Check magic numbers/mime types
    if file_content.startswith(b'%PDF'):
        return 'pdf'
    elif file_content.startswith((b'\x89PNG', b'\xFF\xD8\xFF', b'GIF8', b'BM')):
        return 'image'
    
    return 'unknown'