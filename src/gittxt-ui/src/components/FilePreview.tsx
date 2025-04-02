import { useEffect, useState } from 'react';
import axios from 'axios';
import { Loader2, FileText } from 'lucide-react';

export default function FilePreview({ filePath }) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPreview = async () => {
      if (!filePath) return;
      setLoading(true);
      try {
        const res = await axios.get(`http://localhost:8000/preview?file_path=${encodeURIComponent(filePath)}`);
        setContent(res.data.content);
      } catch (err) {
        setContent('Error loading preview.');
      } finally {
        setLoading(false);
      }
    };
    fetchPreview();
  }, [filePath]);

  if (!filePath) return null;

  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
        <FileText size={16} /> Preview: <span className="text-blue-700">{filePath}</span>
      </h2>
      {loading ? (
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Loader2 className="animate-spin" size={16} />
          <span>Loading preview...</span>
        </div>
      ) : (
        <pre className="text-xs whitespace-pre-wrap font-mono bg-gray-50 p-2 rounded max-h-96 overflow-y-auto">
          {content}
        </pre>
      )}
    </div>
  );
}
