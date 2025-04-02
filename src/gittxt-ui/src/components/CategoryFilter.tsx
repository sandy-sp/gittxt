import React from 'react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Folder, FolderOpen, FileText } from 'lucide-react';
import { Tooltip } from 'react-tooltip';
import { getTooltipContent } from '../utils/tooltipHelpers';

export default function CategoryFilter({
  categories,
  selected,
  onChange,
  onFileClick,
  activePath,
  manifest
}) {
  const [expandedLangs, setExpandedLangs] = useState({});
  const [expandedCats, setExpandedCats] = useState({});

  const toggleLang = (lang) => {
    setExpandedLangs((prev) => ({ ...prev, [lang]: !prev[lang] }));
  };

  const toggleCat = (lang, cat) => {
    const key = `${lang}::${cat}`;
    setExpandedCats((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2">📚 Files by Category</h2>
      <ul className="text-sm">
        {Object.entries(categories).map(([lang, catGroup]) => (
          <li key={lang} className="ml-2">
            <div className="flex items-center space-x-2 cursor-pointer" onClick={() => toggleLang(lang)}>
              {expandedLangs[lang] ? <FolderOpen size={16} /> : <Folder size={16} />}
              <span className="font-bold text-blue-600">{lang}</span>
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
                  {Object.entries(catGroup).map(([cat, files]) => (
                    <li key={cat} className="ml-2">
                      <div className="flex items-center space-x-2 cursor-pointer" onClick={() => toggleCat(lang, cat)}>
                        {expandedCats[`${lang}::${cat}`] ? <FolderOpen size={14} /> : <Folder size={14} />}
                        <span className="font-medium">{cat}</span>
                      </div>
                      <AnimatePresence initial={false}>
                        {expandedCats[`${lang}::${cat}`] && (
                          <motion.ul
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.2 }}
                            className="ml-6"
                          >
                            {files.map((f) => (
                              <li
                                key={f}
                                className={`flex items-center space-x-2 text-xs font-mono cursor-pointer hover:underline ${
                                  activePath === f ? 'bg-yellow-100 px-1 rounded' : ''
                                }`}
                                onClick={() => onFileClick(f)}
                                data-tip={f}
                                data-for={`tooltip-${f}`}
                              >
                                <FileText size={12} />
                                <span
                                  data-tooltip-id={`tooltip-${f}`}
                                  data-tooltip-content={getTooltipContent(f, manifest)}>
                                  {f}
                                </span>
                                <Tooltip id={`tooltip-${f}`} place="right" type="dark" effect="solid" />
                              </li>
                            ))}
                          </motion.ul>
                        )}
                      </AnimatePresence>
                    </li>
                  ))}
                </motion.ul>
              )}
            </AnimatePresence>
          </li>
        ))}
      </ul>
    </div>
  );
}
