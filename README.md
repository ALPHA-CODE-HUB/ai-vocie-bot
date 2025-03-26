# AI Voice Bot

An AI-powered voice bot that dynamically responds to interview questions using conversational AI. The bot represents Adithya S Arangil, an AI/ML Developer with a personalized set of responses based on his professional background.

## Features

- Real-time speech-to-text using OpenAI Whisper
- Natural language understanding and response generation with OpenAI GPT
- Text-to-speech conversion with ElevenLabs
- Interactive chat interface
- Both text and voice input options

## Tech Stack

- **Frontend**: Next.js with TypeScript, Tailwind CSS
- **Backend**: Python FastAPI
- **Speech Processing**: OpenAI Whisper (STT), ElevenLabs (TTS)
- **AI Model**: OpenAI GPT-3.5/4

## Project Structure

```
ai-voice-bot/
├── backend/             # FastAPI server
│   ├── main.py          # Main API endpoints
│   └── requirements.txt # Python dependencies
│
└── frontend/            # Next.js application
    ├── pages/           # React components and pages
    ├── styles/          # CSS styles
    ├── public/          # Static assets
    └── package.json     # JavaScript dependencies
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd ai-voice-bot/backend
   ```

2. Create a virtual environment:
   ```
   py -3.11 venv venv

   venv\Scripts\activate
   ```
   

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the backend directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

6. Start the backend server:
   ```
      python main.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd ai-voice-bot/frontend
   ```

2. Install the required packages:
   ```
   npm install --legacy-peer-deps
   ```

3. Start the development server:
   ```
      npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Type a message in the text box and press enter, or use the microphone button to record your voice
2. The AI will process your input and respond with text and voice
3. Continue the conversation naturally

## Interview Questions

The AI is programmed to provide personalized responses to standard interview questions, including:

1. Life Story Narrative
2. Superpower Definition
3. Growth Areas
4. Workplace Misconceptions
5. Boundary Pushing Approach

## Troubleshooting

### Node.js and npm Installation

If you encounter errors with npm commands not being recognized:
1. Make sure Node.js is installed from https://nodejs.org/
2. Verify installation with `node -v` and `npm -v`
3. Restart your terminal after installation

### PowerShell Execution Policy

If you see errors about execution policy in PowerShell:
1. Open PowerShell as Administrator
2. Run: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
3. Confirm with "Y" when prompted

### React Dependency Conflicts

If you see dependency conflicts with React versions:
1. Use the legacy peer deps flag: `npm install --legacy-peer-deps`
2. Or force installation: `npm install --force`

### Server-Side Rendering Errors

If you encounter errors with "window is not defined":
1. This is expected with components that access browser APIs during SSR
2. The application uses dynamic imports to handle this issue
3. Make sure you're using the latest code with the dynamic import fix

## License

This project is licensed under the MIT License. 