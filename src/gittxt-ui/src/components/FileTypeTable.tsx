import React from 'react';

interface Props {
  fileTypes: Record<string, string[]>;
}

export default function FileTypeTable({ fileTypes }: Props) {
  if (!fileTypes || Object.keys(fileTypes).length === 0) return null;

  return (
    <div className="bg-white shadow rounded p-4">
      <h2 className="text-lg font-semibold mb-2 text-gray-800">📂 File Types</h2>
      <div className="space-y-3 text-sm">
        {Object.entries(fileTypes).map(([category, types]) => (
          <div key={category}>
            <strong className="capitalize text-blue-700">{category}</strong>
            <div className="ml-4 text-gray-700">
              {types.length ? types.join(', ') : <em>No types</em>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
