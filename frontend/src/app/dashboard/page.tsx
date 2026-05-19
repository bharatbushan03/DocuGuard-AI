'use client';
import AppLayout from '@/components/AppLayout';
import { FileText, ShieldAlert, MessageSquare } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500 mt-1">Welcome back to DocuGuard AI Enterprise Assistant.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center mb-4">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-800">Document Hub</h3>
            <p className="text-sm text-slate-500 mt-2 mb-4">
              Upload, manage, and view the indexing status of your enterprise documents.
            </p>
            <Link href="/documents" className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1">
              Go to Documents &rarr;
            </Link>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center mb-4">
              <MessageSquare className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-800">AI Chat Assistant</h3>
            <p className="text-sm text-slate-500 mt-2 mb-4">
              Ask questions about your data with confidence scoring and citations.
            </p>
            <Link href="/chat" className="text-sm font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              Start Chatting &rarr;
            </Link>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="w-12 h-12 bg-red-50 text-red-600 rounded-lg flex items-center justify-center mb-4">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-800">Security & Risk</h3>
            <p className="text-sm text-slate-500 mt-2 mb-4">
              Review high-risk queries, confidence metrics, and system access logs.
            </p>
            <Link href="/admin" className="text-sm font-medium text-red-600 hover:text-red-700 flex items-center gap-1">
              Admin Panel &rarr;
            </Link>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
