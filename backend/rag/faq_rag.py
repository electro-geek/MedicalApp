"""
RAG pipeline for answering FAQ questions.
"""
from typing import Optional
import google.generativeai as genai
from backend.rag.vector_store import get_vector_store
from backend.config import get_config


def get_gemini_model():
    """Get Gemini model for chat."""
    config = get_config()
    api_key = config.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY not found in config.properties. Please set your Gemini API key.")
    
    genai.configure(api_key=api_key)
    model_name = config.get("LLM_MODEL", "gemini-2.5-flash")
    return genai.GenerativeModel(model_name)


def answer_faq(question: str) -> str:
    """
    Answer FAQ question using RAG pipeline.
    
    Args:
        question: User's question
        
    Returns:
        Answer to the question
    """
    # Get relevant context from vector store
    vector_store = get_vector_store()
    relevant_docs = vector_store.query(question, n_results=3)
    
    # Build context from relevant documents
    context_parts = []
    for doc in relevant_docs:
        context_parts.append(doc["document"])
    
    context = "\n\n".join(context_parts)
    
    # Get clinic name from config
    config = get_config()
    clinic_name = config.get("CLINIC_NAME", "our clinic")
    
    # Use Gemini to generate answer based on context
    model = get_gemini_model()
    
    system_prompt = f"""You are a helpful assistant for {clinic_name}. 
Your role is to answer questions about the clinic using the provided context.
Be friendly, accurate, and concise. If the context doesn't contain the answer,
politely say you don't have that information and suggest they contact the clinic directly.
"""
    
    user_prompt = f"""Context about {clinic_name}:
{context}

Question: {question}

Please provide a helpful answer based on the context above."""
    
    try:
        # Combine system prompt and user prompt for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 300
            }
        )
        
        # Check if response was blocked by safety filters or other issues
        if response.candidates:
            candidate = response.candidates[0]
            finish_reason = candidate.finish_reason
            finish_name = finish_reason.name
            finish_value = finish_reason.value
            
            # Check for safety blocking or other non-normal completion reasons
            # SAFETY = 3, MAX_TOKENS = 2, RECITATION = 4, etc.
            # STOP = 1 is normal completion
            if finish_name == 'SAFETY' or finish_value == 3:  # Blocked by safety filters
                print(f"Warning: FAQ response blocked by safety filters (finish_reason: {finish_name})")
                return "I apologize, but I'm having trouble accessing that information right now. Please contact the clinic directly for assistance."
            elif finish_name != 'STOP' or finish_value != 1:  # Not normal completion
                print(f"Warning: Unexpected finish_reason: {finish_name} (value: {finish_value})")
                return "I apologize, but I'm having trouble accessing that information right now. Please contact the clinic directly for assistance."
        
        # Safely access response text
        try:
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                # Response has no text content
                return "I apologize, but I'm having trouble accessing that information right now. Please contact the clinic directly for assistance."
        except Exception as text_error:
            # If accessing text fails, handle gracefully
            print(f"Warning: Could not access FAQ response text: {text_error}")
            return "I apologize, but I'm having trouble accessing that information right now. Please contact the clinic directly for assistance."
            
    except Exception as e:
        error_details = str(e)
        # Check if it's the specific "no valid Part" error
        if "requires the response to contain a valid" in error_details or "finish_reason" in error_details:
            return "I apologize, but I'm having trouble accessing that information right now. Please contact the clinic directly for assistance."
        return f"I apologize, but I'm having trouble accessing the information right now. Please contact the clinic directly for assistance."


def is_faq_question(message: str) -> bool:
    """
    Determine if a message is an FAQ question.
    
    Args:
        message: User's message
        
    Returns:
        True if it appears to be an FAQ question
    """
    # Keywords that suggest FAQ questions
    faq_keywords = [
        "what", "where", "when", "how", "which", "who",
        "insurance", "accept", "payment", "billing",
        "hours", "open", "closed", "location", "directions",
        "parking", "bring", "document", "policy", "cancellation",
        "covid", "mask", "protocol", "first visit", "new patient"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in faq_keywords)
