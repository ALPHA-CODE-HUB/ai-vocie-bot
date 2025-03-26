from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {
        "message": "AI Voice Bot API is running",
        "python_version": sys.version,
        "environment": os.environ.get("VERCEL_ENV", "unknown"),
        "region": os.environ.get("VERCEL_REGION", "unknown")
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# For Vercel serverless deployment
handler = app 