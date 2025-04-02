import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Folder, FolderOpen, FileText } from 'lucide-react';
import { Tooltip } from 'react-tooltip';
import { getTooltipContent } from '../utils/tooltipHelpers';
import { TreeNode, FileManifestEntry } from '../types/api';

interface Props {
  treeData: TreeNode | null;
  selected: Set<string>;
  onToggle: (path: string, selected: boolean) => void;
  onFileClick: (path: string) => void;
  activePath: string;
  filterTypes: string[];
  showSelectedOnly: boolean;
  manifest: Record<string, FileManifestEntry>;
}

function TreeNodeItem({
  node,
  path,
  selected,
  onToggle,
  onFileClick,
  activePath,
  filterTypes,
  showSelectedOnly,
  manifest,
}: Props & { node: TreeNode; path: string }) {
  const [expanded, setExpanded] = useState(true);
  const fullPath = path ? `${path}/${node.name}` : node.name;
  const isSelected = selected.has(fullPath);
  const isFile = !node.children;
  const isActive = fullPath === activePath;

  const ext = isFile ? node.name.split('.').pop() || '' : '';
  const matchesFilter = !filterTypes.length || filterTypes.includes(ext);
  if (isFile && !matchesFilter) return null;
  if (showSelectedOnly && isFile && !isSelected) return null;

  const toggleExpand = () => setExpanded((prev) => !prev);
  const toggleSelect = () => onToggle(fullPath, !isSelected);
  const tooltip = getTooltipContent(fullPath, manifest);

  return (
    <li className="ml-4">
      <div className="flex items-center gap-2" data-tooltip-id={`tooltip-${fullPath}`}>
        {node.children ? (
          <button onClick={toggleExpand}>
            {expanded ? <FolderOpen size={16} /> : <Folder size={16} />}
          </button>
        ) : (
          <FileText size={16} className="text-gray-500 dark:text-gray-400" />
        )}
        <input
          type="checkbox"
          checked={isSelected}
          onChange={toggleSelect}
        />
        <span
          className={`text-sm font-mono ${
            isFile ? 'cursor-pointer text-blue-700 hover:underline' : ''
          } ${isActive ? 'bg-yellow-100 dark:bg-yellow-900 px-1 rounded' : ''}`}
          onClick={() => isFile && onFileClick(fullPath)}
        >
          {node.name}
        </span>
      </div>
      <Tooltip
        id={`tooltip-${fullPath}`}
        place="right"
        effect="solid"
        content={tooltip}
      />
      <AnimatePresence initial={false}>
        {expanded && node.children && (
          <motion.ul
            className="ml-4 mt-1"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {node.children.map((child) => (
              <TreeNodeItem
                key={`${fullPath}/${child.name}`}
                node={child}
                path={fullPath}
                selected={selected}
                onToggle={onToggle}
                onFileClick={onFileClick}
                activePath={activePath}
                filterTypes={filterTypes}
                showSelectedOnly={showSelectedOnly}
                manifest={manifest}
              />
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </li>
  );
}

export default function FileTreeExplorer(props: Props) {
  const {
    treeData,
    selected,
    onToggle,
    onFileClick,
    activePath,
    filterTypes,
    showSelectedOnly,
    manifest,
  } = props;

  if (!treeData) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded p-4 text-red-500">
        ⚠️ No tree structure available.
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">
        📁 Repository Structure
      </h2>
      <ul className="text-sm">
        <TreeNodeItem
          node={treeData}
          path=""
          selected={selected}
          onToggle={onToggle}
          onFileClick={onFileClick}
          activePath={activePath}
          filterTypes={filterTypes}
          showSelectedOnly={showSelectedOnly}
          manifest={manifest}
        />
      </ul>
    </div>
  );
}
