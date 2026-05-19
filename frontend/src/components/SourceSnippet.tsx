export default function SourceSnippet({ content }: { content: string }) {
  return (
    <div className="text-xs font-mono bg-slate-100 p-2 rounded text-slate-700 overflow-x-auto whitespace-pre-wrap mt-2">
      {content}
    </div>
  );
}
