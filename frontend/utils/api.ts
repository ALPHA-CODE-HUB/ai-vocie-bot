import axios from 'axios';

// Define interface for conversation history
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// API client configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const speechToText = async (audioBlob: Blob): Promise<string> => {
  try {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.wav');
    
    const response = await apiClient.post('/api/speech-to-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data.response;
  } catch (error) {
    console.error('Error in speech-to-text conversion:', error);
    throw new Error('Failed to convert speech to text');
  }
};

const api = {
  generateText: async (message: string, conversationHistory: any[]) => {
    const response = await axios.post(`${API_BASE_URL}/api/generate-text`, {
      message,
      conversation_history: conversationHistory
    });
    return response.data.response;
  },

  textToSpeech: async (text: string) => {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await axios.post(`${API_BASE_URL}/api/text-to-speech`, formData, {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default api; 