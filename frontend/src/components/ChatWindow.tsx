'use client';
import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, AlertTriangle, Loader2, ChevronDown, ChevronUp, FileText } from 'lucide-react';
import RiskBadge from './RiskBadge';
import ConfidenceBadge from './ConfidenceBadge';
import CitationCard from './CitationCard';
import SourceSnippet from './SourceSnippet';
import api from '@/lib/api';

interface RetrievedChunk {
  score: number;
  document_id: number;
  chunk_id: number;
  filename: string;
  page_number: number;
  content_preview?: string;
  access_level?: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
  confidence_score?: number;
  risk_level?: string;
  requires_human_review?: boolean;
  retrieved_chunks?: RetrievedChunk[];
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | undefined>();
  const [expandedChunks, setExpandedChunks] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleChunks = (msgId: string) => {
    setExpandedChunks((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

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
        retrieved_chunks: data.retrieved_chunks,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please check if the backend service is running.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Conversation Thread */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 max-w-md mx-auto text-center">
            <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 border border-blue-100">
              <Bot className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold text-slate-800">DocuGuard AI Assistant</h3>
            <p className="text-sm text-slate-500 mt-1">
              Ask questions regarding your indexed corporate policies, legal documents, or security guidelines. All responses will be dynamically annotated with confidence levels and verified citations.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-9 h-9 rounded-xl bg-blue-100 border border-blue-200 flex items-center justify-center flex-shrink-0 shadow-sm">
                <Bot className="w-5 h-5 text-blue-600" />
              </div>
            )}

            <div className={`max-w-[75%] rounded-2xl p-5 shadow-sm ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white font-medium rounded-tr-none'
                : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
            }`}>
              <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>

              {msg.role === 'assistant' && (
                <div className="mt-4 space-y-4 pt-4 border-t border-slate-100">
                  
                  {/* Warning Box for Human Review */}
                  {msg.requires_human_review && (
                    <div className="flex items-start gap-2.5 p-3.5 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 text-xs font-medium">
                      <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-amber-800">Warning: Human Review Recommended</p>
                        <p className="text-amber-700/90 mt-0.5">This response has triggered security policies or failed confidence scoring checks. Manual audit is advised.</p>
                      </div>
                    </div>
                  )}

                  {/* Metadata Indicators */}
                  {(msg.risk_level || msg.confidence_score !== undefined) && (
                    <div className="flex flex-wrap gap-2">
                      {msg.risk_level && <RiskBadge level={msg.risk_level} />}
                      {msg.confidence_score !== undefined && <ConfidenceBadge score={msg.confidence_score} />}
                    </div>
                  )}

                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Citations ({msg.citations.length})</h4>
                      <div className="grid grid-cols-1 gap-2">
                        {msg.citations.map((cit, idx) => (
                          <CitationCard key={idx} citation={cit} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Retrieved Source Snippets (Expandable) */}
                  {msg.retrieved_chunks && msg.retrieved_chunks.length > 0 && (
                    <div className="border border-slate-100 rounded-lg overflow-hidden">
                      <button
                        onClick={() => toggleChunks(msg.id)}
                        className="w-full flex items-center justify-between px-3 py-2 bg-slate-50 hover:bg-slate-100 transition-colors text-xs font-semibold text-slate-600"
                      >
                        <span className="flex items-center gap-1.5">
                          <FileText className="w-3.5 h-3.5 text-slate-400" />
                          Retrieved Source Chunks ({msg.retrieved_chunks.length})
                        </span>
                        {expandedChunks[msg.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </button>

                      {expandedChunks[msg.id] && (
                        <div className="p-3 bg-white border-t border-slate-100 space-y-3 max-h-60 overflow-y-auto">
                          {msg.retrieved_chunks.map((chunk, idx) => (
                            <div key={idx} className="p-2.5 rounded bg-slate-50 border border-slate-150 text-xs">
                              <div className="flex items-center justify-between text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                                <span>{chunk.filename} (Page {chunk.page_number})</span>
                                <span className="bg-slate-200/60 px-1.5 py-0.5 rounded">Score: {(chunk.score * 100).toFixed(0)}%</span>
                              </div>
                              <SourceSnippet content={chunk.content_preview || ''} />
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-9 h-9 rounded-xl bg-slate-200 border border-slate-350 flex items-center justify-center flex-shrink-0 shadow-sm">
                <User className="w-5 h-5 text-slate-600" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-4 justify-start">
            <div className="w-9 h-9 rounded-xl bg-blue-100 border border-blue-200 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-blue-600 animate-pulse" />
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-5 flex items-center gap-2.5 text-slate-500 text-sm shadow-sm font-medium">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" /> Generative pipeline analyzing corpora...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Tray */}
      <div className="p-4 border-t border-slate-200 bg-white">
        <form onSubmit={handleSend} className="relative flex items-center max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your security, legal, or policy question..."
            className="w-full pl-5 pr-14 py-3 rounded-full border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm placeholder-slate-400"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
