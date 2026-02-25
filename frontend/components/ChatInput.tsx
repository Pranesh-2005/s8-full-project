'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSendMessage, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = e.target;
    setInput(textarea.value);

    // Auto-resize textarea
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 120);
    textarea.style.height = `${newHeight}px`;
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="flex gap-2 items-end">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything about your studies..."
          disabled={disabled}
          className="flex-1 px-4 py-3 rounded-xl border border-border bg-input text-foreground placeholder-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed max-h-[120px]"
          rows={1}
        />
        <Button
          type="submit"
          disabled={disabled || !input.trim()}
          size="icon"
          className="h-10 w-10 md:h-11 md:w-11 rounded-lg flex-shrink-0 bg-primary hover:bg-primary/90 text-primary-foreground"
          aria-label="Send message"
        >
          <span className="text-lg md:text-xl">➤</span>
        </Button>
      </div>

      <div className="flex gap-2 flex-wrap text-xs text-muted-foreground">
        <span className="inline-flex items-center gap-1">
          💡 Tip: Press Shift + Enter for new line
        </span>
      </div>
    </form>
  );
}
