import React from 'react';

const AudioFallback: React.FC = () => {
  return (
    <div className="w-full h-12 rounded-md bg-gray-200 flex items-center justify-center">
      <p className="text-gray-500 text-sm">Audio recorder loading...</p>
    </div>
  );
};

export default AudioFallback; 