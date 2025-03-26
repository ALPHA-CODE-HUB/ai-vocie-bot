from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
import os
from dotenv import load_dotenv
from elevenlabs import generate, save, set_api_key
from pydantic import BaseModel
import logging
import tempfile
import io
import json
import requests
from typing import Optional, List, Dict

# Import custom error handling
from errors import setup_exception_handlers, APIKeyMissingError, AudioProcessingError, TextGenerationError, SpeechGenerationError

# Import utility functions
from utils import (
    validate_api_keys, 
    format_conversation_for_openai,
    sanitize_text_input,
    generate_response_for_interview_question,
    detect_interview_question_type
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug - print current directory and check if .env exists
print(f"Current working directory: {os.getcwd()}")
env_path = os.path.join(os.getcwd(), '.env')
print(f"Checking if .env exists: {os.path.exists(env_path)}")

# Initialize FastAPI app
app = FastAPI(title="Home.LLC AI Voice Bot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_exception_handlers(app)

# DIRECTLY SET API KEYS
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["ELEVENLABS_API_KEY"] = "sk_cce18174bb752b10a10abbe0a3cad218905a389cdc10fb7d"

# API key configuration - use the directly set environment variables
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# Log API key (masked)
masked_key = OPENROUTER_API_KEY[:8] + "*" * (len(OPENROUTER_API_KEY) - 16) + OPENROUTER_API_KEY[-8:] if OPENROUTER_API_KEY else "None"
logger.info(f"Using OpenRouter API key: {masked_key}")

# Initialize OpenAI client with OpenRouter base URL
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

if ELEVENLABS_API_KEY:
    set_api_key(ELEVENLABS_API_KEY)
else:
    logger.warning("ELEVENLABS_API_KEY not found in environment variables")

# Validate API keys
api_keys_status = {"OpenRouter": OPENROUTER_API_KEY is not None, "ElevenLabs": ELEVENLABS_API_KEY is not None}

# Persona context 
PERSONA_CONTEXT = """
You are Adithya S Arangil, an AI/ML Developer with a passion for machine learning, deep learning, and research.

Core Personality Traits:
- Professional yet personable tone
- Confident without being arrogant
- Enthusiastic about technology and learning
- Clear and articulate communication style

Personal Information:
- Contact: 7994219931
- Email: adithyasarangil21@gmail.com
- Location: Ernakulam, Kerala

Education:
- Bachelor of Computer Application from Amrita Vishwa Vidyapeetham (2019-2022)

Professional Expertise:
- AI/ML
- Deep Learning
- Android Development
- Java
- Python

Languages:
- English
- Hindi
- Malayalam

Work Experience:
- Machine Learning/Deep Learning Researcher (Freelance, 2023-2025)
  • Conducted research and developed ML/DL models for academic projects and student research papers
  • Assisted students in structuring and writing research papers related to deep learning, machine learning, and computer vision
  • Implemented and optimized models using Python, TensorFlow, PyTorch, and Keras
  • Provided guidance on dataset preprocessing, model evaluation, and paper formatting

Certifications:
- Foundation of Generative AI | Udacity | January 2025
- Data Analytics Job Simulation | Deloitte Australia - Forage | February 2025
- Software Engineering Job Simulation | Electronic Arts - Forage | January 2025
- Cybersecurity Job Simulation | Mastercard - Forage | January 2025
- Cybersecurity Analyst Job Simulation | Tata Group - Forage | November 2024

Publications:
- MALWARE DETECTION USING DEEP LEARNING IN CYBER SECURITY

Professional Profile:
"I aspire to join a globally established organization where I can leverage my technical expertise and skills to make meaningful contributions while advancing my career through continuous learning, collaborative projects, and exposure to challenging professional opportunities."

Life Story: 
"My journey is defined by a relentless curiosity for AI and machine learning. From conducting research for academic projects to supporting student research papers, I've been driven by a desire to leverage technology to solve complex problems and continuously learn."

Superpower:
"My #1 superpower is adaptability in technical problem-solving. Whether it's implementing ML models using TensorFlow and PyTorch or guiding students through research challenges, I can quickly understand complex scenarios and develop innovative solutions."

Growth Areas:
"Expanding my expertise in generative AI technologies, developing more advanced deep learning and computer vision skills, and enhancing my ability to translate complex technical concepts for diverse audiences."

Potential Misconception:
"Colleagues might perceive me as purely technical, but I'm equally passionate about communication and collaborative learning. My work isn't just about coding—it's about creating meaningful technological solutions and helping others understand them."

Pushing Boundaries:
"I consistently push my boundaries by taking on diverse research projects, exploring emerging technologies like generative AI, and challenging myself to learn across different domains—from cybersecurity simulations to data analytics. Each new project is an opportunity to expand my capabilities."
"""

# Define models
class TextRequestModel(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class TextResponseModel(BaseModel):
    response: str

# Helper functions
def generate_ai_response(message: str, conversation_history: List[Dict[str, str]] = []) -> str:
    """Generate a response from the AI using OpenRouter."""
    try:
        if not OPENROUTER_API_KEY:
            raise APIKeyMissingError("OpenRouter")
        
        # Sanitize input
        sanitized_message = sanitize_text_input(message)
        
        # Check if this is a standard interview question
        question_type = detect_interview_question_type(sanitized_message)
        if question_type:
            predefined_response = generate_response_for_interview_question(question_type, sanitized_message)
            if predefined_response:
                return predefined_response
        
        # Prepare conversation history
        messages = format_conversation_for_openai(PERSONA_CONTEXT, conversation_history)
        
        # Add the current message
        messages.append({"role": "user", "content": sanitized_message})
        
        # Log the API key being used (masked)
        logger.info(f"Using OpenRouter API key: {masked_key}")
        
        # Call OpenRouter API with the OpenAI client
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # OpenAI GPT-3.5 Turbo model
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        raise TextGenerationError(f"Failed to generate AI response: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Home.LLC AI Voice Bot API"}

@app.post("/api/speech-to-text", response_model=TextResponseModel)
async def speech_to_text(audio_file: UploadFile = File(...)):
    """Convert speech to text using OpenAI's Whisper model."""
    try:
        if not OPENROUTER_API_KEY:
            raise APIKeyMissingError("OpenRouter")
            
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            # Write the uploaded file to the temporary file
            temp_file.write(await audio_file.read())
            temp_file_path = temp_file.name
        
        # OpenRouter doesn't support Whisper directly, so we'll use OpenAI's API for this
        # We'll need to use requests directly for the audio API
        with open(temp_file_path, "rb") as audio:
            # Most OpenRouter keys don't work with OpenAI's audio API
            # So we'll return a placeholder response for now
            transcript_text = "I'm sorry, but speech-to-text is currently limited. Please type your message instead."
            
            # Attempt to use OpenAI's API directly as a fallback
            try:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                    files={"file": audio},
                    data={"model": "whisper-1"}
                )
                
                # Check if we get a valid response
                if response.status_code == 200:
                    response_json = response.json()
                    if "text" in response_json:
                        transcript_text = response_json["text"]
            except Exception as inner_e:
                logger.warning(f"Speech-to-text fallback failed: {str(inner_e)}")
                # Continue with the placeholder response
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return {"response": transcript_text}
    except Exception as e:
        logger.error(f"Error in speech-to-text conversion: {str(e)}")
        raise AudioProcessingError(f"Speech-to-text conversion failed: {str(e)}")

@app.post("/api/generate-text", response_model=TextResponseModel)
async def generate_text(request: TextRequestModel):
    """Generate text response based on input message."""
    try:
        response_text = generate_ai_response(request.message, request.conversation_history)
        return {"response": response_text}
    except Exception as e:
        logger.error(f"Error generating text response: {str(e)}")
        raise TextGenerationError(f"Text generation failed: {str(e)}")

@app.post("/api/text-to-speech")
async def text_to_speech(text: str = Form(...)):
    """Convert text to speech using ElevenLabs API."""
    try:
        if not ELEVENLABS_API_KEY:
            raise APIKeyMissingError("ElevenLabs")
        
        # Sanitize input
        sanitized_text = sanitize_text_input(text)
            
        # Generate audio using ElevenLabs
        audio = generate(
            text=sanitized_text,
            voice="Adam",  # Default voice
            model="eleven_monolingual_v1"
        )
        
        # Return audio as a streaming response
        return StreamingResponse(
            io.BytesIO(audio),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {str(e)}")
        raise SpeechGenerationError(f"Text-to-speech conversion failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 