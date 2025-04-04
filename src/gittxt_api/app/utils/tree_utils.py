import os
from app.models.response import TreeNode


def build_tree_from_path(base_path: str, max_depth: int = 3) -> TreeNode:
    def walk(path: str, depth: int) -> TreeNode:
        node = TreeNode(name=os.path.basename(path), children=[])
        if depth == 0 or not os.path.isdir(path):
            return node

        try:
            for entry in sorted(os.listdir(path)):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    node.children.append(walk(full_path, depth - 1))
                else:
                    node.children.append(TreeNode(name=entry))
        except Exception as e:
            print(f"[WARNING] Skipping path {path}: {e}")
        return node

    return walk(base_path, max_depth)
