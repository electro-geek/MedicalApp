"""
Vector store setup and management using ChromaDB.
"""
import json
import warnings
import sys
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from backend.config import get_config
from backend.rag.embeddings import generate_embedding

# Suppress ChromaDB telemetry warnings
import logging
import warnings
import os

# Suppress ChromaDB telemetry-related warnings
logging.getLogger("chromadb.telemetry").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", message=".*Failed to send telemetry event.*")
warnings.filterwarnings("ignore", message=".*capture\\(\\) takes 1 positional argument.*")

# Suppress telemetry errors by redirecting stderr during ChromaDB operations
_original_stderr = sys.stderr

class TelemetryErrorFilter:
    """Filter to suppress ChromaDB telemetry errors from stderr."""
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.buffer = []
    
    def write(self, message):
        # Suppress telemetry-related errors
        if "Failed to send telemetry event" in str(message):
            return
        if "capture() takes 1 positional argument" in str(message):
            return
        # Write everything else to original stderr
        self.original_stderr.write(message)
    
    def flush(self):
        self.original_stderr.flush()
    
    def __getattr__(self, name):
        return getattr(self.original_stderr, name)

# Store original stderr
_original_stderr = sys.stderr


class VectorStore:
    """Manages the vector store for clinic information."""
    
    def __init__(self):
        self.config = get_config()
        self.db_path = Path(self.config.get("VECTOR_DB_PATH", "./data/vectordb"))
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Suppress telemetry errors during ChromaDB initialization
        sys.stderr = TelemetryErrorFilter(_original_stderr)
        try:
            # Initialize ChromaDB
            # Disable telemetry to avoid capture() errors
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="clinic_info",
                metadata={"hnsw:space": "cosine"}
            )
        finally:
            # Restore original stderr
            sys.stderr = _original_stderr
    
    def load_clinic_data(self):
        """Load clinic information from JSON file and create embeddings."""
        # Check if data already loaded
        if self.collection.count() > 0:
            return  # Data already loaded
        
        # Suppress telemetry errors during data loading
        sys.stderr = TelemetryErrorFilter(_original_stderr)
        try:
            # Load clinic info JSON
            project_root = Path(__file__).parent.parent.parent
            clinic_info_path = project_root / "data" / "clinic_info.json"
            
            if not clinic_info_path.exists():
                raise FileNotFoundError(f"Clinic info file not found: {clinic_info_path}")
            
            with open(clinic_info_path, 'r') as f:
                clinic_data = json.load(f)
            
            # Process and store data
            documents = []
            metadatas = []
            ids = []
            
            # Process clinic details
            clinic_details = clinic_data.get("clinic_details", {})
            for key, value in clinic_details.items():
                if isinstance(value, str):
                    doc_text = f"{key.replace('_', ' ').title()}: {value}"
                    documents.append(doc_text)
                    metadatas.append({"category": "clinic_details", "key": key})
                    ids.append(f"clinic_details_{key}")
            
            # Process insurance billing
            insurance = clinic_data.get("insurance_billing", {})
            for key, value in insurance.items():
                if isinstance(value, str):
                    doc_text = f"{key.replace('_', ' ').title()}: {value}"
                    documents.append(doc_text)
                    metadatas.append({"category": "insurance_billing", "key": key})
                    ids.append(f"insurance_{key}")
                elif isinstance(value, list):
                    # Handle accepted providers list
                    doc_text = f"Accepted Insurance Providers: {', '.join(value)}"
                    documents.append(doc_text)
                    metadatas.append({"category": "insurance_billing", "key": key})
                    ids.append(f"insurance_{key}")
            
            # Process visit preparation
            visit_prep = clinic_data.get("visit_preparation", {})
            for key, value in visit_prep.items():
                if isinstance(value, str):
                    doc_text = f"{key.replace('_', ' ').title()}: {value}"
                    documents.append(doc_text)
                    metadatas.append({"category": "visit_preparation", "key": key})
                    ids.append(f"visit_prep_{key}")
            
            # Process policies
            policies = clinic_data.get("policies", {})
            for key, value in policies.items():
                if isinstance(value, str):
                    doc_text = f"{key.replace('_', ' ').title()}: {value}"
                    documents.append(doc_text)
                    metadatas.append({"category": "policies", "key": key})
                    ids.append(f"policies_{key}")
            
            # Generate embeddings and store
            embeddings = []
            for doc in documents:
                embedding = generate_embedding(doc)
                embeddings.append(embedding)
            
            # Add to collection
            if documents:
                try:
                    self.collection.add(
                        embeddings=embeddings,
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                except Exception as e:
                    # If adding with embeddings fails, try without (ChromaDB will generate them)
                    print(f"Warning: Could not add with custom embeddings, trying without: {e}")
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
        finally:
            # Restore original stderr
            sys.stderr = _original_stderr
    
    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector store for relevant information.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        # Suppress telemetry errors during query
        sys.stderr = TelemetryErrorFilter(_original_stderr)
        try:
            # Generate query embedding
            query_embedding = generate_embedding(query_text)
            
            # Query collection
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
            except Exception as e:
                # If query with embeddings fails, try with text query
                print(f"Warning: Could not query with custom embedding, trying with text: {e}")
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                
                for i, doc in enumerate(documents):
                    formatted_results.append({
                        "document": doc,
                        "metadata": metadatas[i] if i < len(metadatas) else {},
                        "distance": distances[i] if i < len(distances) else 0.0
                    })
            
            return formatted_results
        finally:
            # Restore original stderr
            sys.stderr = _original_stderr


# Global vector store instance
_vector_store_instance: VectorStore = None


def get_vector_store() -> VectorStore:
    """Get the global vector store instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
        _vector_store_instance.load_clinic_data()
    return _vector_store_instance

