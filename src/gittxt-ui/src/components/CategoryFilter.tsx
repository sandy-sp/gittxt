export default function CategoryFilter({ categories, selected, onChange }) {
    const languages = Object.keys(categories || {});
  
    const toggle = (lang) => {
      const updated = selected.includes(lang)
        ? selected.filter((l) => l !== lang)
        : [...selected, lang];
      onChange({ languages: updated });
    };
  
    return (
      <div className="bg-white shadow-md rounded-xl p-4 mb-4">
        <h2 className="text-lg font-semibold mb-2">🗂️ File Categories</h2>
        <div className="flex flex-wrap gap-2">
          {languages.map((lang) => (
            <button
              key={lang}
              onClick={() => toggle(lang)}
              className={`px-3 py-1 text-sm rounded-full border ${
                selected.includes(lang)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {lang} ({categories[lang].length})
            </button>
          ))}
        </div>
      </div>
    );
  }
  