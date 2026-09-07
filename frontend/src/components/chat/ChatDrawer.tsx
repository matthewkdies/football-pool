import { useEffect, useRef } from 'react';
import { MessageSquare, X, Wifi, WifiOff } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useAuth } from '../../context/AuthContext';
import { ChatMessageItem } from './ChatMessageItem';
import { ChatInput } from './ChatInput';

export function ChatDrawer() {
  const { isChatOpen, closeChat, messages, isConnected } = useChat();
  const { auth } = useAuth();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new message
  useEffect(() => {
    if (isChatOpen && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isChatOpen]);

  if (!isChatOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
        onClick={closeChat}
      />

      {/* Slide-over panel */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <aside
          aria-label="Family chat"
          className="w-screen max-w-md bg-base-200 shadow-2xl border-l border-base-content/10 flex flex-col"
        >
          {/* Header */}
          <div className="p-4 bg-base-300 border-b border-base-content/10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 text-primary rounded-lg">
                <MessageSquare className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-base leading-tight">Pool Chat</h3>
                <div className="flex items-center gap-1.5 text-xs">
                  {isConnected ? (
                    <span className="flex items-center gap-1 text-success">
                      <Wifi className="h-3 w-3" /> Live
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-error">
                      <WifiOff className="h-3 w-3" /> Connecting...
                    </span>
                  )}
                  <span className="opacity-50">·</span>
                  <span className="opacity-70">{messages.length} messages</span>
                </div>
              </div>
            </div>

            <button
              onClick={closeChat}
              className="btn btn-sm btn-circle btn-ghost"
              aria-label="Close chat"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Messages list */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 bg-base-100"
          >
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 opacity-60">
                <MessageSquare className="h-10 w-10 mb-2 opacity-40" />
                <p className="font-semibold text-sm">No messages yet!</p>
                <p className="text-xs mt-1">Start the game day banter with the family.</p>
              </div>
            ) : (
              messages.map((msg) => (
                <ChatMessageItem
                  key={msg.id}
                  message={msg}
                  isCurrentUser={auth?.claimed ? auth.member?.id === msg.member_id : false}
                />
              ))
            )}
          </div>

          {/* Input Area */}
          <ChatInput />
        </aside>
      </div>
    </div>
  );
}
