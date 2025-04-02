import { useState } from 'react';

function TreeNode({ node, path, onToggle, selected, onFileClick, activePath, filterTypes }) {
  const [expanded, setExpanded] = useState(true);
  const fullPath = path ? `${path}/${node.name}` : node.name;
  const isSelected = selected.has(fullPath);
  const isFile = !node.children;
  const isActive = fullPath === activePath;

  const fileExt = isFile ? node.name.split('.').pop() : '';
  const shouldRender = !isFile || !filterTypes.length || filterTypes.includes(fileExt);

  if (!shouldRender) return null;

  const toggleSelect = () => onToggle(fullPath, !isSelected);
  const toggleExpand = () => setExpanded(!expanded);

  return (
    <li className="ml-4">
      <div className="flex items-center space-x-2">
        {node.children && (
          <button onClick={toggleExpand} className="text-sm">
            {expanded ? '▼' : '▶'}
          </button>
        )}
        <input
          type="checkbox"
          checked={isSelected}
          onChange={toggleSelect}
        />
        <span
          className={`text-sm font-mono ${
            isFile ? 'cursor-pointer hover:underline text-blue-700' : ''
          } ${isActive ? 'bg-yellow-100 px-1 rounded' : ''}`}
          onClick={() => isFile && onFileClick(fullPath)}
        >
          {node.name}
        </span>
      </div>
      {expanded && node.children && (
        <ul className="mt-1">
          {node.children.map((child) => (
            <TreeNode
              key={child.name}
              node={child}
              path={fullPath}
              onToggle={onToggle}
              selected={selected}
              onFileClick={onFileClick}
              activePath={activePath}
              filterTypes={filterTypes}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function FileTreeView({ treeData, selected, onToggle, onFileClick, activePath, filterTypes }) {
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
        />
      </ul>
    </div>
  );
}
