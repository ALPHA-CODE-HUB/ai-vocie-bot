import axios from 'axios';

// Define interface for conversation history
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API client configuration
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const transcribeAudio = async (audioBlob: Blob): Promise<string> => {
    const formData = new FormData();
    formData.append('file', audioBlob);

    const response = await fetch(`${API_URL}/transcribe`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('Failed to transcribe audio');
    }

    const data = await response.json();
    return data.text;
};

export const generateResponse = async (message: string): Promise<string> => {
    const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
    });

    if (!response.ok) {
        throw new Error('Failed to generate response');
    }

    const data = await response.json();
    return data.response;
};

export const generateSpeech = async (text: string): Promise<ArrayBuffer> => {
    const response = await fetch(`${API_URL}/speak`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
    });

    if (!response.ok) {
        throw new Error('Failed to generate speech');
    }

    return response.arrayBuffer();
};

const api = {
  generateText: async (message: string, conversationHistory: any[]) => {
    const response = await axios.post(`${API_URL}/api/generate-text`, {
      message,
      conversation_history: conversationHistory
    });
    return response.data.response;
  },

  textToSpeech: async (text: string) => {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await axios.post(`${API_URL}/api/text-to-speech`, formData, {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default api; 