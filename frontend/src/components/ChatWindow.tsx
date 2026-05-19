'use client';
import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, AlertTriangle, Loader2 } from 'lucide-react';
import RiskBadge from './RiskBadge';
import ConfidenceBadge from './ConfidenceBadge';
import CitationCard from './CitationCard';
import api from '@/lib/api';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
  confidence_score?: number;
  risk_level?: string;
  requires_human_review?: boolean;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/api/chat/query', {
        question: userMessage.content,
        session_id: sessionId,
      });

      const data = res.data;
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        confidence_score: data.confidence_score,
        risk_level: data.risk_level,
        requires_human_review: data.requires_human_review,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-lg shadow-sm border border-slate-200">
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <Bot className="w-12 h-12 mb-4 text-blue-200" />
            <p>Hello! I am DocuGuard AI. Ask me questions about your documents.</p>
          </div>
        )}
        
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-blue-600" />
              </div>
            )}
            
            <div className={`max-w-[80%] rounded-2xl px-5 py-4 ${
              msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-50 border border-slate-200 text-slate-800'
            }`}>
              <div className="whitespace-pre-wrap">{msg.content}</div>
              
              {msg.role === 'assistant' && (
                <div className="mt-4 space-y-4">
                  {(msg.risk_level || msg.confidence_score !== undefined) && (
                    <div className="flex flex-wrap gap-2 pt-3 border-t border-slate-200">
                      {msg.risk_level && <RiskBadge level={msg.risk_level} />}
                      {msg.confidence_score !== undefined && <ConfidenceBadge score={msg.confidence_score} />}
                      {msg.requires_human_review && (
                        <span className="flex items-center gap-1 text-xs font-medium text-orange-600 bg-orange-50 px-2 py-0.5 rounded-full border border-orange-200">
                          <AlertTriangle className="w-3 h-3" />
                          Human Review Needed
                        </span>
                      )}
                    </div>
                  )}
                  
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="pt-2">
                      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Sources</p>
                      <div className="space-y-2">
                        {msg.citations.map((cit, idx) => (
                          <CitationCard key={idx} citation={cit} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-slate-600" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-4 justify-start">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-blue-600" />
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 flex items-center gap-2 text-slate-500">
              <Loader2 className="w-4 h-4 animate-spin" /> Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-slate-200 bg-slate-50 rounded-b-lg">
        <form onSubmit={handleSend} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="w-full pl-4 pr-12 py-3 rounded-full border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
