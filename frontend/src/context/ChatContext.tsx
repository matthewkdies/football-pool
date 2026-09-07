import { createContext, useContext, useState, useEffect, useRef, ReactNode, useCallback } from 'react';
import { ChatMessageResponse, WSChatMessage } from '../types';
import { chatApi } from '../api/chatApi';

interface ChatContextType {
  messages: ChatMessageResponse[];
  isConnected: boolean;
  isChatOpen: boolean;
  unreadCount: number;
  openChat: () => void;
  closeChat: () => void;
  toggleChat: () => void;
  sendMessage: (content: string) => void;
  loadHistory: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ChatMessageResponse[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const [unreadCount, setUnreadCount] = useState<number>(0);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const backoffRef = useRef<number>(1000);
  const isChatOpenRef = useRef<boolean>(isChatOpen);

  useEffect(() => {
    isChatOpenRef.current = isChatOpen;
    if (isChatOpen) {
      setUnreadCount(0);
    }
  }, [isChatOpen]);

  const loadHistory = useCallback(async () => {
    try {
      const history = await chatApi.getHistory(50);
      // History is returned newest-first from backend, sort oldest-first for chat display
      const sorted = [...history].sort(
        (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setMessages(sorted);
    } catch {
      // Ignore or log error
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    if (socketRef.current && (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/chat`;

    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        backoffRef.current = 1000; // Reset backoff on successful connect
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WSChatMessage;
          if (data.type === 'chat_message') {
            const newMsg: ChatMessageResponse = {
              id: data.id,
              member_id: data.member_id,
              author_name: data.author_name,
              content: data.content,
              created_at: data.created_at,
            };

            setMessages((prev) => {
              // Avoid duplicate messages if already present
              if (prev.some((m) => m.id === newMsg.id)) {
                return prev;
              }
              return [...prev, newMsg];
            });

            if (!isChatOpenRef.current) {
              setUnreadCount((prev) => prev + 1);
            }
          }
        } catch {
          // invalid JSON or error payload
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        socketRef.current = null;
        // Schedule reconnect
        const delay = Math.min(backoffRef.current, 15000);
        reconnectTimeoutRef.current = setTimeout(() => {
          backoffRef.current = Math.min(backoffRef.current * 1.5, 15000);
          connectWebSocket();
        }, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
    connectWebSocket();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [loadHistory, connectWebSocket]);

  const sendMessage = (content: string) => {
    if (!content.trim() || !socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      return;
    }
    socketRef.current.send(JSON.stringify({ content: content.trim() }));
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        isConnected,
        isChatOpen,
        unreadCount,
        openChat: () => setIsChatOpen(true),
        closeChat: () => setIsChatOpen(false),
        toggleChat: () => setIsChatOpen((prev) => !prev),
        sendMessage,
        loadHistory,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat(): ChatContextType {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
