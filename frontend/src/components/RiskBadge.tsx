export default function RiskBadge({ level }: { level: string }) {
  const getStyles = () => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'low':
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStyles()}`}>
      {level.toUpperCase()} RISK
    </span>
  );
}
