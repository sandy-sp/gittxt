import { useState } from 'react';
import InputSection from './components/InputSection';
import Summary from './components/Summary';
import DirectoryTree from './components/DirectoryTree';
import CategorizedFiles from './components/CategorizedFiles';
import DownloadButtons from './components/DownloadButtons';
import { scanRepository } from './utils/api';
import { parseGitHubURL } from './utils/github';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [scanData, setScanData] = useState(null);

  const handleScan = async (repoUrl) => {
    const { repo, branch } = parseGitHubURL(repoUrl);
    if (!repo) {
      setError('Invalid GitHub URL');
      return;
    }

    setLoading(true);
    setError('');
    setScanData(null);

    try {
      const result = await scanRepository({ repo, branch });
      setScanData(result);
    } catch (err) {
      setError(err.message || 'Scan failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-6xl mx-auto">
      <InputSection onScan={handleScan} loading={loading} />
      {error && <div className="text-red-600 my-2">{error}</div>}
      {scanData && (
        <>
          <Summary data={scanData.summary} />
          <DirectoryTree tree={scanData.tree} />
          <CategorizedFiles categories={scanData.categories} />
          <DownloadButtons links={scanData.downloads} />
        </>
      )}
    </div>
  );
}

export default App;
