import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Tooltip } from 'react-tooltip';
import {
  SummaryCard,
  TreeView,
  FileTreeExplorer,
  CategoryFilter,
  FilePreview,
  FileTypeFilter,
  QuickFilterToggle,
  DownloadLinks,
} from '../components';
import { FileManifestEntry } from '../types/fileManifest';
import { Loader2, GitBranch, Sun, Moon } from 'lucide-react';

interface ScanResponse {
  repo_name: string;
  output_dir: string;
  output_files: string[];
  total_files: number;
  total_size_bytes: number;
  estimated_tokens: number;
  file_type_breakdown: Record<string, number>;
  tokens_by_type: Record<string, number>;
  skipped_files: [string, string][];
  manifest: Record<string, FileManifestEntry>;
  tree: string;
  treeObject: any;
  categories: Record<string, Record<string, string[]>>;
  summary: {
    repo_url: string;
    branch?: string;
  };
  downloads: Record<string, string>;
}

export default function ScanResultsUI() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ScanResponse | null>(null);
  const [filter, setFilter] = useState({ filetypes: [] as string[] });
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [activeFilePath, setActiveFilePath] = useState('');
  const [showSelectedOnly, setShowSelectedOnly] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [scanError, setScanError] = useState('');

  useEffect(() => {
    const theme = localStorage.getItem('theme') || 'light';
    const isDark = theme === 'dark';
    document.documentElement.classList.toggle('dark', isDark);
    setDarkMode(isDark);
  }, []);

  const toggleDarkMode = () => {
    const isDark = !darkMode;
    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    setDarkMode(isDark);
  };

  const triggerScan = async () => {
    if (!repoUrl.startsWith('https://github.com/')) {
      setScanError('Please enter a valid GitHub URL');
      return;
    }
    setLoading(true);
    setResults(null);
    setScanError('');
    try {
      const res = await axios.post<ScanResponse>('http://localhost:8000/scan', {
        repo_url: repoUrl,
        output_format: ['txt', 'json'],
        create_zip: true,
        lite_mode: false,
        tree_depth: 2,
      });
      setResults(res.data);
    } catch (err) {
      console.error('Scan failed', err);
      setScanError('Scan failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTypeFilter = (filetypes: string[]) =>
    setFilter((prev) => ({ ...prev, filetypes }));

  const handleToggleSelect = (path: string, isSelected: boolean) => {
    const updated = new Set(selectedFiles);
    isSelected ? updated.add(path) : updated.delete(path);
    setSelectedFiles(updated);
  };

  const handleResetFilters = () => {
    setFilter({ filetypes: [] });
    setSelectedFiles(new Set());
    setShowSelectedOnly(false);
  };

  const allExtensions = results?.manifest
    ? Array.from(new Set(Object.values(results.manifest).map(f => f.file_type)))
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
              }),
            ])
          ),
        ])
      )
    : {};

  const repoDisplay = (() => {
    try {
      const url = new URL(results?.summary?.repo_url || '');
      return `${url.pathname.slice(1)}${results?.summary?.branch ? ` @ ${results.summary.branch}` : ''}`;
    } catch {
      return '';
    }
  })();

  return (
    <div className="p-4 max-w-7xl mx-auto text-gray-800 dark:text-gray-200">
      {/* Top Bar */}
      <div className="mb-4 flex justify-between items-center">
        <div className="flex-1">
          <input
            className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-600"
            type="text"
            placeholder="Enter GitHub repo URL..."
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
          />
          {scanError && <p className="mt-1 text-red-500 text-sm">{scanError}</p>}
        </div>
        <button onClick={toggleDarkMode} className="ml-4 p-2 hover:scale-110 transition">
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>

      {/* Scan Button */}
      <button
        onClick={triggerScan}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
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

      {/* Results */}
      {results ? (
        <div className="mt-6">
          {/* Repo Info */}
          <div className="flex justify-between items-center mb-3 text-sm">
            <div className="flex items-center gap-2">
              <GitBranch size={16} />
              <span>{repoDisplay}</span>
            </div>
            <div className="text-xs text-gray-400">
              {selectedFiles.size} of {Object.keys(results.manifest || {}).length} selected
            </div>
          </div>

          {/* Summary */}
          <SummaryCard summary={results} />
          <TreeView tree={results.tree} />
          <FileTypeFilter
            filetypes={allExtensions}
            selected={filter.filetypes}
            onChange={handleTypeFilter}
          />
          <QuickFilterToggle
            checked={showSelectedOnly}
            onToggle={setShowSelectedOnly}
            onReset={handleResetFilters}
          />

          {/* Main Panel */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="md:col-span-1">
              <FileTreeExplorer
                treeData={results.treeObject}
                selected={selectedFiles}
                onToggle={handleToggleSelect}
                onFileClick={setActiveFilePath}
                activePath={activeFilePath}
                filterTypes={filter.filetypes}
                showSelectedOnly={showSelectedOnly}
                manifest={results.manifest}
              />
              <CategoryFilter
                categories={filteredCategories}
                selected={[]}
                onChange={() => {}}
                onFileClick={setActiveFilePath}
                activePath={activeFilePath}
                manifest={results.manifest}
              />
            </div>
            <div className="md:col-span-2 space-y-4">
              <FilePreview filePath={activeFilePath} />
              <DownloadLinks downloads={results.downloads} />
            </div>
          </div>
        </div>
      ) : (
        !loading && (
          <div className="mt-8 text-center text-gray-400">
            No results yet. Enter a GitHub URL and start scanning.
          </div>
        )
      )}
    </div>
  );
}
