import { useState } from 'react';
import axios from 'axios';
import SummaryCard from './components/SummaryCard';
import TreeViewer from './components/TreeViewer';
import CategoryFilter from './components/CategoryFilter';
import DownloadLinks from './components/DownloadLinks';

export default function ScanResultsUI() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [filter, setFilter] = useState({ languages: [], types: [] });

  const triggerScan = async () => {
    setLoading(true);
    setResults(null);
    try {
      const response = await axios.post('http://localhost:8000/scan', {
        repo_url: repoUrl,
        output_format: ['txt', 'json'],
        create_zip: true,
        lite_mode: false,
        tree_depth: 2
      });
      setResults(response.data);
    } catch (error) {
      console.error('Scan failed', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
  };

  const filteredCategories = results?.categories
    ? Object.fromEntries(
        Object.entries(results.categories).filter(([lang]) =>
          filter.languages.length ? filter.languages.includes(lang) : true
        )
      )
    : {};

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <div className="mb-4">
        <input
          className="w-full p-2 border rounded"
          type="text"
          placeholder="Enter GitHub repo URL..."
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
        />
        <button
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
          onClick={triggerScan}
          disabled={loading}
        >
          {loading ? 'Scanning...' : 'Scan Repo'}
        </button>
      </div>

      {results && (
        <>
          <SummaryCard summary={results.summary} />
          <TreeViewer tree={results.tree} />
          <CategoryFilter
            categories={results.categories}
            selected={filter.languages}
            onChange={handleFilterChange}
          />
          <DownloadLinks downloads={results.downloads} />
        </>
      )}
    </div>
  );
}
