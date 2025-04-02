import { useState } from 'react';

export default function QuickFilterToggle({ checked, onToggle, onReset }) {
  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4 flex flex-col space-y-3">
      <div className="flex items-center justify-between">
        <label htmlFor="quick-filter" className="flex items-center space-x-2 cursor-pointer">
          <div className={`w-10 h-5 flex items-center bg-gray-300 rounded-full p-1 duration-300 ease-in-out ${checked ? 'bg-blue-500' : 'bg-gray-300'}`}>
            <div className={`bg-white w-4 h-4 rounded-full shadow-md transform duration-300 ease-in-out ${checked ? 'translate-x-5' : ''}`}></div>
          </div>
          <span className="text-sm">
            Show <span className="font-semibold">only selected files</span>
          </span>
        </label>
        <button
          onClick={onReset}
          className="text-xs text-red-500 hover:underline hover:text-red-700"
        >
          Reset Filters
        </button>
      </div>
      <div className="text-xs text-gray-500">
        This filters output based on selected files below. Uses default Gittxt config for tree depth, excluded folders, and classification.
      </div>
    </div>
  );
}