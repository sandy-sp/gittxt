import React from 'react';

interface Props {
  summary: any;
}

export default function SummaryPanel({ summary }: Props) {
  if (!summary) return null;

  return (
    <div className="bg-white shadow rounded p-4">
      <h2 className="text-lg font-semibold mb-2 text-gray-800">📊 Summary</h2>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <strong>Files analyzed:</strong><br />
          {summary.total_files ?? 'N/A'}
        </div>
        <div>
          <strong>Estimated tokens:</strong><br />
          {summary.estimated_tokens ?? 'N/A'}
        </div>
        <div>
          <strong>File types excluded:</strong><br />
          {(summary.excluded_types || []).join(', ') || 'None'}
        </div>
        <div>
          <strong>Output formats:</strong><br />
          {summary.output_format?.join(', ') || 'N/A'}
        </div>
      </div>
    </div>
  );
}
