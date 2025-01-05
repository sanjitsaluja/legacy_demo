import axios from 'axios';
import { ApiResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

export const generateAnswer = async (question: string): Promise<string> => {
  try {
    const response = await axios.post<ApiResponse>(
      `${API_BASE_URL}/conversations/generate`,
      { question },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data.answer;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.error || 'Failed to generate answer');
    }
    throw error;
  }
}; 