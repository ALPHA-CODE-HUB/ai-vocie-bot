import os
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

def validate_api_keys() -> Dict[str, bool]:
    """
    Validate that all required API keys are present in the environment.
    
    Returns:
        Dict[str, bool]: A dictionary with API service names as keys and validation status as values
    """
    api_keys = {
        "OpenAI": os.environ.get("OPENAI_API_KEY") is not None,
        "ElevenLabs": os.environ.get("ELEVENLABS_API_KEY") is not None
    }
    
    for service, is_valid in api_keys.items():
        if not is_valid:
            logger.warning(f"{service} API key is missing")
    
    return api_keys

def format_conversation_for_openai(system_prompt: str, conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Format conversation history for OpenAI API.
    
    Args:
        system_prompt (str): The system prompt that defines AI behavior
        conversation_history (List[Dict[str, str]]): The conversation history
        
    Returns:
        List[Dict[str, str]]: Formatted messages for OpenAI API
    """
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    for message in conversation_history:
        # Ensure only valid roles are included
        if message.get("role") in ["user", "assistant", "system"]:
            messages.append({
                "role": message["role"],
                "content": message["content"]
            })
    
    return messages

def sanitize_text_input(text: str) -> str:
    """
    Sanitize user text input to prevent injection attacks.
    
    Args:
        text (str): The raw user input
        
    Returns:
        str: Sanitized text
    """
    # Remove potentially harmful characters
    text = text.strip()
    
    # Basic sanitization (can be expanded based on requirements)
    # This is a simple example - production code would need more robust sanitization
    return text

def generate_response_for_interview_question(question_type: str, text: str) -> Optional[str]:
    """
    Generate a tailored response for common interview question types.
    
    Args:
        question_type (str): The type of interview question
        text (str): The question text
        
    Returns:
        Optional[str]: A predefined response if available, None otherwise
    """
    interview_responses = {
        "life_story": "My journey is defined by a relentless curiosity for AI and machine learning. From conducting research for academic projects to supporting student research papers, I've been driven by a desire to leverage technology to solve complex problems and continuously learn.",
        "superpower": "My #1 superpower is adaptability in technical problem-solving. Whether it's implementing ML models using TensorFlow and PyTorch or guiding students through research challenges, I can quickly understand complex scenarios and develop innovative solutions.",
        "growth_areas": "I'm focused on expanding my expertise in generative AI technologies, developing more advanced deep learning and computer vision skills, and enhancing my ability to translate complex technical concepts for diverse audiences.",
        "misconception": "Colleagues might perceive me as purely technical, but I'm equally passionate about communication and collaborative learning. My work isn't just about coding—it's about creating meaningful technological solutions and helping others understand them.",
        "pushing_boundaries": "I consistently push my boundaries by taking on diverse research projects, exploring emerging technologies like generative AI, and challenging myself to learn across different domains—from cybersecurity simulations to data analytics. Each new project is an opportunity to expand my capabilities."
    }
    
    return interview_responses.get(question_type)

def detect_interview_question_type(text: str) -> Optional[str]:
    """
    Detect the type of interview question from text.
    
    Args:
        text (str): The question text
        
    Returns:
        Optional[str]: The detected question type or None
    """
    text = text.lower()
    
    if any(phrase in text for phrase in ["tell me about yourself", "your background", "life story", "journey"]):
        return "life_story"
    elif any(phrase in text for phrase in ["superpower", "strength", "greatest skill", "best at"]):
        return "superpower"
    elif any(phrase in text for phrase in ["growth", "improve", "development", "working on", "weakness"]):
        return "growth_areas"
    elif any(phrase in text for phrase in ["misconception", "misunderstand", "wrong about you", "misjudge"]):
        return "misconception"
    elif any(phrase in text for phrase in ["push boundaries", "challenge yourself", "comfort zone", "limits"]):
        return "pushing_boundaries"
    
    return None 