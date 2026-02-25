"""
RAG engine module for embeddings and FAISS-based retrieval.
"""

import os
import warnings
from typing import List, Dict, Tuple
import numpy as np
import faiss
import pickle

# Suppress PyTorch internal warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch')

from sentence_transformers import SentenceTransformer


class RAGEngine:
    """In-memory RAG engine using FAISS for similarity search with persistence."""
    
    def __init__(self, index_path: str = "faiss_index"):
        """Initialize the RAG engine with embedding model."""
        self.model = None
        self.index = None
        self.chunks = []  # Store chunk texts and metadata
        self.dimension = 384  # MiniLM-L6-v2 embedding dimension
        self.index_path = index_path
        
        # Try to load existing index
        self._load_index()
    
    def _load_model(self):
        """Lazy load the embedding model."""
        if self.model is None:
            print("🔄 Loading embedding model...")
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("✅ Embedding model loaded")
    
    def _initialize_index(self):
        """Initialize FAISS index if not already created."""
        if self.index is None:
            self._load_model()
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def _save_index(self):
        """Save FAISS index and chunks to disk."""
        if self.index is not None and self.index.ntotal > 0:
            try:
                # Create directory if it doesn't exist
                os.makedirs(self.index_path, exist_ok=True)
                
                # Save FAISS index
                index_file = os.path.join(self.index_path, "index.faiss")
                faiss.write_index(self.index, index_file)
                
                # Save chunks metadata
                chunks_file = os.path.join(self.index_path, "chunks.pkl")
                with open(chunks_file, 'wb') as f:
                    pickle.dump(self.chunks, f)
                
                print(f"💾 Index saved to {self.index_path}")
            except Exception as e:
                print(f"❌ Failed to save index: {str(e)}")
    
    def _load_index(self):
        """Load FAISS index and chunks from disk."""
        if os.path.exists(self.index_path):
            try:
                index_file = os.path.join(self.index_path, "index.faiss")
                chunks_file = os.path.join(self.index_path, "chunks.pkl")
                
                if os.path.exists(index_file) and os.path.exists(chunks_file):
                    # Load FAISS index
                    self.index = faiss.read_index(index_file)
                    
                    # Load chunks metadata
                    with open(chunks_file, 'rb') as f:
                        self.chunks = pickle.load(f)
                    
                    print(f"✅ Loaded existing index with {len(self.chunks)} chunks")
                    return True
            except Exception as e:
                print(f"⚠️ Failed to load existing index: {str(e)}")
                print("🔄 Will create new index...")
        
        return False
    
    def add_documents(self, chunks: List[Dict], save_index: bool = True):
        """
        Add document chunks to the index.
        
        Args:
            chunks: List of dictionaries with 'text', 'source', 'chunk_id' keys
            save_index: Whether to save index to disk after adding
        """
        if not chunks:
            return
        
        self._initialize_index()
        
        # Extract texts for embedding
        texts = [chunk['text'] for chunk in chunks]
        
        print(f"🧠 Generating embeddings for {len(texts)} chunks...")
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        embeddings = embeddings.astype('float32')
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store chunk metadata
        self.chunks.extend(chunks)
        
        print(f"✅ Added {len(chunks)} chunks to index")
        
        # Save index to disk
        if save_index:
            self._save_index()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks.
        
        Args:
            query: Search query text
            top_k: Number of results to return
        
        Returns:
            List of dictionaries with 'text', 'source', 'chunk_id', 'score' keys
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        self._load_model()
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True).astype('float32')
        
        # Search in FAISS
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                chunk_data = self.chunks[idx].copy()
                # Convert L2 distance to similarity score (lower distance = higher similarity)
                distance = float(distances[0][i])
                # Simple similarity: 1 / (1 + distance)
                similarity = 1.0 / (1.0 + distance)
                chunk_data['score'] = similarity
                chunk_data['distance'] = distance
                results.append(chunk_data)
        
        return results
    
    def get_chunk_count(self) -> int:
        """Get total number of indexed chunks."""
        if self.index is None:
            return 0
        return self.index.ntotal
    
    def reset(self):
        """Reset the index and clear all chunks."""
        self.index = None
        self.chunks = []
        
        # Remove saved index files
        if os.path.exists(self.index_path):
            try:
                import shutil
                shutil.rmtree(self.index_path)
                print("🗑️ Removed saved index files")
            except Exception as e:
                print(f"⚠️ Failed to remove index files: {str(e)}")
    
    def rebuild_from_data(self, data_dir: str = "data"):
        """
        Rebuild the entire index from documents in data directory.
        
        Args:
            data_dir: Directory containing documents to index
        """
        from .processing import process_documents_from_directory
        
        # Reset current index
        self.reset()
        
        # Process documents and build index
        try:
            chunks = process_documents_from_directory(data_dir)
            if chunks:
                self.add_documents(chunks)
                return len(chunks)
            else:
                print("⚠️ No documents found to process")
                return 0
        except Exception as e:
            print(f"❌ Failed to rebuild index: {str(e)}")
            return 0