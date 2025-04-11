# 🧠 API Reference

_This section will document internal APIs and CLI commands in future updates._

## Endpoints

### Inspect Repository

**POST** `/inspect`

This endpoint inspects a Git repository and provides details about its structure, including textual and non-textual files, a summary, and preview snippets.

#### Request Body

| Field      | Type     | Required | Description                              |
|------------|----------|----------|------------------------------------------|
| `repo_url` | `string` | Yes      | The URL of the Git repository to inspect. |
| `branch`   | `string` | No       | The branch to inspect (default: main branch). |
| `subdir`   | `string` | No       | A specific subdirectory to inspect (optional). |

#### Response

| Field              | Type       | Description                                      |
|--------------------|------------|--------------------------------------------------|
| `repo_name`        | `string`   | The name of the repository.                     |
| `branch`           | `string`   | The branch that was inspected.                  |
| `tree`             | `object`   | The directory tree structure of the repository. |
| `textual_files`    | `list`     | A list of textual files in the repository.      |
| `non_textual_files`| `list`     | A list of non-textual files in the repository.  |
| `summary`          | `string`   | A summary of the repository contents.           |
| `preview_snippets` | `object`   | Snippets of content from textual files.         |

#### Example Request

```json
{
  "repo_url": "https://github.com/example/repo.git",
  "branch": "main",
  "subdir": "src"
}
```

#### Example Response

```json
{
  "repo_name": "repo",
  "branch": "main",
  "tree": {
    "src": {
      "file1.py": "textual",
      "file2.png": "non-textual"
    }
  },
  "textual_files": ["src/file1.py"],
  "non_textual_files": ["src/file2.png"],
  "summary": "Repository contains 1 textual file and 1 non-textual file.",
  "preview_snippets": {
    "src/file1.py": "def example_function():\n    pass"
  }
}
```

#### Error Responses

- **500 Internal Server Error**: If the inspection fails, the response will include an error message.

```json
{
  "detail": "Inspect failed: <error details>"
}
