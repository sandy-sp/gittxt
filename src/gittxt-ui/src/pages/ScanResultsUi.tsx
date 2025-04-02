import { useState } from 'react';
import axios from 'axios';
import SummaryCard from './components/SummaryCard';
import TreeViewer from './components/TreeViewer';
import CategoryFilter from './components/CategoryFilter';
import DownloadLinks from './components/DownloadLinks';
import FileTreeView from './components/FileTreeView';
import FilePreview from './components/FilePreview';
import FileTypeFilter from './components/FileTypeFilter';

export default function ScanResultsUI() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [filter, setFilter] = useState({ languages: [], filetypes: [] });
  const [selectedFiles, setSelectedFiles] = useState(new Set());
  const [activeFilePath, setActiveFilePath] = useState('');

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
    setFilter((prev) => ({ ...prev, ...newFilter }));
  };

  const handleTypeFilter = (filetypes) => {
    setFilter((prev) => ({ ...prev, filetypes }));
  };

  const handleToggleSelect = (path, isSelected) => {
    const updated = new Set(selectedFiles);
    if (isSelected) updated.add(path);
    else updated.delete(path);
    setSelectedFiles(updated);
  };

  const handleFileClick = (path) => {
    setActiveFilePath(path);
  };

  const allExtensions = results?.manifest
    ? Array.from(
        new Set(
          Object.values(results.manifest)
            .map((f) => f.file_type)
            .filter(Boolean)
        )
      )
    : [];

  const filteredCategories = results?.categories
    ? Object.fromEntries(
        Object.entries(results.categories).map(([lang, cats]) => [
          lang,
          Object.fromEntries(
            Object.entries(cats).map(([cat, files]) => [
              cat,
              files.filter((f) => {
                const ext = results.manifest?.[f]?.file_type;
                return !filter.filetypes.length || filter.filetypes.includes(ext);
              })
            ])
          )
        ])
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
          <FileTypeFilter filetypes={allExtensions} selected={filter.filetypes} onChange={handleTypeFilter} />
          <FileTreeView
            treeData={results.treeObject}
            selected={selectedFiles}
            onToggle={handleToggleSelect}
            onFileClick={handleFileClick}
            activePath={activeFilePath}
          />
          <CategoryFilter
            categories={filteredCategories}
            selected={filter.languages}
            onChange={handleFilterChange}
            onFileClick={handleFileClick}
            activePath={activeFilePath}
          />
          <FilePreview filePath={activeFilePath} />
          <DownloadLinks downloads={results.downloads} />
        </>
      )}
    </div>
  );
}
