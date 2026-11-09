"""
Packages the complete, verified B.Tech Major Project into ChurnGuide_BTech_Project.zip
Excludes .venv, cache directories, and temporary artifacts.
"""

import os
import zipfile

ZIP_NAME = "ChurnGuide_BTech_Project.zip"
ROOT_DIR = os.path.abspath(".")

EXCLUDE_DIRS = {
    ".venv", "venv", "__pycache__", ".pytest_cache", ".git", ".idea", ".vscode", "temp_extract_test"
}

EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".DS_Store"
}

EXCLUDE_FILES = {
    ZIP_NAME, "staged_upload.csv", "scored_customers.csv"
}

def package_project():
    print(f"Creating standalone distribution package: {ZIP_NAME}...")
    file_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ROOT_DIR):
            # Modify dirs in-place to avoid recursing into excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                _, ext = os.path.splitext(file)
                if ext in EXCLUDE_EXTS:
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ROOT_DIR)

                # Avoid staging artifacts
                if "uploads" in rel_path and file != ".gitkeep":
                    continue
                if "scored" in rel_path and file != ".gitkeep":
                    continue

                zipf.write(full_path, rel_path)
                file_count += 1
                total_uncompressed_bytes += os.path.getsize(full_path)

    zip_size_bytes = os.path.getsize(ZIP_NAME)
    print(f"Package successfully created!")
    print(f"Files included: {file_count}")
    print(f"Uncompressed size: {total_uncompressed_bytes / (1024*1024):.2f} MB")
    print(f"ZIP package size: {zip_size_bytes / (1024*1024):.2f} MB")
    return ZIP_NAME

if __name__ == "__main__":
    package_project()

