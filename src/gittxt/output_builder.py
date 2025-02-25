import os
import json
from gittxt.logger import get_logger

logger = get_logger(__name__)

class OutputBuilder:
    def __init__(self, output_file="gittxt_output.txt", max_lines=None, output_format="txt"):
        self.output_file = output_file
        self.max_lines = max_lines
        self.output_format = output_format.lower()

    def read_file_content(self, file_path):
        """Read file content with optional line limits."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                if self.max_lines:
                    content = f.readlines()[:self.max_lines]
                else:
                    content = f.readlines()
            return content
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return [f"[Error reading {file_path}: {e}]\n"]

    def generate_output(self, files):
        """Generate output in text or JSON format."""
        if self.output_format == "json":
            return self._generate_json_output(files)
        return self._generate_text_output(files)

    def _generate_text_output(self, files):
        """Generate a single .txt file containing all extracted content."""
        logger.info(f"Writing output to {self.output_file} (TXT format)")
        with open(self.output_file, "w", encoding="utf-8") as out:
            for file_path in files:
                file_size = os.path.getsize(file_path)
                out.write(f"=== File: {file_path} (size: {file_size} bytes) ===\n")
                content = self.read_file_content(file_path)
                out.writelines(content)
                out.write("\n\n")
        logger.info(f"✅ Output saved to {self.output_file}")
        return self.output_file

    def _generate_json_output(self, files):
        """Generate output in JSON format."""
        logger.info(f"Writing output to {self.output_file} (JSON format)")
        output_data = []
        
        for file_path in files:
            file_size = os.path.getsize(file_path)
            content = self.read_file_content(file_path)
            output_data.append({
                "file": file_path,
                "size": file_size,
                "content": "".join(content)
            })
        
        with open(self.output_file, "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=4)
        
        logger.info(f"✅ Output saved to {self.output_file}")
        return self.output_file
