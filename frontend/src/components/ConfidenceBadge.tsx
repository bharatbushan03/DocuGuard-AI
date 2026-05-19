export default function ConfidenceBadge({ score }: { score: number }) {
  let label = 'Low';
  let styles = 'bg-red-100 text-red-800 border-red-200';

  if (score >= 0.75) {
    label = 'High';
    styles = 'bg-green-100 text-green-800 border-green-200';
  } else if (score >= 0.45) {
    label = 'Medium';
    styles = 'bg-yellow-100 text-yellow-800 border-yellow-200';
  }

  const percentage = (score * 100).toFixed(0);

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles}`}>
      {label} Confidence ({percentage}%)
    </span>
  );
}
