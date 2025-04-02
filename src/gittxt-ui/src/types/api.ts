// types/api.ts

export interface FileManifestEntry {
    path: string;
    file_type: string;
    language: string;
    size_bytes: number;
    size_readable: string;
    token_count: number;
    tokens_readable: string;
  }
  
  export type SkippedFile = [file_path: string, reason: string];
  
  export interface ScanResponse {
    repo_name: string;
    output_dir: string;
    output_files: string[];
    total_files: number;
    total_size_bytes: number;
    estimated_tokens: number;
    file_type_breakdown: Record<string, number>;
    tokens_by_type: Record<string, number>;
    skipped_files: SkippedFile[];
    manifest: Record<string, FileManifestEntry>;
    tree: string;
    treeObject: TreeNode;
    categories: Record<string, Record<string, string[]>>;
    summary: {
      repo_url: string;
      branch?: string;
    };
    downloads: Record<string, string>;
  }
  
  export interface ScanRequest {
    repo_url: string;
    output_format: string[];
    create_zip: boolean;
    lite_mode: boolean;
    branch?: string;
    subdir?: string;
    include_patterns?: string[];
    exclude_patterns?: string[];
    size_limit?: number;
    tree_depth?: number;
    log_level?: string;
    sync_ignore?: boolean;
    exclude_dirs?: string[];
    output_dir?: string;
  }
  
  // TreeNode for TreeViewer
  export interface TreeNode {
    name: string;
    children?: TreeNode[];
  }
  