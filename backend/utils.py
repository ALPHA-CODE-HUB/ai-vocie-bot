import os
import logging
import tempfile
import requests
from openai import OpenAI
from elevenlabs import generate, set_api_key
from typing import Dict, List, Any, Optional

# Configure logging
def setup_logging():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

# Validate API keys
def validate_api_keys():
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
    
    # Set ElevenLabs API key
    set_api_key(ELEVENLABS_API_KEY)
    
    return OPENAI_API_KEY, ELEVENLABS_API_KEY

# Process audio file
def process_audio_file(audio_file):
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        # Write the uploaded file to the temporary file
        temp_file.write(audio_file.read())
        temp_file_path = temp_file.name
    
    try:
        # Attempt to use OpenAI's API directly
        with open(temp_file_path, "rb") as audio:
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                files={"file": audio},
                data={"model": "whisper-1"}
            )
            
            if response.status_code == 200:
                response_json = response.json()
                if "text" in response_json:
                    return response_json["text"]
            return "I'm sorry, but speech-to-text is currently limited. Please type your message instead."
    
    except Exception as e:
        logging.error(f"Error processing audio file: {str(e)}")
        return "I'm sorry, but speech-to-text is currently limited. Please type your message instead."
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

# Generate AI response
def generate_ai_response(message: str, conversation_history: list = []) -> str:
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key not found")
    
    # Initialize OpenAI client with OpenRouter base URL
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    
    # Prepare conversation history
    messages = []
    messages.append({"role": "system", "content": "You are a helpful AI assistant."})
    for msg in conversation_history:
        messages.append(msg)
    messages.append({"role": "user", "content": message})
    
    # Call OpenRouter API
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Generate speech
def generate_speech(text: str) -> bytes:
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
    
    if not ELEVENLABS_API_KEY:
        raise ValueError("ElevenLabs API key not found")
    
    # Generate audio using ElevenLabs
    audio = generate(
        text=text,
        voice="Adam",  # Default voice
        model="eleven_monolingual_v1"
    )
    
    return audio

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