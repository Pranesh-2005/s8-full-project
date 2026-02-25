'use client';

import { useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onClearChat: () => void;
  messagesCount: number;
}

export default function Sidebar({
  isOpen,
  onClose,
  onNewChat,
  onClearChat,
  messagesCount,
}: SidebarProps) {
  const sidebarRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        sidebarRef.current &&
        !sidebarRef.current.contains(event.target as Node) &&
        isOpen
      ) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 md:hidden z-30"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        ref={sidebarRef}
        className={`fixed md:relative w-64 h-full bg-sidebar text-sidebar-foreground border-r border-sidebar-border flex flex-col transition-transform duration-300 ease-in-out z-40 md:z-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-sidebar-border">
          <h2 className="font-bold text-lg">Chat History</h2>
          <button
            onClick={onClose}
            className="md:hidden p-2 hover:bg-sidebar-accent rounded-lg transition-colors"
            aria-label="Close sidebar"
          >
            ✕
          </button>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {/* New Chat Button */}
          <Button
            onClick={() => {
              onNewChat();
              onClose();
            }}
            className="w-full bg-sidebar-primary hover:bg-sidebar-primary/90 text-sidebar-primary-foreground rounded-lg py-6 font-medium"
          >
            + New Chat
          </Button>

          {/* Chat Info */}
          <div className="bg-sidebar-accent/20 rounded-lg p-4 space-y-2">
            <p className="text-sm text-sidebar-foreground font-medium">Current Session</p>
            <p className="text-xs text-sidebar-foreground/70">
              {messagesCount} message{messagesCount !== 1 ? 's' : ''} in this chat
            </p>
          </div>

          {/* Quick Actions */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-sidebar-foreground/70 uppercase tracking-wide">
              Quick Actions
            </p>
            <div className="space-y-2">
              <button
                onClick={() => {
                  onClearChat();
                  onClose();
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-sidebar-accent/20 transition-colors text-sidebar-foreground"
              >
                🗑️ Clear Chat
              </button>
              <button
                onClick={() => {
                  const element = document.createElement('a');
                  element.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent('Chat History');
                  element.download = `chat-${new Date().toISOString().split('T')[0]}.txt`;
                  element.click();
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-sidebar-accent/20 transition-colors text-sidebar-foreground"
              >
                💾 Export Chat
              </button>
            </div>
          </div>

          {/* Info Section */}
          <div className="bg-sidebar-accent/10 rounded-lg p-4 space-y-3 mt-auto">
            <h3 className="font-semibold text-sm text-sidebar-foreground">About StudyBot</h3>
            <ul className="text-xs text-sidebar-foreground/70 space-y-2">
              <li className="flex gap-2">
                <span>📚</span>
                <span>Get instant answers to study questions</span>
              </li>
              <li className="flex gap-2">
                <span>💡</span>
                <span>Learn at your own pace</span>
              </li>
              <li className="flex gap-2">
                <span>🚀</span>
                <span>Works offline as a PWA app</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-sidebar-border px-4 py-4 text-xs text-sidebar-foreground/60 text-center">
          <p>StudyBot AI v1.0</p>
          <p className="mt-1">Your personal learning companion</p>
        </div>
      </div>
    </>
  );
}
