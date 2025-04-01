import React, { useState, useCallback } from 'react';
import axios from 'axios';

interface ScanResponse {
  success: boolean;
  data: any;
}

interface Props {
  onScanComplete: (data: ScanResponse) => void;
}

export default function ScanForm({ onScanComplete }: Props) {
  const [repoUrl, setRepoUrl] = useState('');
  const [exclude, setExclude] = useState('.git,node_modules');
  const [sizeLimit, setSizeLimit] = useState(50000);
  const [formats, setFormats] = useState<string[]>(['txt', 'json']);
  const [lite, setLite] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFormatToggle = useCallback((format: string) => {
    setFormats(prev =>
      prev.includes(format)
        ? prev.filter(f => f !== format)
        : [...prev, format]
    );
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!repoUrl.startsWith('https://github.com/')) {
      setError('Please enter a valid GitHub repository URL.');
      setLoading(false);
      return;
    }

    try {
      const res = await axios.post<ScanResponse>('http://127.0.0.1:8000/scan', {
        repo_url: repoUrl,
        exclude_patterns: exclude.split(',').map(p => p.trim()),
        include_patterns: [],
        size_limit: sizeLimit,
        output_format: formats,
        lite: lite
      });

      onScanComplete(res.data);
    } catch (err) {
      setError('Scan failed. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow mb-4 space-y-4">
      <div>
        <label htmlFor="repoUrl" className="block font-semibold">GitHub Repo URL</label>
        <input
          id="repoUrl"
          type="url"
          value={repoUrl}
          onChange={e => setRepoUrl(e.target.value)}
          className="w-full border p-2 rounded mt-1"
          placeholder="https://github.com/user/repo"
          required
        />
      </div>

      <div>
        <label htmlFor="exclude" className="block font-semibold">Exclude Patterns</label>
        <input
          id="exclude"
          type="text"
          value={exclude}
          onChange={e => setExclude(e.target.value)}
          className="w-full border p-2 rounded mt-1"
          placeholder=".git,node_modules"
        />
      </div>

      <div>
        <label htmlFor="sizeLimit" className="block font-semibold">
          Include files under (bytes): {sizeLimit}
        </label>
        <input
          id="sizeLimit"
          type="range"
          min={1024}
          max={100000}
          value={sizeLimit}
          onChange={e => setSizeLimit(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      <div>
        <label className="block font-semibold">Output Formats</label>
        <div className="flex gap-4 mt-1">
          {['txt', 'json', 'md', 'zip'].map(fmt => (
            <label key={fmt} className="flex items-center gap-1">
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
          checked={lite}
          onChange={() => setLite(!lite)}
        />
        <label htmlFor="liteMode">Lite Mode</label>
      </div>

      {error && <p className="text-red-500">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        {loading ? "Scanning..." : "Get Text"}
      </button>
    </form>
  );
}
