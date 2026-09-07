import { useState } from 'react';
import { Send, UserCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useChat } from '../../context/ChatContext';

export function ChatInput() {
  const { auth, openClaimModal } = useAuth();
  const { sendMessage, isConnected } = useChat();
  const [content, setContent] = useState('');

  const isClaimed = auth?.claimed && auth.member;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || !isClaimed || !isConnected) return;
    sendMessage(content);
    setContent('');
  };

  if (!isClaimed) {
    return (
      <div className="p-4 bg-base-300/60 border-t border-base-content/10 flex flex-col items-center gap-2 text-center">
        <p className="text-xs text-base-content/70">
          You are currently in <strong>read-only mode</strong>.
        </p>
        <button
          onClick={openClaimModal}
          className="btn btn-sm btn-primary gap-2 w-full shadow-sm"
        >
          <UserCheck className="h-4 w-4" />
          Claim Your Name to Chat
        </button>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="p-3 bg-base-300 border-t border-base-content/10 flex items-center gap-2"
    >
      <input
        type="text"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        maxLength={500}
        disabled={!isConnected}
        placeholder={isConnected ? `Chat as ${auth.member?.first_name}...` : 'Connecting to chat...'}
        className="input input-sm md:input-md input-bordered flex-1 bg-base-100 text-sm focus:outline-primary"
      />
      <button
        type="submit"
        disabled={!content.trim() || !isConnected}
        className="btn btn-sm md:btn-md btn-primary btn-square"
        aria-label="Send message"
      >
        <Send className="h-4 w-4" />
      </button>
    </form>
  );
}
