import React from 'react';

interface Props {
  tree: string;
}

export default function TreeView({ tree }: Props) {
  if (!tree) return null;

  return (
    <div className="bg-white shadow rounded p-4">
      <h2 className="text-lg font-semibold mb-2 text-gray-800">📁 Directory Structure</h2>
      <pre className="bg-gray-100 text-sm p-3 rounded overflow-x-auto whitespace-pre-wrap">
        {tree}
      </pre>
    </div>
  );
}
