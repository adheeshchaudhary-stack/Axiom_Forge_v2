import hashlib
import os
from typing import Dict, Any
from pypdf import PdfReader

def calculate_file_hashes(file_content: bytes) -> Dict[str, str]:
    """Calculate MD5 and SHA-256 hashes of file content."""
    # Ensure content is bytes
    if isinstance(file_content, bytearray):
        file_content = bytes(file_content)
    
    md5_hash = hashlib.md5(file_content).hexdigest()
    sha256_hash = hashlib.sha256(file_content).hexdigest()
    
    return {
        'md5': md5_hash,
        'sha256': sha256_hash
    }

def get_file_type(file_content: bytes, file_name: str) -> str:
    """Determine file type based on content and extension."""
    # Ensure content is bytes
    if isinstance(file_content, bytearray):
        file_content = bytes(file_content)
    
    # Check file extension first
    if file_name.lower().endswith('.pdf'):
        return 'PDF'
    elif file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        return 'Image'
    elif file_name.lower().endswith('.csv'):
        return 'CSV'
    elif file_name.lower().endswith('.txt'):
        return 'Text'
    
    # Fallback to magic numbers
    if file_content.startswith(b'%PDF'):
        return 'PDF'
    elif file_content.startswith(b'\x89PNG'):
        return 'Image'
    elif file_content.startswith(b'\xff\xd8\xff'):
        return 'Image'
    elif b',' in file_content[:100]:  # Simple CSV detection
        return 'CSV'
    
    return 'Unknown'

def extract_pdf_metadata(file_content: bytes) -> Dict[str, Any]:
    """Extract metadata from PDF files."""
    # Ensure content is bytes
    if isinstance(file_content, bytearray):
        file_content = bytes(file_content)
    
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        metadata = pdf_reader.metadata
        
        if metadata:
            return {
                'title': metadata.get('/Title', 'N/A'),
                'author': metadata.get('/Author', 'N/A'),
                'creator': metadata.get('/Creator', 'N/A'),
                'producer': metadata.get('/Producer', 'N/A'),
                'creation_date': metadata.get('/CreationDate', 'N/A'),
                'modification_date': metadata.get('/ModDate', 'N/A'),
                'pages': len(pdf_reader.pages)
            }
        else:
            return {'error': 'No metadata found'}
    except Exception as e:
        return {'error': f'Failed to extract PDF metadata: {str(e)}'}

def extract_image_metadata(file_content: bytes) -> Dict[str, Any]:
    """Extract metadata from image files."""
    # Ensure content is bytes
    if isinstance(file_content, bytearray):
        file_content = bytes(file_content)
    
    # Image metadata extraction not available (PIL not in approved libraries)
    return {'error': 'Image metadata extraction not available - PIL not in approved libraries'}

# Import required modules
import io