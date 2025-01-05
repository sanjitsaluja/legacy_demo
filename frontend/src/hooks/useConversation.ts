import { useState, useCallback } from 'react';
import { generateAnswer } from '../services/api';
import { ConversationState } from '../types';

export const useConversation = () => {
  const [state, setState] = useState<ConversationState>({
    currentQuestion: '',
    currentAnswer: null,
    isLoading: false,
    error: null,
  });

  const setQuestion = useCallback((question: string) => {
    setState(prev => ({ ...prev, currentQuestion: question }));
  }, []);

  const submitQuestion = useCallback(async () => {
    if (!state.currentQuestion.trim()) {
      setState(prev => ({ ...prev, error: 'Please enter a question' }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const answer = await generateAnswer(state.currentQuestion);
      setState(prev => ({
        ...prev,
        currentAnswer: answer,
        isLoading: false,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'An error occurred',
        isLoading: false,
      }));
    }
  }, [state.currentQuestion]);

  return {
    ...state,
    setQuestion,
    submitQuestion,
  };
}; 