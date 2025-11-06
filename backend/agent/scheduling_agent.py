"""
Scheduling agent logic and state management.
"""
import json
import re
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import google.generativeai as genai
from backend.config import get_config
from backend.agent.prompts import get_system_prompt, get_tool_instructions
from backend.tools.availability_tool import check_availability, get_available_slots
from backend.tools.booking_tool import book_appointment
from backend.rag.faq_rag import answer_faq, is_faq_question


class SchedulingAgent:
    """Manages conversation state and handles scheduling logic."""
    
    def __init__(self):
        self.config = get_config()
        api_key = self.config.get("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY not found in config.properties. Please set your Gemini API key.")
        
        genai.configure(api_key=api_key)
        model_name = self.config.get("LLM_MODEL", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(model_name)
        
        # Conversation states
        self.conversations: Dict[str, Dict[str, Any]] = {}
    
    def _get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get or create conversation state."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "messages": [],
                "state": "greeting",  # greeting, collecting_info, suggesting_slots, confirming, completed
                "appointment_type": None,
                "preferences": {},
                "patient_info": {},
                "selected_slot": None
            }
        return self.conversations[conversation_id]
    
    def _add_message(self, conversation_id: str, role: str, content: str):
        """Add message to conversation history."""
        conv = self._get_conversation(conversation_id)
        conv["messages"].append({
            "role": role,
            "content": content
        })
    
    def _call_llm(self, messages: List[Dict[str, str]], tools_enabled: bool = True) -> str:
        """Call Gemini LLM with messages."""
        system_prompt = get_system_prompt()
        
        # Build the prompt from messages
        prompt_parts = [system_prompt]
        
        if tools_enabled:
            prompt_parts.append(get_tool_instructions())
        
        # Convert messages to text format for Gemini
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        # Add final user prompt if last message is not from user
        if messages and messages[-1].get("role") != "user":
            prompt_parts.append("User: Please respond.")
        
        full_prompt = "\n\n".join(prompt_parts)
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 500
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
                    print(f"Warning: Response blocked by safety filters (finish_reason: {finish_name})")
                    return self._handle_safety_blocked(prompt_parts)
                elif finish_name != 'STOP' or finish_value != 1:  # Not normal completion
                    print(f"Warning: Unexpected finish_reason: {finish_name} (value: {finish_value})")
                    return self._handle_safety_blocked(prompt_parts)
            
            # Safely access response text
            try:
                if hasattr(response, 'text') and response.text:
                    response_text = response.text.strip()
                    # Clean up any tool call syntax that might have leaked through
                    response_text = self._clean_response(response_text)
                    return response_text
                else:
                    # Response has no text content
                    print("Warning: Response has no text content")
                    return self._handle_safety_blocked(prompt_parts)
            except Exception as text_error:
                # If accessing text fails, handle gracefully
                print(f"Warning: Could not access response text: {text_error}")
                return self._handle_safety_blocked(prompt_parts)
                
        except Exception as e:
            # Log the actual error for debugging
            import traceback
            error_details = str(e)
            print(f"Error calling Gemini API: {error_details}")
            print(f"Traceback: {traceback.format_exc()}")
            
            # Check if it's the specific "no valid Part" error
            if "requires the response to contain a valid" in error_details or "finish_reason" in error_details:
                return self._handle_safety_blocked(prompt_parts)
            
            return f"I apologize, but I'm experiencing technical difficulties. Please try again or contact our office directly."
    
    def _clean_response(self, text: str) -> str:
        """Remove tool call syntax and technical details from response."""
        # Remove tool call patterns
        patterns_to_remove = [
            r'\*\*Tool Call:\*\*.*?`',
            r'`check_availability\([^)]+\)`',
            r'`book_appointment\([^)]+\)`',
            r'`answer_faq\([^)]+\)`',
            r'\*\*Tool Call:\*\*',
            r'Tool Call:',
            r'Calling tool:',
            r'Using tool:',
        ]
        
        cleaned_text = text
        for pattern in patterns_to_remove:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    def _handle_safety_blocked(self, prompt_parts: List[str]) -> str:
        """Handle case where response was blocked by safety filters."""
        # Extract the last user message for context
        user_message = ""
        for part in reversed(prompt_parts):
            if part.startswith("User: "):
                user_message = part.replace("User: ", "").strip()
                break
        
        # Provide a helpful response without using the blocked content
        if "book" in user_message.lower() or "appointment" in user_message.lower() or "schedule" in user_message.lower():
            return "I'd be happy to help you schedule an appointment! Could you please tell me:\n1. What type of appointment you need (consultation, follow-up, physical exam, or specialist)?\n2. Your preferred date and time?"
        elif "morning" in user_message.lower() or "afternoon" in user_message.lower() or "evening" in user_message.lower() or "week" in user_message.lower():
            return "Let me check our availability for that time. Could you please provide:\n1. The specific date you prefer?\n2. The type of appointment you need?"
        else:
            return "I understand you'd like to schedule an appointment. Could you please provide:\n1. The type of appointment you need?\n2. Your preferred date and time?\n\nI'll help you find the best available slot!"
    
    def _extract_appointment_info(self, user_message: str, conversation_id: str) -> Dict[str, Any]:
        """Extract appointment information from user message."""
        conv = self._get_conversation(conversation_id)
        
        # Check for FAQ questions
        if is_faq_question(user_message):
            faq_answer = answer_faq(user_message)
            return {"type": "faq", "answer": faq_answer}
        
        # Check for appointment type keywords
        message_lower = user_message.lower()
        appointment_types = {
            "consultation": ["consultation", "checkup", "check-up", "routine", "general", "appointment"],
            "followup": ["follow-up", "followup", "follow up", "returning"],
            "physical": ["physical", "exam", "examination"],
            "special": ["specialist", "special", "complex"]
        }
        
        detected_type = None
        for appt_type, keywords in appointment_types.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_type = appt_type
                break
        
        # Extract date preferences
        date_preferences = {}
        if "today" in message_lower or "asap" in message_lower or "soon" in message_lower:
            date_preferences["urgency"] = "asap"
        elif "tomorrow" in message_lower:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            date_preferences["preferred_date"] = tomorrow
        elif "this week" in message_lower:
            date_preferences["timeframe"] = "this_week"
        elif "next week" in message_lower:
            date_preferences["timeframe"] = "next_week"
        
        # Extract time preferences
        time_preferences = {}
        if "morning" in message_lower:
            time_preferences["preferred_time"] = "morning"
        elif "afternoon" in message_lower:
            time_preferences["preferred_time"] = "afternoon"
        elif "evening" in message_lower:
            time_preferences["preferred_time"] = "evening"
        
        return {
            "type": "scheduling",
            "appointment_type": detected_type,
            "date_preferences": date_preferences,
            "time_preferences": time_preferences
        }
    
    def process_message(self, user_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user message and return agent response.
        
        Args:
            user_message: User's message
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dictionary with response and conversation_id
        """
        # Generate or use conversation ID
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        conv = self._get_conversation(conversation_id)
        
        # Add user message to history
        self._add_message(conversation_id, "user", user_message)
        
        # Extract information from message
        info = self._extract_appointment_info(user_message, conversation_id)
        
        # Handle FAQ questions
        if info.get("type") == "faq":
            response = info["answer"]
            self._add_message(conversation_id, "assistant", response)
            return {
                "response": response,
                "conversation_id": conversation_id
            }
        
        # Handle scheduling
        # Update conversation state based on extracted info
        if info.get("appointment_type"):
            conv["appointment_type"] = info["appointment_type"]
        
        if info.get("date_preferences"):
            conv["preferences"].update(info["date_preferences"])
        
        if info.get("time_preferences"):
            conv["preferences"].update(info["time_preferences"])
        
        # Build context for LLM
        context_messages = []
        
        # Add conversation history (last 5 messages for context)
        recent_messages = conv["messages"][-5:]
        for msg in recent_messages:
            context_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # If we have appointment type and preferences, check availability
        if conv["appointment_type"] and conv["preferences"]:
            # Determine date to check
            date_to_check = None
            if "preferred_date" in conv["preferences"]:
                date_to_check = conv["preferences"]["preferred_date"]
            elif "urgency" in conv["preferences"] and conv["preferences"]["urgency"] == "asap":
                # Check today and next few days
                date_to_check = datetime.now().strftime("%Y-%m-%d")
            elif "timeframe" in conv["preferences"]:
                if conv["preferences"]["timeframe"] == "this_week":
                    date_to_check = datetime.now().strftime("%Y-%m-%d")
                else:
                    # Next week
                    date_to_check = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            else:
                # Default to tomorrow
                date_to_check = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Check availability
            availability_result = check_availability(date_to_check, conv["appointment_type"])
            available_slots = [slot for slot in availability_result.get("available_slots", []) if slot.get("available")]
            
            # Filter by time preference if specified
            if "preferred_time" in conv["preferences"]:
                preferred = conv["preferences"]["preferred_time"]
                if preferred == "morning":
                    available_slots = [s for s in available_slots if int(s["start_time"].split(":")[0]) < 12]
                elif preferred == "afternoon":
                    available_slots = [s for s in available_slots if 12 <= int(s["start_time"].split(":")[0]) < 17]
                elif preferred == "evening":
                    available_slots = [s for s in available_slots if int(s["start_time"].split(":")[0]) >= 17]
            
            # Add availability info to context with current date reference
            if available_slots:
                # Format date nicely for context
                date_obj = datetime.strptime(date_to_check, "%Y-%m-%d")
                if date_to_check == datetime.now().strftime("%Y-%m-%d"):
                    date_display = f"today ({date_obj.strftime('%B %d, %Y')})"
                elif date_to_check == (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"):
                    date_display = f"tomorrow ({date_obj.strftime('%B %d, %Y')})"
                else:
                    date_display = f"{date_obj.strftime('%B %d, %Y')}"
                
                slots_text = "\n".join([
                    f"- {s['start_time']} - {s['end_time']}" for s in available_slots[:5]
                ])
                context_messages.append({
                    "role": "system",
                    "content": f"Available appointment slots for {date_display}:\n{slots_text}\n\nNote: Today is {datetime.now().strftime('%B %d, %Y')}. Present these slots naturally without mentioning tool calls or technical details."
                })
        
        # Generate response using LLM
        response = self._call_llm(context_messages, tools_enabled=True)
        
        # Add response to history
        self._add_message(conversation_id, "assistant", response)
        
        return {
            "response": response,
            "conversation_id": conversation_id
        }


# Global agent instance
_agent_instance: Optional[SchedulingAgent] = None


def get_agent() -> SchedulingAgent:
    """Get the global scheduling agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SchedulingAgent()
    return _agent_instance
