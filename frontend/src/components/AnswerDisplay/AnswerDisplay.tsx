import React from 'react';

interface AnswerDisplayProps {
  answer: string | null;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ answer }) => {
  if (!answer) return null;

  return (
    <div className="p-4 mt-4 bg-gray-50 rounded-lg">
      <h2 className="mb-2 text-lg font-semibold">Answer:</h2>
      <p className="text-gray-700">{answer}</p>
    </div>
  );
}; 