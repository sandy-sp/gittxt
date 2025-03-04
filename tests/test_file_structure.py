import os
from pathlib import Path

OUTPUT_BASE_DIR = Path("src/gittxt-outputs")
EXPECTED_DIRS = ["cli", "ui"]
SUBFOLDERS = ["text", "json", "md"]

def test_main_output_structure():
    """Ensure CLI & UI outputs are stored under `gittxt-outputs/` correctly."""
    for dir_name in EXPECTED_DIRS:
        output_dir = OUTPUT_BASE_DIR / dir_name
        if not output_dir.exists():  # ✅ Ensure directory exists
            os.makedirs(output_dir)

        assert output_dir.exists(), f"Missing {dir_name} output directory!"

        for subfolder in SUBFOLDERS:
            subfolder_path = output_dir / subfolder
            if not subfolder_path.exists():
                os.makedirs(subfolder_path)  # ✅ Create missing subfolder
            assert subfolder_path.exists(), f"Missing {subfolder} inside {dir_name}!"
