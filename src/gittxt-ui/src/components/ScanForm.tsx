import React, { useState } from 'react';
import axios from 'axios';

interface Props {
  onScanComplete: (data: any) => void;
}

export default function ScanForm({ onScanComplete }: Props) {
  const [repoUrl, setRepoUrl] = useState('');
  const [exclude, setExclude] = useState('.git,node_modules');
  const [sizeLimit, setSizeLimit] = useState(50000);
  const [formats, setFormats] = useState<string[]>(['txt', 'json']);
  const [lite, setLite] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleFormatToggle = (format: string) => {
    setFormats(prev =>
      prev.includes(format)
        ? prev.filter(f => f !== format)
        : [...prev, format]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/scan', {
        repo_url: repoUrl,
        exclude_patterns: exclude.split(',').map(p => p.trim()),
        include_patterns: [],
        size_limit: sizeLimit,
        output_format: formats,
        lite: lite
      });

      onScanComplete(res.data);
    } catch (err) {
      alert("Scan failed. See console.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow mb-4 space-y-4">
      <div>
        <label className="block font-semibold">GitHub Repo URL</label>
        <input
          type="url"
          value={repoUrl}
          onChange={e => setRepoUrl(e.target.value)}
          className="w-full border p-2 rounded mt-1"
          placeholder="https://github.com/user/repo"
          required
        />
      </div>

      <div>
        <label className="block font-semibold">Exclude Patterns</label>
        <input
          type="text"
          value={exclude}
          onChange={e => setExclude(e.target.value)}
          className="w-full border p-2 rounded mt-1"
          placeholder=".git,node_modules"
        />
      </div>

      <div>
        <label className="block font-semibold">Include files under (bytes): {sizeLimit}</label>
        <input
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
          type="checkbox"
          checked={lite}
          onChange={() => setLite(!lite)}
        />
        <label>Lite Mode</label>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        {loading ? "Scanning..." : "Ingest"}
      </button>
    </form>
  );
}
