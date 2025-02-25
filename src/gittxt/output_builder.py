import os

class OutputBuilder:
    def __init__(self, output_file="gittxt_output.txt", max_lines=None):
        self.output_file = output_file
        self.max_lines = max_lines  # Optional limit for large files

    def read_file_content(self, file_path):
        """Read file content with optional line limits."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                if self.max_lines:
                    content = f.readlines()[:self.max_lines]  # Read only first N lines
                else:
                    content = f.readlines()
            return content
        except Exception as e:
            return [f"[Error reading {file_path}: {e}]\n"]

    def generate_output(self, files):
        """Compile all file contents into a structured output."""
        with open(self.output_file, "w", encoding="utf-8") as out:
            for file_path in files:
                file_size = os.path.getsize(file_path)
                out.write(f"=== File: {file_path} (size: {file_size} bytes) ===\n")
                content = self.read_file_content(file_path)
                out.writelines(content)
                out.write("\n\n")
        return self.output_file
