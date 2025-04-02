export default function TreeViewer({ tree }) {
    if (!tree) return null;
  
    return (
      <div className="bg-white shadow-md rounded-xl p-4 mb-4">
        <h2 className="text-lg font-semibold mb-2">🌲 Directory Tree</h2>
        <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto whitespace-pre-wrap">
          {tree.trim()}
        </pre>
      </div>
    );
  }
  