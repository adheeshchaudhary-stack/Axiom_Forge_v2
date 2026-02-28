import hashlib
import io
from typing import Dict, Any, Optional
from pypdf import PdfReader
from PIL import Image, ExifTags

def calculate_file_hashes(file_content: Any) -> Dict[str, str]:
    # FORCE TO BYTES: Essential fix for hashlib compatibility
    data = bytes(file_content)
    return {
        'md5': hashlib.md5(data).hexdigest(),
        'sha256': hashlib.sha256(data).hexdigest()
    }

def extract_pdf_metadata(file_content: Any) -> Dict[str, Any]:
    metadata = {'author': None, 'creator': None, 'creation_date': None, 'title': None, 'page_count': 0}
    try:
        data = bytes(file_content)
        pdf_reader = PdfReader(io.BytesIO(data))
        if pdf_reader.metadata:
            info = pdf_reader.metadata
            metadata['author'] = getattr(info, 'author', None)
            metadata['creator'] = getattr(info, 'creator', None)
            metadata['title'] = getattr(info, 'title', None)
        metadata['page_count'] = len(pdf_reader.pages)
    except Exception as e:
        metadata['error'] = f"PDF Error: {str(e)}"
    return metadata

def extract_image_metadata(file_content: Any) -> Dict[str, Any]:
    metadata = {'format': None, 'size': None, 'exif_data': {}}
    try:
        data = bytes(file_content)
        image = Image.open(io.BytesIO(data))
        metadata['format'] = image.format
        metadata['size'] = image.size
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                metadata['exif_data'][str(tag)] = str(value)
    except Exception as e:
        metadata['error'] = f"Image Error: {str(e)}"
    return metadata

def get_file_type(file_content: Any, file_name: str = "") -> str:
    data = bytes(file_content)
    if file_name.lower().endswith('.pdf') or data.startswith(b'%PDF'):
        return 'pdf'
    elif any(file_name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']) or data.startswith((b'\x89PNG', b'\xFF\xD8\xFF')):
        return 'image'
    return 'unknown'