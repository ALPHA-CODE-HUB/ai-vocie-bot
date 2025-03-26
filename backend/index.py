import sys
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Attempt to import app with error handling
try:
    from main import app
    
    # For Vercel serverless deployment
    handler = app
    
    # Log successful initialization
    logger.info("FastAPI application successfully initialized")
except Exception as e:
    # Log the full exception for debugging
    error_msg = f"Error initializing application: {str(e)}\n{traceback.format_exc()}"
    logger.error(error_msg)
    
    # Create a minimal emergency app for error reporting
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    
    emergency_app = FastAPI()
    
    @emergency_app.get("/{path:path}")
    @emergency_app.post("/{path:path}")
    async def error_response(request: Request, path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Server initialization failed",
                "message": str(e),
                "path": path,
                "python_version": sys.version,
                "sys_path": sys.path
            }
        )
    
    handler = emergency_app 