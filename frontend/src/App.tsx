import React from 'react';
import { QuestionInput } from './components/QuestionInput/QuestionInput';
import { LoadingIndicator } from './components/LoadingIndicator/LoadingIndicator';
import { AnswerDisplay } from './components/AnswerDisplay/AnswerDisplay';
import { useConversation } from './hooks/useConversation';

const App: React.FC = () => {
  const {
    currentQuestion,
    currentAnswer,
    isLoading,
    error,
    setQuestion,
    submitQuestion,
  } = useConversation();

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container max-w-3xl px-4 py-8 mx-auto">
        <h1 className="mb-8 text-3xl font-bold text-center">
          Mental Health Assistant
        </h1>
        
        <div className="p-6 bg-white rounded-lg shadow-md">
          <QuestionInput
            value={currentQuestion}
            onChange={setQuestion}
            onSubmit={submitQuestion}
            disabled={isLoading}
          />
          
          {error && (
            <div className="p-3 mt-4 text-red-700 bg-red-100 rounded-lg">
              {error}
            </div>
          )}
          
          {isLoading && <LoadingIndicator />}
          
          <AnswerDisplay answer={currentAnswer} />
        </div>
      </div>
    </div>
  );
};

export default App; 