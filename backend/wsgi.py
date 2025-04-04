import sys
import os

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Import the FastAPI app
from main import app

# For WSGI deployment to PythonAnywhere
application = app 