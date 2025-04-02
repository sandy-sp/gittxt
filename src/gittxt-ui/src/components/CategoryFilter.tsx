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
      <div className="space-y-4">
        {languages.map((lang) => (
          <div key={lang} className="border rounded p-2">
            <button
              onClick={() => toggle(lang)}
              className={`text-left w-full text-sm font-medium ${
                selected.includes(lang) ? 'text-blue-600' : 'text-gray-800'
              }`}
            >
              {lang} ({Object.values(categories[lang]).flat().length})
            </button>

            {selected.includes(lang) && (
              <ul className="mt-2 ml-4 list-disc text-sm text-gray-700">
                {Object.entries(categories[lang]).map(([subcat, files]) => (
                  <li key={subcat} className="mb-1">
                    <strong className="text-gray-600">{subcat}</strong>
                    <ul className="ml-4 list-[circle]">
                      {files.map((f) => (
                        <li key={f} className="truncate text-xs text-gray-600">
                          {f}
                        </li>
                      ))}
                    </ul>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
