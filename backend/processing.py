"""
Document processing module for loading and chunking documents.
Supports PDF, TXT, and MD files.
"""

import re
import os
from typing import List, Dict
from io import BytesIO
import pypdf


def clean_text(text: str) -> str:
    """Clean text by removing excessive whitespace and normalizing."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 characters per token."""
    return len(text) // 4


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Chunk text into overlapping windows based on token count.
    
    Args:
        text: Input text to chunk
        chunk_size: Target token count per chunk
        overlap: Token overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Estimate tokens and convert to character-based chunking
    # Approximate: 4 chars per token
    char_chunk_size = chunk_size * 4
    char_overlap = overlap * 4
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + char_chunk_size
        
        # If this is not the last chunk, try to break at sentence boundary
        if end < text_length:
            # Look for sentence endings within the last 200 chars
            sentence_end = max(
                text.rfind('.', start, end),
                text.rfind('!', start, end),
                text.rfind('?', start, end),
                text.rfind('\n', start, end)
            )
            
            if sentence_end > start + char_chunk_size // 2:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - char_overlap
        if start >= text_length:
            break
    
    return chunks


def load_pdf_from_path(file_path: str) -> str:
    """
    Load text from PDF file path.
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Extracted text content
    """
    try:
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        full_text = '\n\n'.join(text_parts)
        return clean_text(full_text)
    except Exception as e:
        raise ValueError(f"Error loading PDF {file_path}: {str(e)}")


def load_pdf(file_content: bytes, filename: str) -> str:
    """
    Load text from PDF file bytes.
    
    Args:
        file_content: PDF file bytes
        filename: Original filename
    
    Returns:
        Extracted text content
    """
    try:
        pdf_file = BytesIO(file_content)
        reader = pypdf.PdfReader(pdf_file)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        full_text = '\n\n'.join(text_parts)
        return clean_text(full_text)
    except Exception as e:
        raise ValueError(f"Error loading PDF {filename}: {str(e)}")


def load_text_file_from_path(file_path: str) -> str:
    """
    Load text from TXT or MD file path.
    
    Args:
        file_path: Path to text file
    
    Returns:
        Text content
    """
    try:
        # Try UTF-8 first, fallback to latin-1
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
        
        return clean_text(text)
    except Exception as e:
        raise ValueError(f"Error loading text file {file_path}: {str(e)}")


def load_text_file(file_content: bytes, filename: str) -> str:
    """
    Load text from TXT or MD file bytes.
    
    Args:
        file_content: File bytes
        filename: Original filename
    
    Returns:
        Text content
    """
    try:
        # Try UTF-8 first, fallback to latin-1
        try:
            text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            text = file_content.decode('latin-1')
        
        return clean_text(text)
    except Exception as e:
        raise ValueError(f"Error loading text file {filename}: {str(e)}")


def process_documents(uploaded_files: List) -> List[Dict]:
    """
    Process uploaded files and return chunked documents.
    Works with Gradio file objects (which are file paths as strings).
    
    Args:
        uploaded_files: List of file paths (strings) from Gradio
    
    Returns:
        List of dictionaries with 'text', 'source', and 'chunk_id' keys
    """
    all_chunks = []
    
    print(f"📄 Processing {len(uploaded_files)} uploaded files...")
    
    for file_path in uploaded_files:
        try:
            # Extract filename from path
            filename = os.path.basename(file_path)
            file_extension = filename.split('.')[-1].lower()
            
            print(f"🔄 Processing: {filename}")
            
            # Load document based on type
            if file_extension == 'pdf':
                text = load_pdf_from_path(file_path)
            elif file_extension in ['txt', 'md']:
                text = load_text_file_from_path(file_path)
            else:
                print(f"⚠️ Skipping unsupported file: {filename}")
                continue  # Skip unsupported files
            
            if not text:
                print(f"⚠️ No text extracted from: {filename}")
                continue
            
            # Chunk the text
            chunks = chunk_text(text, chunk_size=800, overlap=150)
            
            # Store chunks with metadata
            for idx, chunk in enumerate(chunks):
                all_chunks.append({
                    'text': chunk,
                    'source': filename,
                    'chunk_id': f"{filename}_chunk_{idx}",
                    'chunk_index': idx
                })
            
            print(f"✅ Created {len(chunks)} chunks from {filename}")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
            continue
    
    print(f"✅ Total chunks created: {len(all_chunks)}")
    return all_chunks


# Additional functions for local directory processing
def get_available_files(data_dir: str = "data") -> List[str]:
    """
    Get list of available files in the data directory.
    
    Args:
        data_dir: Directory path containing documents
    
    Returns:
        List of filenames
    """
    if not os.path.exists(data_dir):
        return []
    
    supported_extensions = {'.pdf', '.txt', '.md'}
    files = []
    
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            if ext.lower() in supported_extensions:
                files.append(filename)
    
    return sorted(files)


def process_documents_from_directory(data_dir: str = "data") -> List[Dict]:
    """
    Process all documents in the data directory and return chunked documents.
    
    Args:
        data_dir: Directory path containing documents
    
    Returns:
        List of dictionaries with 'text', 'source', and 'chunk_id' keys
    """
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory '{data_dir}' not found")
    
    all_chunks = []
    supported_extensions = {'.pdf', '.txt', '.md'}
    
    # Get all files in the data directory
    files = []
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            if ext.lower() in supported_extensions:
                files.append((filename, file_path))
    
    if not files:
        raise ValueError(f"No supported files found in '{data_dir}' directory")
    
    print(f"📄 Processing {len(files)} files from '{data_dir}' directory...")
    
    for filename, file_path in files:
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            
            # Load document based on type
            if file_extension == '.pdf':
                text = load_pdf_from_path(file_path)
                print(f"✅ Loaded PDF: {filename}")
            elif file_extension in ['.txt', '.md']:
                text = load_text_file_from_path(file_path)
                print(f"✅ Loaded text file: {filename}")
            else:
                continue  # Skip unsupported files
            
            if not text:
                print(f"⚠️ No text extracted from: {filename}")
                continue
            
            # Chunk the text
            chunks = chunk_text(text, chunk_size=800, overlap=150)
            
            # Store chunks with metadata
            for idx, chunk in enumerate(chunks):
                all_chunks.append({
                    'text': chunk,
                    'source': filename,
                    'chunk_id': f"{filename}_chunk_{idx}",
                    'chunk_index': idx
                })
            
            print(f"   → Created {len(chunks)} chunks")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            continue
    
    print(f"✅ Total chunks created: {len(all_chunks)}")
    return all_chunks