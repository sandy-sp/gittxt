import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Loader2, FileText } from 'lucide-react';

interface Props {
  filePath: string;
}

interface PreviewResponse {
  content: string;
}

export default function FilePreview({ filePath }: Props) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPreview = async () => {
      if (!filePath) return;
      setContent('');
      setError(null);
      setLoading(true);
      try {
        const res = await axios.get<PreviewResponse>(
          `http://localhost:8000/preview?file_path=${encodeURIComponent(filePath)}`
        );
        setContent(res.data.content);
      } catch (err: any) {
        console.error('Preview load error:', err);
        setError('⚠️ Error loading file preview.');
      } finally {
        setLoading(false);
      }
    };

    fetchPreview();
  }, [filePath]);

  if (!filePath) return null;

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-800 dark:text-gray-200">
        <FileText size={16} />
        <span className="truncate">Preview: <span className="text-blue-700 dark:text-blue-400">{filePath}</span></span>
      </h2>

      {loading ? (
        <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-300">
          <Loader2 className="animate-spin" size={16} />
          <span>Loading preview...</span>
        </div>
      ) : error ? (
        <div className="text-red-500 text-sm">{error}</div>
      ) : (
        <pre className="text-xs whitespace-pre-wrap font-mono bg-gray-100 dark:bg-gray-900 p-2 rounded max-h-96 overflow-y-auto">
          {content || 'No content available.'}
        </pre>
      )}
    </div>
  );
}
