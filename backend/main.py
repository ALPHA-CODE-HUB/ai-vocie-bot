from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from openai import OpenAI
import os
from dotenv import load_dotenv
from elevenlabs import generate, save, set_api_key
import logging
import tempfile
import io
import json
import requests
from typing import Optional, List, Dict
from pydantic import BaseModel

# Import custom error handling
from errors import setup_exception_handlers, APIKeyMissingError, AudioProcessingError, TextGenerationError, SpeechGenerationError

# Import utility functions
from utils import (
    process_audio_file,
    generate_ai_response,
    generate_speech,
    setup_logging,
    validate_api_keys
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
setup_logging()

# Validate API keys
validate_api_keys()

# Define request models
class TextRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []

@app.get("/")
async def read_root():
    return {"message": "AI Voice Bot API is running"}

@app.post("/api/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...)):
    try:
        if not audio_file:
            raise AudioProcessingError("No audio file provided")
        
        # Process the audio file
        text = process_audio_file(audio_file)
        return JSONResponse({"response": text})
    
    except Exception as e:
        logging.error(f"Error in speech_to_text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-text")
async def generate_text(request: TextRequest):
    try:
        if not request.message:
            raise TextGenerationError("No message provided")
        
        response = generate_ai_response(request.message, request.conversation_history)
        return JSONResponse({"response": response})
    
    except Exception as e:
        logging.error(f"Error in generate_text: {str(e)}")
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
        logging.error(f"Error in text_to_speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# For Vercel serverless deployment
handler = app 