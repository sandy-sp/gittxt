import { useState, useEffect } from 'react';
import axios from 'axios';
import SummaryCard from './components/SummaryCard';
import TreeViewer from './components/TreeViewer';
import CategoryFilter from './components/CategoryFilter';
import DownloadLinks from './components/DownloadLinks';
import FileTreeView from './components/FileTreeView';
import FilePreview from './components/FilePreview';
import FileTypeFilter from './components/FileTypeFilter';
import QuickFilterToggle from './components/QuickFilterToggle';
import { Loader2, GitBranch, Sun, Moon } from 'lucide-react';

export default function ScanResultsUI() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [filter, setFilter] = useState({ languages: [], filetypes: [] });
  const [selectedFiles, setSelectedFiles] = useState(new Set());
  const [activeFilePath, setActiveFilePath] = useState('');
  const [showSelectedOnly, setShowSelectedOnly] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      setDarkMode(true);
    }
  }, []);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('theme', newMode ? 'dark' : 'light');
    document.documentElement.classList.toggle('dark', newMode);
  };

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

  const handleResetFilters = () => {
    setFilter({ languages: [], filetypes: [] });
    setSelectedFiles(new Set());
    setShowSelectedOnly(false);
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
                if (showSelectedOnly && !selectedFiles.has(f)) return false;
                return !filter.filetypes.length || filter.filetypes.includes(ext);
              })
            ])
          )
        ])
      )
    : {};

  const repoInfo = results?.summary?.repo_url
    ? new URL(results.summary.repo_url)
    : null;
  const repoDisplay = repoInfo ? `${repoInfo.pathname.slice(1)}${results.summary.branch ? ` @ ${results.summary.branch}` : ''}` : '';

  const totalTextual = results?.manifest
    ? Object.keys(results.manifest).length
    : 0;
  const selectedCount = selectedFiles.size;

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <div className="mb-4 flex justify-between items-center">
        <input
          className="w-full p-2 border rounded"
          type="text"
          placeholder="Enter GitHub repo URL..."
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
        />
        <button
          onClick={toggleDarkMode}
          className="ml-4 p-2 text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
      <button
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded flex items-center space-x-2 disabled:opacity-50"
        onClick={triggerScan}
        disabled={loading}
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin" size={16} />
            <span>Scanning...</span>
          </>
        ) : (
          <span>Scan Repo</span>
        )}
      </button>

      {results && (
        <>
          <div className="flex flex-wrap items-center justify-between text-sm text-gray-600 dark:text-gray-300 mb-3 gap-2">
            <div className="flex items-center space-x-2">
              <GitBranch size={16} />
              <span>{repoDisplay}</span>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {selectedCount} of {totalTextual} files selected
            </div>
          </div>
          <SummaryCard summary={results.summary} />
          <TreeViewer tree={results.tree} />
          <FileTypeFilter filetypes={allExtensions} selected={filter.filetypes} onChange={handleTypeFilter} />
          <QuickFilterToggle
            checked={showSelectedOnly}
            onToggle={setShowSelectedOnly}
            onReset={handleResetFilters}
          />
          <button
            className="ml-2 px-3 py-1 text-sm rounded border bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white"
            onClick={() => setSelectedFiles(new Set())}
          >
            Deselect All
          </button>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-1">
              <FileTreeView
                treeData={results.treeObject}
                selected={selectedFiles}
                onToggle={handleToggleSelect}
                onFileClick={handleFileClick}
                activePath={activeFilePath}
                filterTypes={filter.filetypes}
                showSelectedOnly={showSelectedOnly}
                showBadges={true}
              />
              <CategoryFilter
                categories={filteredCategories}
                selected={filter.languages}
                onChange={handleFilterChange}
                onFileClick={handleFileClick}
                activePath={activeFilePath}
                selectedFiles={selectedFiles}
                showBadges={true}
              />
            </div>
            <div className="md:col-span-2">
              <FilePreview filePath={activeFilePath} />
              <DownloadLinks downloads={results.downloads} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}