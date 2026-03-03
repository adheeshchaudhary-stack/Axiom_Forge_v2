import hashlib
import magic
import logging
from typing import Dict, Tuple, Optional

def calculate_file_hashes(data: bytes) -> Dict[str, str]:
    """
    Calculate MD5 and SHA-256 hashes of file data.
    
    Args:
        data (bytes): File content as bytes
        
    Returns:
        Dict[str, str]: Dictionary containing hash values
    """
    try:
        md5_hash = hashlib.md5(data).hexdigest()
        sha256_hash = hashlib.sha256(data).hexdigest()
        
        return {
            'md5': md5_hash,
            'sha256': sha256_hash
        }
    except Exception as e:
        logging.error(f"Error calculating file hashes: {e}")
        return {'md5': 'Error', 'sha256': 'Error'}

def get_file_type(data: bytes) -> Dict[str, str]:
    """
    Identify file type using Magic Byte analysis.
    
    Args:
        data (bytes): File content as bytes
        
    Returns:
        Dict[str, str]: Dictionary containing file type information
    """
    try:
        # Get MIME type
        mime_type = magic.from_buffer(data, mime=True)
        
        # Get human-readable description
        file_description = magic.from_buffer(data)
        
        return {
            'mime_type': mime_type,
            'description': file_description
        }
    except Exception as e:
        logging.error(f"Error identifying file type: {e}")
        return {'mime_type': 'Unknown', 'description': 'Error'}

def analyze_file_metadata(file_path: str) -> Optional[Dict]:
    """
    Comprehensive file analysis including hashes and type identification.
    
    Args:
        file_path (str): Path to the file to analyze
        
    Returns:
        Optional[Dict]: File metadata or None if analysis fails
    """
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Get file size
        file_size = len(file_data)
        
        # Calculate hashes
        hashes = calculate_file_hashes(file_data)
        
        # Get file type
        file_type = get_file_type(file_data)
        
        return {
            'path': file_path,
            'size': file_size,
            'hashes': hashes,
            'type': file_type
        }
    except Exception as e:
        logging.error(f"Error analyzing file {file_path}: {e}")
        return None