import React from 'react';
import ReactMarkdown from 'react-markdown';

interface AnswerDisplayProps {
  answer: string | null;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ answer }) => {
  if (!answer) return null;

  return (
    <div className="p-4 mt-4 bg-gray-50 rounded-lg">
      <h2 className="mb-2 text-lg font-semibold">Answer:</h2>
      <div className="prose prose-sm max-w-none text-gray-700">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>
    </div>
  );
}; 