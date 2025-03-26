from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os

app = FastAPI()

@app.get("/api")
async def hello():
    return {"message": "AI Voice Bot API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Add routes for your other API functions
# These will be implemented gradually as we confirm each step works

# Special handler for Vercel serverless functions
def handler(request, context):
    return app 