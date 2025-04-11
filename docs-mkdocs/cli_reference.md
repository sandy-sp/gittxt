# 🖥️ CLI Reference

_A full reference of all Gittxt CLI subcommands and options._

## Subcommands

### `scan`
Scan directories or GitHub repositories to extract text in AI-ready formats.

#### Usage:
```bash
gittxt scan [OPTIONS] [REPOS]...
```

#### Options:
- `repos`: One or more repository paths or URLs to scan.
- `--exclude-dir, -x`: Exclude specific folder paths from scanning.
- `--output-dir, -o`: Specify a custom output directory for the generated files.
- `--output-format, -f`: Specify output formats (comma-separated). Supported formats: `txt`, `json`, `md`.
- `--include-patterns, -i`: Glob patterns to include specific files (textual only).
- `--exclude-patterns, -e`: Glob patterns to exclude specific files.
- `--zip`: Create a ZIP bundle of the output files.
- `--lite`: Generate minimal output instead of full content.
- `--sync`: Enable `.gitignore` usage for excluding files.
- `--size-limit`: Set a maximum file size (in bytes) for files to include.
- `--branch`: Specify a Git branch for remote repositories.
- `--tree-depth`: Limit the directory tree output to a specific depth.
- `--log-level`: Set the logging level (e.g., `INFO`, `DEBUG`).

#### Example:
```bash
gittxt scan https://github.com/example/repo -o ./output -f json,md --lite
```

---

### `config`
Manage configuration settings for Gittxt.

#### Usage:
```bash
gittxt config [OPTIONS]
```

#### Options:
- `--set`: Set a configuration key-value pair.
- `--get`: Retrieve the value of a specific configuration key.
- `--reset`: Reset all configuration settings to their defaults.

#### Example:
```bash
gittxt config --set output_dir ./custom_output
```

---

### `clean`
Clean up temporary files or cached data used by Gittxt.

#### Usage:
```bash
gittxt clean [OPTIONS]
```

#### Options:
- `--all`: Remove all temporary files and cached data.
- `--temp`: Remove only temporary files.
- `--cache`: Remove only cached data.

#### Example:
```bash
gittxt clean --all
```

---

### `reverse_command`
Reverse operations performed by Gittxt, if applicable.

#### Usage:
```bash
gittxt reverse_command [OPTIONS]
```

#### Options:
- `--input-dir`: Specify the directory containing the files to reverse.
- `--output-dir`: Specify the directory to save the reversed files.
- `--log-level`: Set the logging level (e.g., `INFO`, `DEBUG`).

#### Example:
```bash
gittxt reverse_command --input-dir ./output --output-dir ./reversed
```

---

## Notes
- All commands support the `--log-level` option to control the verbosity of logs.
- For more information, refer to the [official documentation](https://github.com/sinisterpuppy/gittxt).
