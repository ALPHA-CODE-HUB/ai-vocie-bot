import { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import { FaMicrophone } from 'react-icons/fa';
import { IoMdPulse } from 'react-icons/io';
import api from '../utils/api';

// Interface for message objects
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

// Add type declaration for SpeechRecognition
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export default function Home() {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioSrc, setAudioSrc] = useState<string | null>(null);
  const [transcribedText, setTranscribedText] = useState('');
  const audioRef = useRef<HTMLAudioElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';
        
        recognitionRef.current.onresult = (event: any) => {
          let interimTranscript = '';
          let finalTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }
          
          setTranscribedText(finalTranscript || interimTranscript);
        };
        
        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error', event.error);
          setIsRecording(false);
        };
        
        recognitionRef.current.onend = () => {
          if (isRecording) {
            recognitionRef.current.start();
          }
        };
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Play audio when available
  useEffect(() => {
    if (audioSrc && audioRef.current) {
      audioRef.current.play();
    }
  }, [audioSrc]);

  // Start recording on mouse down
  const startRecording = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser');
      return;
    }
    
    try {
      recognitionRef.current.start();
      setIsRecording(true);
      setTranscribedText('');
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };
  
  // Stop recording on mouse up
  const stopRecording = async () => {
    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
      
      if (transcribedText.trim()) {
        await handleSendMessage(transcribedText);
      }
    }
  };

  // Handle sending a message
  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isProcessing) return;
    
    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setTranscribedText('');
    setIsProcessing(true);
    
    try {
      const history = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      const aiResponse = await api.generateText(text, history);
      setMessages(prev => [...prev, { role: 'assistant', content: aiResponse }]);
      
      const audioBlob = await api.textToSpeech(aiResponse);
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudioSrc(audioUrl);
    } catch (error) {
      console.error('Error processing message:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error processing your request. Please try again.'
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col">
      <Head>
        <title>AI Voice Assistant</title>
        <meta name="description" content="Your personal AI voice assistant" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="bg-black/30 backdrop-blur-sm border-b border-gray-800">
        <div className="max-w-4xl mx-auto py-4 px-4 flex items-center">
          <div className="flex-shrink-0 mr-4">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
              <IoMdPulse className="h-6 w-6 text-white" />
            </div>
          </div>
          <h1 className="text-xl font-semibold text-white">
            Voice Chat Assistant
          </h1>
        </div>
      </header>

      <main className="flex-grow p-4 flex items-center justify-center">
        <div className="w-full max-w-4xl bg-gray-900/50 backdrop-blur-md rounded-lg border border-gray-800 overflow-hidden flex flex-col h-[calc(100vh-8rem)]">
          {/* Chat Area */}
          <div 
            ref={chatContainerRef}
            className="flex-grow p-4 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent"
          >
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
                <div className="w-16 h-16 mb-4 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
                  <IoMdPulse className="h-8 w-8 text-white" />
                </div>
                <p className="text-lg font-medium mb-2">Welcome to Voice Chat Assistant</p>
                <p className="text-sm text-gray-500">Press and hold the microphone button to start speaking</p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`my-2 ${
                    message.role === 'user' ? 'ml-auto' : 'mr-auto'
                  }`}
                >
                  <div className={`max-w-[80%] p-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-100'
                  }`}>
                    {message.content}
                  </div>
                </div>
              ))
            )}
            {isProcessing && (
              <div className="flex justify-center my-4">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            )}
          </div>

          {/* Microphone Button */}
          <div className="p-4 border-t border-gray-800 flex justify-center items-center">
            {isRecording && (
              <div className="absolute transform -translate-y-16 bg-gray-800 px-4 py-2 rounded-lg text-sm text-gray-300">
                {transcribedText || "Listening..."}
              </div>
            )}
            <button
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onMouseLeave={stopRecording}
              onTouchStart={startRecording}
              onTouchEnd={stopRecording}
              disabled={isProcessing}
              className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200 ${
                isRecording 
                  ? 'bg-red-500 scale-110' 
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              <FaMicrophone className={`text-white text-xl ${isRecording ? 'animate-pulse' : ''}`} />
            </button>
          </div>
        </div>
      </main>

      {/* Hidden audio element */}
      <audio ref={audioRef} src={audioSrc || ''} className="hidden" />
      
      {/* Custom scrollbar style */}
      <style jsx global>{`
        .scrollbar-thin::-webkit-scrollbar {
          width: 4px;
        }
        .scrollbar-thin::-webkit-scrollbar-track {
          background: transparent;
        }
        .scrollbar-thin::-webkit-scrollbar-thumb {
          background-color: rgba(107, 114, 128, 0.5);
          border-radius: 2px;
        }
      `}</style>
    </div>
  );
} 