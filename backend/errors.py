from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define custom exceptions
class APIKeyMissingError(HTTPException):
    """Raised when an API key is missing from environment variables."""
    def __init__(self, detail: str = "API key missing"):
        super().__init__(status_code=401, detail=detail)

class AudioProcessingError(HTTPException):
    """Raised when there's an error processing audio files."""
    def __init__(self, detail: str = "Error processing audio file"):
        super().__init__(status_code=400, detail=detail)

class TextGenerationError(HTTPException):
    """Raised when there's an error generating text responses."""
    def __init__(self, detail: str = "Error generating text"):
        super().__init__(status_code=500, detail=detail)

class SpeechGenerationError(HTTPException):
    """Raised when there's an error generating speech."""
    def __init__(self, detail: str = "Error generating speech"):
        super().__init__(status_code=500, detail=detail)

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

# Function to register all exception handlers with the app
def setup_exception_handlers(app):
    """Setup custom exception handlers for the FastAPI app."""
    @app.exception_handler(APIKeyMissingError)
    async def api_key_missing_exception_handler(request: Request, exc: APIKeyMissingError):
        logger.error(f"API Key Missing: {exc}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(AudioProcessingError)
    async def audio_processing_exception_handler(request: Request, exc: AudioProcessingError):
        logger.error(f"Audio Processing Error: {exc}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(TextGenerationError)
    async def text_generation_exception_handler(request: Request, exc: TextGenerationError):
        logger.error(f"Text Generation Error: {exc}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(SpeechGenerationError)
    async def speech_generation_exception_handler(request: Request, exc: SpeechGenerationError):
        logger.error(f"Speech Generation Error: {exc}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    app.add_middleware(ErrorHandlingMiddleware)