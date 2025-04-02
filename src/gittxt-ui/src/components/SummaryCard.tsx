export default function SummaryCard({ summary }) {
  if (!summary) return null;

  const rows = [
    ['📦 Files', summary.total_files],
    ['📁 Size', `${(summary.total_size_bytes / 1024).toFixed(1)} KB`],
    ['🔢 Tokens', summary.estimated_tokens],
  ];

  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2">📊 Summary</h2>
      <table className="w-full">
        <tbody>
          {rows.map(([label, value], i) => (
            <tr key={i} className="border-b last:border-none">
              <td className="py-1 pr-4 text-sm text-gray-600">{label}</td>
              <td className="py-1 text-sm font-medium">{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
