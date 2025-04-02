export default function DownloadLinks({ downloads }) {
    if (!downloads) return null;
  
    return (
      <div className="bg-white shadow-md rounded-xl p-4 mb-4">
        <h2 className="text-lg font-semibold mb-2">⬇️ Downloads</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(downloads).map(([type, url]) => (
            <a
              key={type}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 underline hover:text-blue-800 text-sm"
            >
              {type.toUpperCase()}
            </a>
          ))}
        </div>
      </div>
    );
  }
  