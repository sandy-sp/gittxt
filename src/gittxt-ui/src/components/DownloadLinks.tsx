import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, ChevronDown, ChevronRight } from 'lucide-react';

export default function DownloadLinks({ downloads }) {
  const [open, setOpen] = useState(true);

  if (!downloads || Object.keys(downloads).length === 0) return null;

  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4">
      <div
        className="flex items-center space-x-2 cursor-pointer text-lg font-semibold text-blue-700"
        onClick={() => setOpen(!open)}
      >
        <Download size={18} />
        <span>Downloads</span>
        {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
      </div>
      <AnimatePresence initial={false}>
        {open && (
          <motion.ul
            className="mt-2 text-sm list-disc list-inside text-blue-600"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {Object.entries(downloads).map(([label, link]) => (
              <li key={label}>
                <a
                  href={link}
                  className="underline hover:text-blue-800"
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
