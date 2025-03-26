# PythonAnywhere Deployment Guide for AI Voice Bot

## Step 1: Create a PythonAnywhere Account
1. Go to [PythonAnywhere](https://www.pythonanywhere.com/) and sign up for a free account.
2. After logging in, you'll land on the dashboard.

## Step 2: Set Up a New Web App
1. Click on the "Web" tab in the top navigation bar.
2. Click on "Add a new web app".
3. Choose your domain name (it will be yourusername.pythonanywhere.com).
4. Select "Manual configuration" (not the Flask/Django options).
5. Select Python 3.9 as your Python version.

## Step 3: Upload Your Code
1. Go to the "Files" tab.
2. Create a new directory for your project (e.g., `ai-voice-bot`).
3. You can either upload files through the interface or use Git:

### Using Git:
1. Go to the "Consoles" tab and start a new Bash console.
2. Run the following commands:
   ```bash
   cd
   git clone https://github.com/ALPHA-CODE-HUB/ai-vocie-bot.git
   ```

## Step 4: Set Up a Virtual Environment
1. In the Bash console, run:
   ```bash
   cd ai-vocie-bot
   mkvirtualenv --python=/usr/bin/python3.9 voicebot-env
   pip install -r backend/requirements.txt
   ```

## Step 5: Configure the Web App
1. Go back to the "Web" tab.
2. Under "Code" section, set:
   - Source code: `/home/yourusername/ai-vocie-bot/backend`
   - Working directory: `/home/yourusername/ai-vocie-bot/backend`
   - WSGI configuration file: Look for the path to your WSGI file.

3. Edit the WSGI configuration file by clicking on the link. Replace its contents with:
   ```python
   import sys
   import os
   
   # Add your project directory to path
   path = '/home/yourusername/ai-vocie-bot/backend'
   if path not in sys.path:
       sys.path.append(path)
   
   # Import the FastAPI app and wrap it for WSGI serving
   from backend.wsgi import application
   ```

4. In the "Virtualenv" section, enter the path to your virtual environment:
   ```
   /home/yourusername/.virtualenvs/voicebot-env
   ```

## Step 6: Set Environment Variables
1. Still on the "Web" tab, add these environment variables in the "Environment variables" section:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

## Step 7: Configure Static Files (if needed)
1. If your app has a frontend, add a static files mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/ai-vocie-bot/frontend/dist/`

## Step 8: Reload Your Web App
1. Click the green "Reload" button at the top of the Web tab.

## Testing Your Deployment
1. Visit your PythonAnywhere URL: `https://yourusername.pythonanywhere.com`
2. You should see your AI Voice Bot API running.

## Troubleshooting
- If you encounter issues, check the error logs under the "Web" tab.
- Make sure all paths are correct in the WSGI configuration.
- Ensure your virtual environment has all necessary packages.
- Free accounts have CPU and memory limitations, so complex operations might be slow.

## Limitations of Free Tier
- The free tier includes:
  - 1 web app on a *.pythonanywhere.com subdomain
  - 512MB storage
  - Limited CPU usage
  - Web app is always on (no sleep policy like on some other platforms)
  - No scheduled tasks
  - Support from the Beginner forums 