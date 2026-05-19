'use client';
import AppLayout from '@/components/AppLayout';
import ChatWindow from '@/components/ChatWindow';

export default function ChatPage() {
  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Chat Assistant</h1>
          <p className="text-slate-500 mt-1">Ask questions based on the uploaded documents. Answers include citations and confidence scores.</p>
        </div>
        
        <ChatWindow />
      </div>
    </AppLayout>
  );
}
