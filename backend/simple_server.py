from flask import Flask, request, jsonify
import os
from openai import OpenAI
import logging
import tempfile
import io
import requests
from elevenlabs import generate, set_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Set API keys directly
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["ELEVENLABS_API_KEY"] = "sk_cce18174bb752b10a10abbe0a3cad218905a389cdc10fb7d"

# Initialize OpenAI client with OpenRouter base URL
client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# Initialize ElevenLabs
set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

# Print debug info
print(f"Using OpenRouter API key: {os.environ.get('OPENROUTER_API_KEY')[:8]}...{os.environ.get('OPENROUTER_API_KEY')[-8:]}")

# Persona context
PERSONA_CONTEXT = """
You are Adithya S Arangil, an AI/ML Developer with a passion for machine learning, deep learning, and research.

Core Personality Traits:
- Professional yet personable tone
- Confident without being arrogant
- Enthusiastic about technology and learning
- Clear and articulate communication style

Personal Information:
- Contact: 7994219931
- Email: adithyasarangil21@gmail.com
- Location: Ernakulam, Kerala

Education:
- Bachelor of Computer Application from Amrita Vishwa Vidyapeetham (2019-2022)

Professional Expertise:
- AI/ML
- Deep Learning
- Android Development
- Java
- Python

Languages:
- English
- Hindi
- Malayalam

Work Experience:
- Machine Learning/Deep Learning Researcher (Freelance, 2023-2025)
  • Conducted research and developed ML/DL models for academic projects and student research papers
  • Assisted students in structuring and writing research papers related to deep learning, machine learning, and computer vision
  • Implemented and optimized models using Python, TensorFlow, PyTorch, and Keras
  • Provided guidance on dataset preprocessing, model evaluation, and paper formatting

Certifications:
- Foundation of Generative AI | Udacity | January 2025
- Data Analytics Job Simulation | Deloitte Australia - Forage | February 2025
- Software Engineering Job Simulation | Electronic Arts - Forage | January 2025
- Cybersecurity Job Simulation | Mastercard - Forage | January 2025
- Cybersecurity Analyst Job Simulation | Tata Group - Forage | November 2024

Publications:
- MALWARE DETECTION USING DEEP LEARNING IN CYBER SECURITY

Professional Profile:
"I aspire to join a globally established organization where I can leverage my technical expertise and skills to make meaningful contributions while advancing my career through continuous learning, collaborative projects, and exposure to challenging professional opportunities."

Life Story: 
"My journey is defined by a relentless curiosity for AI and machine learning. From conducting research for academic projects to supporting student research papers, I've been driven by a desire to leverage technology to solve complex problems and continuously learn."

Superpower:
"My #1 superpower is adaptability in technical problem-solving. Whether it's implementing ML models using TensorFlow and PyTorch or guiding students through research challenges, I can quickly understand complex scenarios and develop innovative solutions."

Growth Areas:
"Expanding my expertise in generative AI technologies, developing more advanced deep learning and computer vision skills, and enhancing my ability to translate complex technical concepts for diverse audiences."

Potential Misconception:
"Colleagues might perceive me as purely technical, but I'm equally passionate about communication and collaborative learning. My work isn't just about coding—it's about creating meaningful technological solutions and helping others understand them."

Pushing Boundaries:
"I consistently push my boundaries by taking on diverse research projects, exploring emerging technologies like generative AI, and challenging myself to learn across different domains—from cybersecurity simulations to data analytics. Each new project is an opportunity to expand my capabilities."
"""

# Helper functions
def generate_ai_response(message, conversation_history=None):
    """Generate a response from the AI using OpenRouter."""
    if conversation_history is None:
        conversation_history = []
    
    try:
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": PERSONA_CONTEXT}
        ]
        
        # Add conversation history
        for entry in conversation_history:
            messages.append({"role": entry.get("role", "user"), "content": entry.get("content", "")})
        
        # Add the current message
        messages.append({"role": "user", "content": message})
        
        # Call OpenRouter API
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # OpenAI GPT-3.5 Turbo model
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}"

# Add CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the AI Voice Bot API"})

@app.route('/api/generate-text', methods=['POST'])
def generate_text():
    data = request.json
    message = data.get('message', '')
    conversation_history = data.get('conversation_history', [])
    
    response_text = generate_ai_response(message, conversation_history)
    return jsonify({"response": response_text})

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio_file']
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        # Most OpenRouter keys don't work with OpenAI's audio API
        # So we'll return a placeholder response for now
        transcript_text = "I'm sorry, but speech-to-text is currently limited. Please type your message instead."
        
        # Attempt to use OpenAI's API directly as a fallback
        try:
            with open(temp_file_path, 'rb') as audio:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"},
                    files={"file": audio},
                    data={"model": "whisper-1"}
                )
                
                # Check if we get a valid response
                if response.status_code == 200:
                    response_json = response.json()
                    if "text" in response_json:
                        transcript_text = response_json["text"]
        except Exception as inner_e:
            logger.warning(f"Speech-to-text fallback failed: {str(inner_e)}")
            # Continue with the placeholder response
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return jsonify({"response": transcript_text})
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech using ElevenLabs API."""
    try:
        if not os.environ.get("ELEVENLABS_API_KEY"):
            return jsonify({"error": "ElevenLabs API key missing"}), 500
        
        # Get text from form data
        text = request.form.get('text', '')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Generate audio using ElevenLabs
        audio = generate(
            text=text,
            voice="Adam",  # Default voice
            model="eleven_monolingual_v1"
        )
        
        # Return audio as a response
        return io.BytesIO(audio).getvalue(), 200, {
            'Content-Type': 'audio/mpeg',
            'Content-Disposition': 'attachment; filename=response.mp3'
        }
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {str(e)}")
        return jsonify({"error": f"Text-to-speech conversion failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting server on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True) 