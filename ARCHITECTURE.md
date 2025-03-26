# Technical Architecture: Home.LLC AI Voice Bot

## System Overview

The Home.LLC AI Voice Bot is designed as a distributed system with a clear separation between the frontend user interface and the backend AI processing components. This architecture enables scalability, maintainable code, and performance optimization.

## Component Diagram

```
┌─────────────────┐         ┌────────────────────┐         ┌─────────────────┐
│    Frontend     │         │      Backend       │         │  External APIs  │
│   (Next.js)     │ ◄─────► │     (FastAPI)      │ ◄─────► │ (OpenAI, etc.)  │
└─────────────────┘         └────────────────────┘         └─────────────────┘
       ▲                             ▲
       │                             │
       │                             │
       ▼                             ▼
┌─────────────────┐         ┌────────────────────┐
│   UI Components │         │  AI Processing     │
│   Interaction   │         │  Speech Services   │
└─────────────────┘         └────────────────────┘
```

## Key Components

### 1. Frontend Layer

- **Framework**: Next.js with TypeScript
- **State Management**: React Hooks for local state management
- **UI Components**:
  - Chat Interface (message display, input controls)
  - Audio Recording Component (ReactMic)
  - Audio Playback Component (HTML5 Audio)
- **Styling**: Tailwind CSS for responsive design

### 2. Backend Layer

- **Framework**: FastAPI (Python)
- **Core Modules**:
  - API Endpoints
  - Conversation Management
  - Personality Configuration
  - Error Handling

### 3. AI Processing Pipeline

#### Speech-to-Text Flow
1. User audio captured via browser
2. Audio sent to backend via API
3. Backend forwards to OpenAI Whisper API
4. Transcribed text returned to backend
5. Text forwarded to frontend for display

#### Text Processing Flow
1. User text input (typed or transcribed)
2. Text sent to backend
3. Context and conversation history added
4. Query processed by OpenAI GPT
5. Response text generated
6. Response returned to frontend

#### Text-to-Speech Flow
1. AI response text received
2. Text sent to ElevenLabs API
3. Generated audio returned
4. Audio streamed to browser
5. Audio played through user's device

## Data Flow

1. **User Input**: 
   - Text input via form
   - Audio input via microphone
   
2. **Backend Processing**:
   - Speech-to-Text conversion
   - Context enrichment
   - Response generation
   - Text-to-Speech conversion
   
3. **Response Delivery**:
   - Text displayed in chat interface
   - Audio played through browser

## Persona Configuration

The AI personality is defined in a central configuration within the backend:

- **System Prompt**: Defines core personality attributes
- **Context Management**: Maintains conversation history
- **Response Templates**: Pre-defined patterns for common questions

## Scalability Considerations

- **API Rate Limiting**: Controls request frequency to external services
- **Caching**: Common responses can be cached for performance
- **Stateless Design**: Backend maintains minimal state for horizontal scaling

## Security Measures

- **API Key Protection**: Environment variables for secure key storage
- **Input Validation**: All user inputs validated before processing
- **CORS Configuration**: Properly restricted cross-origin resource sharing

## Development Workflow

1. Local development with hot reloading
2. Backend and frontend run on separate ports
3. API proxy configuration for seamless integration

## Deployment Options

- **Containerization**: Docker for consistent environments
- **Hosting**: Can be deployed on Vercel (frontend) and Python-compatible hosts (backend)
- **CI/CD**: Automated testing and deployment pipelines 