import { request } from './client';
import { ChatMessageResponse } from '../types';

export const chatApi = {
  /** Fetch paginated chat history */
  getHistory: (limit = 50, offset = 0) =>
    request<ChatMessageResponse[]>(`/api/chat/history?limit=${limit}&offset=${offset}`),
};
