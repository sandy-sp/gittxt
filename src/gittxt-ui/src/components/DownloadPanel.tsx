import React from 'react';

interface Props {
  scanId: string;
  availableFormats: string[];
}

export default function DownloadPanel({ scanId, availableFormats }: Props) {
  if (!scanId || !availableFormats.length) return null;

  const handleDownload = (format: string) => {
    const url = `http://127.0.0.1:8000/download/${scanId}?format=${format}`;
    window.open(url, '_blank');
  };

  return (
    <div className="bg-white shadow rounded p-4">
      <h2 className="text-lg font-semibold mb-2 text-gray-800">📥 Download Outputs</h2>
      <div className="flex flex-wrap gap-3">
        {availableFormats.map(format => (
          <button
            key={format}
            onClick={() => handleDownload(format)}
            className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded"
          >
            {format.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}
