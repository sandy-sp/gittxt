import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { ScanRequest, ScanResponse } from '../types/api';

interface Props {
  onScanComplete: (data: ScanResponse) => void;
}

export default function ScanForm({ onScanComplete }: Props) {
  const [repoUrl, setRepoUrl] = useState('');
  const [exclude, setExclude] = useState('.git,node_modules');
  const [sizeLimit, setSizeLimit] = useState(50000);
  const [formats, setFormats] = useState<string[]>(['txt', 'json']);
  const [liteMode, setLiteMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFormatToggle = useCallback((format: string) => {
    setFormats((prev) =>
      prev.includes(format) ? prev.filter((f) => f !== format) : [...prev, format]
    );
  }, []);

  const validateURL = (url: string): boolean => {
    return /^https:\/\/github\.com\/[\w-]+\/[\w.-]+$/.test(url.trim());
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateURL(repoUrl)) {
      setError('❌ Please enter a valid GitHub repository URL.');
      return;
    }

    setLoading(true);

    const payload: ScanRequest = {
      repo_url: repoUrl.trim(),
      output_format: formats,
      create_zip: true,
      lite_mode: liteMode,
      exclude_patterns: exclude.split(',').map((p) => p.trim()),
      include_patterns: [],
      size_limit: sizeLimit,
      tree_depth: 2,
    };

    try {
      const res = await axios.post<ScanResponse>('http://localhost:8000/scan', payload);
      onScanComplete(res.data);
    } catch (err: any) {
      console.error('Scan error:', err);
      setError('❌ Scan failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white dark:bg-gray-800 p-6 rounded shadow mb-6 space-y-4 text-sm"
    >
      <div>
        <label htmlFor="repoUrl" className="block font-semibold text-gray-700 dark:text-gray-200">
          GitHub Repo URL
        </label>
        <input
          id="repoUrl"
          type="url"
          className="w-full border rounded p-2 mt-1 dark:bg-gray-700 dark:text-white dark:border-gray-600"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/user/repo"
          required
        />
      </div>

      <div>
        <label htmlFor="exclude" className="block font-semibold text-gray-700 dark:text-gray-200">
          Exclude Patterns
        </label>
        <input
          id="exclude"
          type="text"
          className="w-full border rounded p-2 mt-1 dark:bg-gray-700 dark:text-white dark:border-gray-600"
          value={exclude}
          onChange={(e) => setExclude(e.target.value)}
          placeholder=".git,node_modules"
        />
      </div>

      <div>
        <label htmlFor="sizeLimit" className="block font-semibold text-gray-700 dark:text-gray-200">
          Max File Size (bytes): {sizeLimit}
        </label>
        <input
          id="sizeLimit"
          type="range"
          min={1024}
          max={100000}
          value={sizeLimit}
          onChange={(e) => setSizeLimit(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      <div>
        <label className="block font-semibold text-gray-700 dark:text-gray-200">
          Output Formats
        </label>
        <div className="flex gap-4 mt-1">
          {['txt', 'json', 'md', 'zip'].map((fmt) => (
            <label key={fmt} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formats.includes(fmt)}
                onChange={() => handleFormatToggle(fmt)}
              />
              {fmt.toUpperCase()}
            </label>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          id="liteMode"
          type="checkbox"
          checked={liteMode}
          onChange={() => setLiteMode(!liteMode)}
        />
        <label htmlFor="liteMode" className="text-gray-700 dark:text-gray-200">
          Lite Mode
        </label>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Scanning...' : 'Get Text'}
      </button>
    </form>
  );
}
