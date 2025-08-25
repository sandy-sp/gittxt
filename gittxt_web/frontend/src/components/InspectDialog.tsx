import React, { useState, useEffect } from 'react';
import { getInspectionContent, FileInspectResponse } from '../api';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './InspectDialog.css';

interface InspectDialogProps {
  scanId: string;
  filePath: string;
  onClose: () => void;
}

const InspectDialog: React.FC<InspectDialogProps> = ({ scanId, filePath, onClose }) => {
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFileContent = async () => {
      try {
        setLoading(true);
        const data: FileInspectResponse = await getInspectionContent(scanId, filePath);
        setFileContent(data.content);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch file content.');
        console.error('Failed to fetch file content:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchFileContent();
  }, [scanId, filePath]);

  const getLanguage = (filename: string): string => {
    const extension = filename.split('.').pop();
    switch (extension) {
      case 'py': return 'python';
      case 'js': return 'javascript';
      case 'ts': return 'typescript';
      case 'html': return 'html';
      case 'css': return 'css';
      case 'json': return 'json';
      case 'md': return 'markdown';
      case 'sh': return 'bash';
      case 'yml':
      case 'yaml': return 'yaml';
      default: return 'text';
    }
  };

  const language = getLanguage(filePath);

  return (
    <div className="inspect-dialog-overlay">
      <div className="inspect-dialog-content">
        <div className="inspect-dialog-header">
          <h3>Inspecting: {filePath}</h3>
          <button onClick={onClose} className="close-button">&times;</button>
        </div>
        <div className="inspect-dialog-body">
          {loading && <p>Loading file content...</p>}
          {error && <p className="error-message">Error: {error}</p>}
          {fileContent !== null && (
            <SyntaxHighlighter language={language} style={oneDark}>
              {fileContent}
            </SyntaxHighlighter>
          )}
        </div>
      </div>
    </div>
  );
};

export default InspectDialog;