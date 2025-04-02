import { useState, useEffect } from 'react';
import axios from 'axios';

export default function FilePreview({ filePath }) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchContent = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`http://localhost:8000/preview?file_path=${encodeURIComponent(filePath)}`);
        setContent(res.data.content);
      } catch (err) {
        setContent('// Cannot preview this file');
      } finally {
        setLoading(false);
      }
    };

    if (filePath) fetchContent();
  }, [filePath]);

  if (!filePath) return null;

  return (
    <div className="bg-white shadow-md rounded-xl p-4 mt-4">
      <h2 className="text-lg font-semibold mb-2">📝 File Preview</h2>
      <div className="text-sm text-gray-600 mb-1 font-mono truncate">{filePath}</div>
      <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto whitespace-pre-wrap max-h-96">
        {loading ? '// Loading preview...' : content}
      </pre>
    </div>
  );
}
