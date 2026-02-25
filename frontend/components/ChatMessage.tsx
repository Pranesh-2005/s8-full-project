'use client';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  source?: string;
}

export default function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`flex gap-3 max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}
      >
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm ${
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-accent text-accent-foreground'
          }`}
        >
          {isUser ? '👤' : '🤖'}
        </div>

        {/* Message Bubble */}
        <div className="flex flex-col gap-1">
          <div
            className={`rounded-2xl px-4 py-3 break-words ${
              isUser
                ? 'bg-primary text-primary-foreground rounded-tr-sm'
                : 'bg-muted text-foreground rounded-tl-sm'
            }`}
          >
            <p className="text-sm md:text-base whitespace-pre-wrap">{message.content}</p>
          </div>

          {/* Timestamp and Source */}
          <div className={`flex items-center gap-2 text-xs text-muted-foreground px-2 ${
            isUser ? 'justify-end' : 'justify-start'
          }`}>
            <span>{formatTime(message.timestamp)}</span>
            {message.source && !isUser && (
              <span className="text-accent">📌 Source: {message.source}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
