import { ChatMessageResponse } from '../../types';

interface ChatMessageItemProps {
  message: ChatMessageResponse;
  isCurrentUser: boolean;
}

export function ChatMessageItem({ message, isCurrentUser }: ChatMessageItemProps) {
  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className={`chat ${isCurrentUser ? 'chat-end' : 'chat-start'}`}>
      <div className="chat-header text-xs opacity-70 mb-1 flex items-center gap-1">
        <span className="font-semibold">{message.author_name}</span>
        <time className="text-[10px] opacity-60">{formatTime(message.created_at)}</time>
      </div>
      <div
        className={`chat-bubble text-sm break-words leading-relaxed ${
          isCurrentUser
            ? 'chat-bubble-primary text-primary-content shadow-sm'
            : 'chat-bubble-neutral bg-base-300 text-base-content border border-base-content/10 shadow-sm'
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
