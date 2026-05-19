import { FileText } from 'lucide-react';

interface Citation {
  document: string;
  page: string;
  chunk_id: string;
  supporting_text: string;
}

export default function CitationCard({ citation }: { citation: Citation }) {
  return (
    <div className="bg-slate-50 p-4 rounded-md border border-slate-200 mt-2">
      <div className="flex items-center gap-2 mb-2">
        <FileText className="w-4 h-4 text-blue-500" />
        <span className="text-sm font-semibold text-slate-800">{citation.document}</span>
        <span className="text-xs text-slate-500">Page {citation.page}</span>
      </div>
      <p className="text-sm text-slate-600 italic border-l-2 border-blue-300 pl-3 py-1">
        "{citation.supporting_text}"
      </p>
    </div>
  );
}
