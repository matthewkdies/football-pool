import { useState } from 'react';
import { Send, UserCheck, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useChat } from '../../context/ChatContext';

export function ChatInput() {
  const { auth, openClaimModal } = useAuth();
  const { sendMessage, isConnected } = useChat();
  const [content, setContent] = useState('');
  const [isSending, setIsSending] = useState(false);

  const isClaimed = auth?.claimed && auth.member;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || !isClaimed || isSending) return;
    const textToSend = content;
    setContent('');
    setIsSending(true);
    try {
      await sendMessage(textToSend);
    } catch {
      setContent(textToSend); // Restore input if send fails
    } finally {
      setIsSending(false);
    }
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
        disabled={isSending}
        placeholder={isConnected ? `Chat as ${auth.member?.first_name}...` : `Chat as ${auth.member?.first_name}...`}
        className="input input-sm md:input-md input-bordered flex-1 bg-base-100 text-sm focus:outline-primary"
      />
      <button
        type="submit"
        disabled={!content.trim() || isSending}
        className="btn btn-sm md:btn-md btn-primary btn-square"
        aria-label="Send message"
      >
        {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
      </button>
    </form>
  );
}
