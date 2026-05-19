'use client';
import { File, Lock, Globe, Users } from 'lucide-react';

interface Document {
  id: string;
  filename: string;
  access_level: string;
  status: string;
  created_at: string;
}

export default function DocumentTable({ documents }: { documents: Document[] }) {
  const getAccessIcon = (level: string) => {
    switch (level) {
      case 'private': return <Lock className="w-4 h-4 text-slate-500" />;
      case 'internal': return <Users className="w-4 h-4 text-blue-500" />;
      case 'public': return <Globe className="w-4 h-4 text-green-500" />;
      default: return <File className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">File Name</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Access Level</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Uploaded</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-200">
          {documents.map((doc) => (
            <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-50 rounded text-blue-600">
                    <File className="w-5 h-5" />
                  </div>
                  <span className="text-sm font-medium text-slate-900">{doc.filename}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center gap-2 text-sm text-slate-600 capitalize">
                  {getAccessIcon(doc.access_level)}
                  {doc.access_level}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  doc.status === 'indexed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {doc.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                {new Date(doc.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
          {documents.length === 0 && (
            <tr>
              <td colSpan={4} className="px-6 py-8 text-center text-slate-500 text-sm">
                No documents found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
