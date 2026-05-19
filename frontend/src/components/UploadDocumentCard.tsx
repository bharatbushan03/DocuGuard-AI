'use client';
import { useState } from 'react';
import { UploadCloud, Loader2 } from 'lucide-react';
import api from '@/lib/api';

export default function UploadDocumentCard({ onUploadSuccess }: { onUploadSuccess: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [accessLevel, setAccessLevel] = useState('private');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('access_level', accessLevel);

    try {
      await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setFile(null);
      setAccessLevel('private');
      onUploadSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Upload New Document</h3>
      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Select File</label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-slate-300 border-dashed rounded-md hover:border-blue-500 transition-colors">
            <div className="space-y-1 text-center">
              <UploadCloud className="mx-auto h-12 w-12 text-slate-400" />
              <div className="flex text-sm text-slate-600 justify-center">
                <label
                  htmlFor="file-upload"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                >
                  <span>Upload a file</span>
                  <input id="file-upload" name="file-upload" type="file" className="sr-only" onChange={(e) => setFile(e.target.files?.[0] || null)} />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-slate-500">PDF, DOCX, TXT, MD up to 10MB</p>
            </div>
          </div>
          {file && <p className="mt-2 text-sm text-green-600 font-medium">Selected: {file.name}</p>}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Access Level</label>
          <select 
            value={accessLevel}
            onChange={(e) => setAccessLevel(e.target.value)}
            className="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
          >
            <option value="private">Private</option>
            <option value="internal">Internal</option>
            <option value="public">Public</option>
          </select>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={!file || loading}
          className="w-full flex justify-center items-center gap-2 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Upload'}
        </button>
      </form>
    </div>
  );
}
