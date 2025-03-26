from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import tempfile
import io
import json
import logging
import sys
import traceback
from typing import Optional, List, Dict
from pydantic import BaseModel

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Now attempt to import optional dependencies
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    logger.info("Environment variables loaded")
    
    # Import conditional dependencies with error handling
    try:
        from openai import OpenAI
        logger.info("OpenAI imported successfully")
    except ImportError as e:
        logger.error(f"Error importing OpenAI: {str(e)}")
        
    try:
        from elevenlabs import generate, save, set_api_key
        logger.info("ElevenLabs imported successfully")
    except ImportError as e:
        logger.error(f"Error importing ElevenLabs: {str(e)}")
    
    # Import custom error handling
    try:
        from errors import setup_exception_handlers, APIKeyMissingError, AudioProcessingError, TextGenerationError, SpeechGenerationError
        logger.info("Custom error handlers imported successfully")
    except ImportError as e:
        logger.error(f"Error importing custom error handlers: {str(e)}")
    
    # Import utility functions
    try:
        from utils import (
            process_audio_file,
            generate_ai_response,
            generate_speech,
            setup_logging,
            validate_api_keys
        )
        logger.info("Utility functions imported successfully")
    except ImportError as e:
        logger.error(f"Error importing utility functions: {str(e)}")

except Exception as e:
    error_msg = f"Critical error during initialization: {str(e)}\n{traceback.format_exc()}"
    logger.error(error_msg)
    # Continue - we'll create a minimal app below

# Initialize FastAPI app
app = FastAPI()
logger.info("FastAPI app initialized")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

# Try to setup logging and validate keys, but don't fail if they're not available
try:
    setup_logging()
    validate_api_keys()
except NameError:
    logger.warning("Could not setup logging or validate API keys - continuing with minimal app")
except Exception as e:
    logger.error(f"Error in setup: {str(e)}")

# Define request models
class TextRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []

@app.get("/")
async def read_root():
    env_info = {
        "python_version": sys.version,
        "environment": os.environ.get("VERCEL_ENV", "unknown"),
        "region": os.environ.get("VERCEL_REGION", "unknown")
    }
    return {
        "message": "AI Voice Bot API is running",
        "environment": env_info
    }

@app.get("/debug")
async def debug_info():
    """Endpoint for debugging server configuration"""
    import importlib.metadata
    
    try:
        installed_packages = {pkg: importlib.metadata.version(pkg) 
                             for pkg in ["fastapi", "uvicorn", "openai", "elevenlabs", "python-dotenv"]}
    except Exception as e:
        installed_packages = {"error": str(e)}
        
    return {
        "python_version": sys.version,
        "sys_path": sys.path,
        "environment_variables": {
            k: "[REDACTED]" if k.lower().endswith("key") or k.lower().endswith("secret") 
            else v for k, v in dict(os.environ).items()
        },
        "installed_packages": installed_packages,
        "working_directory": os.getcwd(),
        "files_in_directory": os.listdir("."),
    }

# Only add API endpoints if the necessary functions were imported successfully
if all(func in globals() for func in ["process_audio_file", "generate_ai_response", "generate_speech"]):
    @app.post("/api/speech-to-text")
    async def speech_to_text(audio_file: UploadFile = File(...)):
        try:
            if not audio_file:
                raise AudioProcessingError("No audio file provided")
            
            # Process the audio file
            text = process_audio_file(audio_file)
            return JSONResponse({"response": text})
        
        except Exception as e:
            logger.error(f"Error in speech_to_text: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/generate-text")
    async def generate_text(request: TextRequest):
        try:
            if not request.message:
                raise TextGenerationError("No message provided")
            
            response = generate_ai_response(request.message, request.conversation_history)
            return JSONResponse({"response": response})
        
        except Exception as e:
            logger.error(f"Error in generate_text: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/text-to-speech")
    async def text_to_speech(text: str = Form(...)):
        try:
            if not text:
                raise SpeechGenerationError("No text provided")
            
            audio_data = generate_speech(text)
            
            # Create a temporary file to store the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            return FileResponse(
                temp_file_path,
                media_type="audio/mpeg",
                filename="response.mp3"
            )
        
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
else:
    logger.warning("Not all required functions are available - API endpoints will be limited")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# For Vercel serverless deployment
handler = app 