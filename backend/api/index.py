from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a simple app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running", "python_version": sys.version}

@app.get("/debug")
async def debug():
    return {
        "python_version": sys.version,
        "sys_path": sys.path,
        "working_directory": os.getcwd(),
        "files_in_directory": os.listdir("."),
        "environment": {k: v for k, v in os.environ.items() if not k.lower().endswith("key") and not k.lower().endswith("secret")}
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal server error: {str(exc)}"}
    )

# Export handler for Vercel
handler = app 