import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, ChevronDown, ChevronRight } from 'lucide-react';

interface Props {
  downloads: Record<string, string>; // label -> url
}

export default function DownloadLinks({ downloads }: Props) {
  const [open, setOpen] = useState(true);

  const isEmpty = !downloads || Object.keys(downloads).length === 0;
  if (isEmpty) return null;

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-4 mb-4">
      {/* Toggle Header */}
      <div
        className="flex items-center justify-between cursor-pointer text-lg font-semibold text-blue-700 dark:text-blue-400"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-2">
          <Download size={18} />
          <span>Downloads</span>
        </div>
        {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
      </div>

      {/* Collapsible Content */}
      <AnimatePresence initial={false}>
        {open && (
          <motion.ul
            className="mt-2 text-sm list-disc list-inside text-blue-700 dark:text-blue-300"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {Object.entries(downloads).map(([label, url]) => (
              <li key={label}>
                <a
                  href={url}
                  className="underline hover:text-blue-900 dark:hover:text-blue-100"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {label}
                </a>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}
