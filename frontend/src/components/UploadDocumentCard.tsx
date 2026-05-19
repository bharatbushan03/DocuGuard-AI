'use client';
import { useState, useRef } from 'react';
import { UploadCloud, Loader2, AlertCircle, FileText, CheckCircle2 } from 'lucide-react';
import api from '@/lib/api';

interface UploadDocumentCardProps {
  onUploadSuccess: () => void;
}

export default function UploadDocumentCard({ onUploadSuccess }: UploadDocumentCardProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedExtensions = ['pdf', 'docx', 'txt', 'md'];

  const validateFile = (selectedFile: File): boolean => {
    const fileExtension = selectedFile.name.split('.').pop()?.toLowerCase();
    if (!fileExtension || !allowedExtensions.includes(fileExtension)) {
      setError('Unsupported file type. Please upload PDF, DOCX, TXT, or MD files only.');
      return false;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size exceeds the 10MB limit.');
      return false;
    }
    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
        setError('');
        setSuccess(false);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
        setError('');
        setSuccess(false);
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError('');
    setSuccess(false);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const total = progressEvent.total || 0;
          if (total > 0) {
            const progress = Math.round((progressEvent.loaded * 100) / total);
            setUploadProgress(progress);
          }
        },
      });

      setSuccess(true);
      setFile(null);
      setUploadProgress(null);
      onUploadSuccess();
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during file upload.');
      setUploadProgress(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Upload Document</h3>
      <form onSubmit={handleUpload} className="space-y-4">
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className={`relative flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg transition-colors ${
            dragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-500 bg-slate-50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            id="file-upload-input"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            accept=".pdf,.docx,.txt,.md"
            onChange={handleFileChange}
            disabled={loading}
          />
          <UploadCloud className="h-10 w-10 text-slate-400 mb-2" />
          <p className="text-sm font-medium text-slate-700 text-center">
            Drag and drop your file here, or <span className="text-blue-600 hover:underline">browse</span>
          </p>
          <p className="text-xs text-slate-500 mt-1">PDF, DOCX, TXT, or MD up to 10MB</p>
        </div>

        {file && (
          <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg border border-blue-100 text-blue-800 text-sm">
            <FileText className="h-5 w-5 flex-shrink-0" />
            <div className="flex-1 truncate font-medium">{file.name}</div>
            <button
              type="button"
              onClick={() => setFile(null)}
              className="text-xs text-red-600 hover:underline"
              disabled={loading}
            >
              Remove
            </button>
          </div>
        )}

        {uploadProgress !== null && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-slate-600">
              <span>Uploading...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-start gap-2 p-3 bg-red-50 rounded-lg border border-red-100 text-red-800 text-sm">
            <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="flex items-start gap-2 p-3 bg-green-50 rounded-lg border border-green-100 text-green-800 text-sm">
            <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <span>Document uploaded successfully and is now processing!</span>
          </div>
        )}

        <button
          type="submit"
          disabled={!file || loading}
          className="w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Uploading...
            </>
          ) : (
            'Start Upload'
          )}
        </button>
      </form>
    </div>
  );
}
