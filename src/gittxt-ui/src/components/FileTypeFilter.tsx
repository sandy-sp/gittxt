import React from 'react';
import { useState } from 'react';

export default function FileTypeFilter({ filetypes, selected, onChange }) {
  const toggleType = (ext) => {
    const updated = selected.includes(ext)
      ? selected.filter((e) => e !== ext)
      : [...selected, ext];
    onChange(updated);
  };

  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2">🧩 File Type Filter</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
        {filetypes.map((ext) => (
          <label key={ext} className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selected.includes(ext)}
              onChange={() => toggleType(ext)}
            />
            <span className="font-mono">.{ext}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
