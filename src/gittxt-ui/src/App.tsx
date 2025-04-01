import React, { useState } from 'react';
import {
  ScanForm,
  SummaryPanel,
  TreeView,
  FileTypeTable,
  DownloadPanel
} from './components';

export default function App() {
  const [scanResult, setScanResult] = useState<any>(null);

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold text-blue-700 mb-6">Gittxt Visualizer</h1>

      {/* Scan Input */}
      <ScanForm onScanComplete={setScanResult} />

      {/* Output Results */}
      {scanResult && (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-300 p-4 rounded">
            <h2 className="text-xl font-semibold text-green-700 mb-2">✅ Scan Complete</h2>
            <p><strong>Repo:</strong> {scanResult.repo_name}</p>
            <p><strong>Scan ID:</strong> {scanResult.scan_id}</p>
            <p><strong>Timestamp:</strong> {scanResult.timestamp}</p>
          </div>

          <SummaryPanel summary={scanResult.summary} />
          <TreeView tree={scanResult.directory_tree} />
          <FileTypeTable fileTypes={scanResult.file_types} />
          <DownloadPanel
            scanId={scanResult.scan_id}
            availableFormats={scanResult.summary.output_format || ['txt']}
          />
        </div>
      )}
    </div>
  );
}
