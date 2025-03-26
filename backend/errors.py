from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define custom exceptions
class APIKeyMissingError(HTTPException):
    def __init__(self, service_name: str):
        super().__init__(
            status_code=500,
            detail=f"{service_name} API key is missing. Please check your environment variables."
        )

class AudioProcessingError(HTTPException):
    def __init__(self, message: str = "Error processing audio"):
        super().__init__(
            status_code=400,
            detail=message
        )

class TextGenerationError(HTTPException):
    def __init__(self, message: str = "Error generating text response"):
        super().__init__(
            status_code=500,
            detail=message
        )

class SpeechGenerationError(HTTPException):
    def __init__(self, message: str = "Error generating speech from text"):
        super().__init__(
            status_code=500,
            detail=message
        )

# Error handling middleware
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as exc:
            # Re-raise HTTP exceptions as they are already handled by FastAPI
            raise
        except Exception as exc:
            # Log the exception
            logger.exception(f"Unhandled exception: {str(exc)}")
            
            # Return a generic error response
            return JSONResponse(
                status_code=500,
                content={"detail": "An unexpected error occurred. Please try again later."}
            )

# Error handlers to register with the FastAPI app
async def api_key_missing_exception_handler(request: Request, exc: APIKeyMissingError):
    logger.error(f"API Key Missing: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def audio_processing_exception_handler(request: Request, exc: AudioProcessingError):
    logger.error(f"Audio Processing Error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def text_generation_exception_handler(request: Request, exc: TextGenerationError):
    logger.error(f"Text Generation Error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def speech_generation_exception_handler(request: Request, exc: SpeechGenerationError):
    logger.error(f"Speech Generation Error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Function to register all exception handlers with the app
def setup_exception_handlers(app):
    app.add_exception_handler(APIKeyMissingError, api_key_missing_exception_handler)
    app.add_exception_handler(AudioProcessingError, audio_processing_exception_handler)
    app.add_exception_handler(TextGenerationError, text_generation_exception_handler)
    app.add_exception_handler(SpeechGenerationError, speech_generation_exception_handler)
    app.add_middleware(ErrorHandlingMiddleware) 