'use client';

import { useState, useEffect } from 'react';
import ChatInterface from '@/components/ChatInterface';
import ThemeToggle from '@/components/ThemeToggle';

export default function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      <header className="flex items-center justify-between h-16 px-4 md:px-6 border-b border-border bg-card">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold">
            📚
          </div>
          <div className="hidden sm:block">
            <h1 className="text-lg md:text-xl font-bold text-foreground">StudyBot AI</h1>
            <p className="text-xs text-muted-foreground">Your AI Learning Assistant</p>
          </div>
        </div>
        <ThemeToggle />
      </header>

      <main className="flex-1 overflow-hidden">
        <ChatInterface />
      </main>
    </div>
  );
}
