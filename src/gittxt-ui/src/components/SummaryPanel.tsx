import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart3, ChevronDown, ChevronRight } from 'lucide-react';

export default function SummaryPanel({ summary }) {
  const [open, setOpen] = useState(true);

  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4">
      <div
        className="flex items-center space-x-2 cursor-pointer text-lg font-semibold text-blue-700"
        onClick={() => setOpen(!open)}
      >
        <BarChart3 size={18} />
        <span>Summary</span>
        {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
      </div>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            className="mt-2 text-sm"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <pre className="whitespace-pre-wrap font-mono text-xs bg-gray-50 p-2 rounded">
              {JSON.stringify(summary, null, 2)}
            </pre>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
