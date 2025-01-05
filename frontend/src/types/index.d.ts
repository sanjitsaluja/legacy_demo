export interface ApiResponse {
  answer: string;
}

export interface Conversation {
  question: string;
  answer: string | null;
}

export interface ConversationState {
  currentQuestion: string;
  currentAnswer: string | null;
  isLoading: boolean;
  error: string | null;
} 