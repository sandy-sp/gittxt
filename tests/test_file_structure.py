import pytest
import os
from pathlib import Path

# Define paths
OUTPUT_BASE_DIR = Path("src/gittxt-outputs")
EXPECTED_DIRS = ["cli", "ui"]
SUBFOLDERS = ["text", "json", "md"]

def test_main_output_structure():
    """Ensure CLI & UI outputs are stored under `gittxt-outputs/` correctly."""
    for dir_name in EXPECTED_DIRS:
        output_dir = OUTPUT_BASE_DIR / dir_name
        assert output_dir.exists(), f"Missing {dir_name} output directory!"

        for subfolder in SUBFOLDERS:
            assert (output_dir / subfolder).exists(), f"Missing {subfolder} inside {dir_name}!"
