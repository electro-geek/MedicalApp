"""
Embedding generation using Google Gemini.
"""
import google.generativeai as genai
from backend.config import get_config


def get_embedding_client():
    """Initialize Gemini for embeddings."""
    config = get_config()
    api_key = config.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY not found in config.properties. Please set your Gemini API key.")
    
    genai.configure(api_key=api_key)
    return genai


def generate_embedding(text: str) -> list:
    """
    Generate embedding for given text using Gemini.
    
    Args:
        text: Text to generate embedding for
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        # Initialize Gemini (configure is called in get_embedding_client)
        get_embedding_client()
        
        # Use Gemini's embedding model
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        
        return result['embedding']
    except Exception as e:
        raise Exception(f"Error generating embedding: {str(e)}")

