# 🔍 Scan Repositories

_This page provides detailed usage instructions for the `gittxt scan` command._

## Overview

The `gittxt scan` command is used to scan directories or GitHub repositories for textual files. It supports various options for filtering, formatting, and output customization. The command is designed to handle both local and remote repositories, providing detailed summaries and flexible output formats.

---

## Usage

```bash
gittxt scan [OPTIONS] [REPOS]...
```

### Arguments

- **`REPOS`**: One or more repository paths or URLs to scan. These can be local directories or remote GitHub repositories.

---

### Options

#### General Options

- **`--log-level`**: Set the verbosity of logs.  
  Choices: `debug`, `info`, `warning`, `error`  
  Default: `warning`

- **`--sync`**: Opt-in to `.gitignore` usage for excluding files and directories.

- **`--size-limit`**: Specify the maximum file size (in bytes) to include in the scan.

- **`--branch`**: Specify a Git branch to scan for remote repositories. Ignored for local paths.

- **`--tree-depth`**: Limit the depth of the directory tree to scan. Useful for large repositories.

---

#### Filtering Options

- **`--exclude-dir`, `-x`**: Exclude specific folder paths from the scan.  
  Example: `-x node_modules -x dist`

- **`--include-patterns`, `-i`**: Include files matching specific glob patterns. Only textual files are processed.  
  Example: `-i "*.md" -i "*.txt"`

- **`--exclude-patterns`, `-e`**: Exclude files matching specific glob patterns.  
  Example: `-e "*.log" -e "*.tmp"`

---

#### Output Options

- **`--output-dir`, `-o`**: Specify a custom directory for the output files.  
  Default: Configured output directory in `gittxt` settings.

- **`--output-format`, `-f`**: Specify one or more output formats (comma-separated).  
  Supported formats: `txt`, `json`, `md`  
  Example: `-f txt,json`

- **`--zip`**: Create a ZIP bundle of the output files.

- **`--lite`**: Generate minimal output instead of full content.

---

## Examples

### Scan a Local Directory

```bash
gittxt scan /path/to/local/repo
```

### Scan a Remote GitHub Repository

```bash
gittxt scan https://github.com/user/repo --branch main
```

### Exclude Specific Directories and Files

```bash
gittxt scan /path/to/repo -x node_modules -e "*.log"
```

### Generate Output in Multiple Formats

```bash
gittxt scan /path/to/repo -f txt,json,md -o /path/to/output
```

### Limit File Size and Include Specific Patterns

```bash
gittxt scan /path/to/repo --size-limit 50000 -i "*.md" -i "*.txt"
```

---

## Output

After the scan, the following information is displayed:

1. **Summary Table**: Includes metrics such as total files, total size, and estimated tokens.
2. **File Type Breakdown**: A detailed breakdown of file types, their counts, and token estimates.
3. **Skipped Files**: A summary of files that were skipped during the scan, along with reasons.

---

## Notes

- The `--branch` option is ignored for local repositories.
- If no repositories are specified, the command will exit with an error.
- Non-textual files are automatically excluded from the scan.

---

## Troubleshooting

- **Invalid Output Format**: Ensure the `--output-format` option only includes supported formats (`txt`, `json`, `md`).
- **No Textual Files Found**: Verify the include patterns and ensure the repository contains textual files.

For more information, refer to the [official documentation](https://example.com/gittxt-docs).
