import os
import subprocess
import sys

def run_server():
    """
    Run the FastAPI server.
    """
    # Check if environment variables are set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        sys.exit(1)
    if not os.environ.get("ELEVENLABS_API_KEY"):
        print("Error: ELEVENLABS_API_KEY environment variable is not set")
        sys.exit(1)
    
    print("Environment variables are set")
    
    # Run uvicorn server
    try:
        print("Starting FastAPI server...")
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server() 