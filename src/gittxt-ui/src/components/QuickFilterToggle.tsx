import { useState } from 'react';

export default function QuickFilterToggle({ checked, onToggle }) {
  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4 flex flex-col space-y-2">
      <div className="flex items-center space-x-2">
        <input
          id="quick-filter"
          type="checkbox"
          checked={checked}
          onChange={(e) => onToggle(e.target.checked)}
        />
        <label htmlFor="quick-filter" className="text-sm">
          Show <span className="font-semibold">only selected files</span> in views
        </label>
      </div>
      <div className="text-xs text-gray-500">
        This filters output based on selected files below. Uses default Gittxt config for tree depth, excluded folders, and classification.
      </div>
    </div>
  );
}
