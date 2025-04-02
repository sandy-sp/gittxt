import React from 'react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Folder, FolderOpen, FileText } from 'lucide-react';
import { Tooltip } from 'react-tooltip';
import { getTooltipContent } from '../utils/tooltipHelpers';

function TreeNode({
  node,
  path,
  onToggle,
  selected,
  onFileClick,
  activePath,
  filterTypes,
  showSelectedOnly,
  manifest
}) {
  if (!node) {
    console.error("TreeNode received an undefined node:", { path });
    return null;
  }

  console.log("Rendering TreeNode:", { node, path });

  const [expanded, setExpanded] = useState(true);
  const fullPath = path ? `${path}/${node.name}` : node.name;
  const isSelected = selected?.has(fullPath) || false; // Defensive check
  const isFile = !node.children;
  const isActive = fullPath === activePath;

  const fileExt = isFile ? node.name.split('.').pop() : '';
  const shouldRender = !isFile || !filterTypes?.length || filterTypes.includes(fileExt); // Defensive check
  if (!shouldRender) return null;
  if (showSelectedOnly && isFile && !selected?.has(fullPath)) return null; // Defensive check

  const toggleSelect = () => onToggle?.(fullPath, !isSelected); // Defensive check
  const toggleExpand = () => setExpanded(!expanded);

  const meta = manifest?.[fullPath];
  const tooltip = meta
    ? `Size: ${meta.human_readable_size || meta.size} • Tokens: ${meta.token_count || '?'}`
    : '';

  return (
    <li className="ml-4">
      <div className="flex items-center space-x-2" data-tip={tooltip}>
        {node.children && (
          <button onClick={toggleExpand} className="text-sm">
            {expanded ? <FolderOpen size={16} /> : <Folder size={16} />}
          </button>
        )}
        {!node.children && <FileText size={16} className="text-gray-600" />}
        <input
          type="checkbox"
          checked={isSelected}
          onChange={toggleSelect}
        />
        <span
          className={`text-sm font-mono ${
            isFile ? 'cursor-pointer hover:underline text-blue-700' : ''
          } ${isActive ? 'bg-yellow-100 px-1 rounded' : ''}`}
          onClick={() => isFile && onFileClick?.(fullPath)} // Defensive check
        >
          {node.name}
        </span>
      </div>
      <span
        data-tooltip-id={`tooltip-${fullPath}`}
        data-tooltip-content={getTooltipContent(fullPath, manifest)}>
        {fullPath}
      </span>
      <Tooltip id={`tooltip-${fullPath}`} place="right" type="dark" effect="solid" />
      <AnimatePresence initial={false}>
        {expanded && node.children && (
          <motion.ul
            className="mt-1"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {node.children.map((child) => (
              <TreeNode
                key={child.name} // Add a unique key for each child
                node={child} // Pass the correct child node
                path={fullPath} // Update the path for the child
                selected={selected}
                onToggle={onToggle}
                onFileClick={onFileClick}
                activePath={activePath}
                filterTypes={filterTypes || []}
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

export default function FileTreeExplorer({
  treeData,
  selected,
  onToggle,
  onFileClick,
  activePath,
  filterTypes,
  showSelectedOnly,
  manifest
}) {
  console.log("Rendering FileTreeExplorer:", { treeData });

  if (!treeData) {
    console.error("FileTreeExplorer received undefined treeData");
    return <div>Error: No tree data available</div>;
  }

  return (
    <div className="bg-white shadow-md rounded-xl p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2">📁 Repository Structure</h2>
      <ul className="text-sm">
        <TreeNode
          node={treeData}
          path=""
          selected={selected}
          onToggle={onToggle}
          onFileClick={onFileClick}
          activePath={activePath}
          filterTypes={filterTypes || []}
          showSelectedOnly={showSelectedOnly}
          manifest={manifest}
        />
      </ul>
    </div>
  );
}
