"""
Chat API endpoint for the scheduling agent.
"""
from fastapi import APIRouter
from backend.models.schemas import ChatMessage, ChatResponse
from backend.agent.scheduling_agent import get_agent


router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Process a chat message and return agent response.
    
    Args:
        chat_message: Chat message with user input and optional conversation ID
        
    Returns:
        Chat response with agent message and conversation ID
    """
    agent = get_agent()
    
    try:
        result = agent.process_message(
            user_message=chat_message.message,
            conversation_id=chat_message.conversation_id
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            status="success"
        )
    except Exception as e:
        return ChatResponse(
            response=f"I apologize, but I encountered an error: {str(e)}. Please try again or contact our office directly.",
            conversation_id=chat_message.conversation_id or "error",
            status="error"
        )
