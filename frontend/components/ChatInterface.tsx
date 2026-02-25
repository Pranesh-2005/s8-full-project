'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import Sidebar from './Sidebar';
import { useToast } from '@/hooks/use-toast';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  source?: string;
}

interface GradioMessage {
  role: 'user' | 'assistant';
  metadata: null;
  content: string;
  options: null;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Load messages from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('chat-messages');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setMessages(parsed.map((msg: any) => ({ ...msg, timestamp: new Date(msg.timestamp) })));
      } catch (e) {
        console.error('Failed to load messages:', e);
      }
    }
  }, []);

  // Save messages to localStorage
  useEffect(() => {
    localStorage.setItem('chat-messages', JSON.stringify(messages));
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatHistoryForGradio = (): GradioMessage[] => {
    return messages.map((msg) => ({
      role: msg.role,
      metadata: null,
      content: msg.content,
      options: null,
    }));
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    // Check if running in browser
    if (typeof window === 'undefined') {
      console.error('[v0] API calls must run in browser only');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      console.log('[v0] Starting API call to Hugging Face Space');
      console.log('[v0] User input:', content);

      // Dynamic import - MUST be inside async function to avoid SSR issues
      const { Client } = await import('@gradio/client');
      console.log('[v0] Gradio client imported successfully');

      // Connect to HF Space  
      console.log('[v0] Connecting to Pranesh64/s8-project');
      const client = await Client.connect('Pranesh64/s8-project', {
        // hf_token: process.env.NEXT_PUBLIC_HF_TOKEN || undefined,
      });
      console.log('[v0] Connected to Hugging Face Space');

      const formattedHistory = formatHistoryForGradio();
      console.log('[v0] Formatted history:', formattedHistory.length, 'messages');

      // Call the API
      console.log('[v0] Calling /search_and_answer endpoint');
      const result = await client.predict('/search_and_answer', {
        question: content,
        top_k: 5,
        history: formattedHistory,
      });

      console.log('[v0] API response received:', result);

      let assistantContent = 'I apologize, but I couldn\'t process your question. Please try again.';

      // Handle the new response format
      if (result.data && Array.isArray(result.data)) {
        // result.data[0] contains the updated chat history
        // result.data[1] contains the cleared question field (empty string)
        
        const chatHistory = result.data[0];
        console.log('[v0] Chat history from API:', chatHistory);
        
        if (Array.isArray(chatHistory) && chatHistory.length > 0) {
          // Get the last message from the chat history (should be the assistant's response)
          const lastMessage = chatHistory[chatHistory.length - 1];
          
          if (lastMessage && lastMessage.role === 'assistant' && lastMessage.content) {
            assistantContent = lastMessage.content;
            console.log('[v0] Assistant content extracted:', assistantContent.substring(0, 100) + '...');
          }
        }
      }

      // Create assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: assistantContent,
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      console.log('[v0] Message added to state');
      
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error occurred';
      console.error('[v0] Full error:', error);
      console.error('[v0] API Error:', errorMsg);
      setError(errorMsg);

      // Show helpful error message
      let helpfulMsg = errorMsg;
      if (errorMsg.includes('Failed to fetch')) {
        helpfulMsg = 'Network error: The HF Space server is unreachable. Check your internet connection.';
      } else if (errorMsg.includes('401') || errorMsg.includes('403')) {
        helpfulMsg = 'Authentication error: Your HF_TOKEN may be invalid. Check your environment variables.';
      } else if (errorMsg.includes('404')) {
        helpfulMsg = 'Space not found: Pranesh64/s8-project may not exist or be private.';
      } else if (errorMsg.includes('timeout')) {
        helpfulMsg = 'Request timed out: The server is taking too long to respond. Please try again.';
      }

      toast({
        title: 'Error',
        description: helpfulMsg,
        variant: 'destructive',
      });

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Sorry, I encountered an error: ${helpfulMsg}. Please try again.`,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    localStorage.removeItem('chat-messages');
  };

  const handleNewChat = () => {
    handleClearChat();
  };

  return (
    <div className="flex h-full overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={handleNewChat}
        onClearChat={handleClearChat}
        messagesCount={messages.length}
      />

      {/* Chat Area */}
      <div className="flex flex-col flex-1 w-full">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-4 md:py-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4">
              <div className="text-5xl md:text-6xl">🤖</div>
              <div>
                <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
                  Welcome to AI Document Assistant!
                </h2>
                <p className="text-muted-foreground max-w-sm mx-auto">
                  Ask me anything about your documents. I can help you find information, summarize content, and answer questions.
                </p>
              </div>
              <div className="pt-4 space-y-2 max-w-xs">
                <p className="text-sm text-muted-foreground font-medium">Try asking:</p>
                <div className="space-y-1 text-xs text-muted-foreground">
                  <p>• What are the main topics covered?</p>
                  <p>• Summarize the key findings</p>
                  <p>• Explain the methodology used</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto w-full space-y-4">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-3">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-border bg-card px-4 md:px-8 py-4 md:py-6">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
          </div>
        </div>
      </div>

      {/* Mobile Menu Button */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="md:hidden fixed bottom-20 right-4 w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-lg z-40 hover:bg-primary/90 transition-colors"
          aria-label="Open menu"
        >
          ☰
        </button>
      )}
    </div>
  );
}