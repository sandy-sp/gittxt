import { FileManifestEntry } from '../types/fileManifest';

export function getTooltipContent(file: string, manifest: Record<string, FileManifestEntry>): string {
  const entry = manifest?.[file];
  if (!entry) return 'No metadata available';

  return [
    `📄 ${file}`,
    `🧩 Type: ${entry.file_type || 'unknown'}`,
    `💬 Tokens: ${entry.tokens_readable || entry.token_count}`,
    `📦 Size: ${entry.size_readable || entry.size_bytes + ' bytes'}`,
    `🌐 Language: ${entry.language || 'n/a'}`
  ].join('\n');
}
