import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Folder, FolderOpen, FileText } from 'lucide-react';
import { Tooltip } from 'react-tooltip';
import { getTooltipContent } from '../utils/tooltipHelpers';
import { FileManifestEntry } from '../types/api';

type Categories = Record<string, Record<string, string[]>>;

interface Props {
  categories: Categories;
  selected: string[]; // selected languages (future use)
  onChange: (langs: string[]) => void;
  onFileClick: (path: string) => void;
  activePath: string;
  manifest: Record<string, FileManifestEntry>;
}

export default function CategoryFilter({
  categories,
  selected,
  onChange,
  onFileClick,
  activePath,
  manifest,
}: Props) {
  const [expandedLangs, setExpandedLangs] = useState<Record<string, boolean>>({});
  const [expandedCats, setExpandedCats] = useState<Record<string, boolean>>({});

  const toggleLang = (lang: string) => {
    setExpandedLangs((prev) => ({ ...prev, [lang]: !prev[lang] }));
  };

  const toggleCat = (lang: string, cat: string) => {
    const key = `${lang}::${cat}`;
    setExpandedCats((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  if (!categories || Object.keys(categories).length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded p-4 text-sm text-gray-500 dark:text-gray-300">
        No categorized files available.
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">📚 Files by Category</h2>
      <ul className="text-sm">
        {Object.entries(categories).map(([lang, catGroup]) => (
          <li key={lang} className="ml-2">
            <div
              className="flex items-center space-x-2 cursor-pointer"
              onClick={() => toggleLang(lang)}
            >
              {expandedLangs[lang] ? <FolderOpen size={16} /> : <Folder size={16} />}
              <span className="font-bold text-blue-600 dark:text-blue-400">{lang}</span>
            </div>

            <AnimatePresence initial={false}>
              {expandedLangs[lang] && (
                <motion.ul
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="ml-6 mt-1"
                >
                  {Object.entries(catGroup).map(([cat, files]) => {
                    const catKey = `${lang}::${cat}`;
                    return (
                      <li key={cat} className="ml-2">
                        <div
                          className="flex items-center space-x-2 cursor-pointer"
                          onClick={() => toggleCat(lang, cat)}
                        >
                          {expandedCats[catKey] ? <FolderOpen size={14} /> : <Folder size={14} />}
                          <span className="font-medium">{cat}</span>
                        </div>

                        <AnimatePresence initial={false}>
                          {expandedCats[catKey] && (
                            <motion.ul
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              exit={{ opacity: 0, height: 0 }}
                              transition={{ duration: 0.2 }}
                              className="ml-6"
                            >
                              {files.map((file) => (
                                <li
                                  key={file}
                                  className={`flex items-center gap-2 text-xs font-mono cursor-pointer hover:underline ${
                                    activePath === file ? 'bg-yellow-100 dark:bg-yellow-900 px-1 rounded' : ''
                                  }`}
                                  onClick={() => onFileClick(file)}
                                  data-tooltip-id={`tooltip-${file}`}
                                >
                                  <FileText size={12} />
                                  <span>{file}</span>
                                  <Tooltip
                                    id={`tooltip-${file}`}
                                    content={getTooltipContent(file, manifest)}
                                    place="right"
                                    effect="solid"
                                  />
                                </li>
                              ))}
                            </motion.ul>
                          )}
                        </AnimatePresence>
                      </li>
                    );
                  })}
                </motion.ul>
              )}
            </AnimatePresence>
          </li>
        ))}
      </ul>
    </div>
  );
}
