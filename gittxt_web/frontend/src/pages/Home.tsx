import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { performScan, ScanRequest, ScanResponse } from '../api';
import './Home.css';

const HomePage: React.FC = () => {
  const [repoUrl, setRepoUrl] = useState<string>('');
  const [excludeDirs, setExcludeDirs] = useState<string>('');
  const [includePatterns, setIncludePatterns] = useState<string>('');
  const [excludePatterns, setExcludePatterns] = useState<string>('');
  const [sizeLimit, setSizeLimit] = useState<number | undefined>();
  const [branch, setBranch] = useState<string>('');
  const [docsOnly, setDocsOnly] = useState<boolean>(false);
  const [syncIgnore, setSyncIgnore] = useState<boolean>(false);
  const [createZip, setCreateZip] = useState<boolean>(false);
  const [lite, setLite] = useState<boolean>(false);
  const [noTree, setNoTree] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const request: ScanRequest = {
      repo_path: repoUrl,
      exclude_dirs: excludeDirs.split(',').map(d => d.trim()).filter(d => d.length > 0),
      include_patterns: includePatterns.split(',').map(p => p.trim()).filter(p => p.length > 0),
      exclude_patterns: excludePatterns.split(',').map(p => p.trim()).filter(p => p.length > 0),
      size_limit: sizeLimit,
      branch: branch,
      docs_only: docsOnly,
      sync_ignore: syncIgnore,
      create_zip: createZip,
      lite: lite,
      no_tree: noTree,
    };

    try {
      const response: ScanResponse = await performScan(request);
      if (response.scan_id) {
        navigate(`/scan/${response.scan_id}`);
      } else {
        throw new Error(response.message || "Scan failed with no specific message.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
      console.error('Failed to start scan:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <h1 className="title">Gittxt Web Scanner</h1>
      <p className="subtitle">Scan a GitHub repository and generate output.</p>

      <form onSubmit={handleSubmit} className="scan-form">
        <div className="form-group">
          <label htmlFor="repoUrl">Repository URL</label>
          <input
            type="text"
            id="repoUrl"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="e.g., https://github.com/user/repo"
            required
            className="repo-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="branch">Branch (optional)</label>
          <input
            type="text"
            id="branch"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            placeholder="e.g., main"
            className="branch-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="excludeDirs">Exclude Directories (comma-separated)</label>
          <input
            type="text"
            id="excludeDirs"
            value={excludeDirs}
            onChange={(e) => setExcludeDirs(e.target.value)}
            placeholder="e.g., .git, node_modules"
            className="exclude-input"
          />
        </div>

        <div className="form-group-checkboxes">
          <label className="checkbox-label">
            <input type="checkbox" checked={docsOnly} onChange={(e) => setDocsOnly(e.target.checked)} />
            Only scan documentation files (--docs)
          </label>
          <label className="checkbox-label">
            <input type="checkbox" checked={syncIgnore} onChange={(e) => setSyncIgnore(e.target.checked)} />
            Use .gittxtignore
          </label>
          <label className="checkbox-label">
            <input type="checkbox" checked={createZip} onChange={(e) => setCreateZip(e.target.checked)} />
            Create ZIP bundle
          </label>
          <label className="checkbox-label">
            <input type="checkbox" checked={lite} onChange={(e) => setLite(e.target.checked)} />
            Lite mode (minimal output)
          </label>
          <label className="checkbox-label">
            <input type="checkbox" checked={noTree} onChange={(e) => setNoTree(e.target.checked)} />
            Exclude directory tree
          </label>
        </div>

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Scanning...' : 'Start Scan'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default HomePage;