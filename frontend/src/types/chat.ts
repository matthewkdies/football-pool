export interface ChatMessageResponse {
  id: number;
  member_id: number;
  author_name: string;
  content: string;
  created_at: string;
}

export interface WSChatBroadcastMessage {
  type: 'chat_message';
  id: number;
  member_id: number;
  author_name: string;
  content: string;
  created_at: string;
}

export interface WSChatErrorMessage {
  type: 'error';
  message: string;
}

export type WSChatMessage = WSChatBroadcastMessage | WSChatErrorMessage;
