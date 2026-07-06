#!/usr/bin/env python3
"""
Remove all __init__.py files from the codebase

Following Python 3.3+ implicit namespace packages (PEP 420), we don't need
__init__.py files. This script removes them all to maintain a clean codebase
with zero circular import issues.

Usage:
    python scripts/remove_init_files.py
"""

import os
from pathlib import Path


def remove_init_files(root_dir: str = "."):
    """
    Remove all __init__.py files from the codebase
    
    Args:
        root_dir: Root directory to start searching from
    """
    root_path = Path(root_dir).resolve()
    removed_count = 0
    skipped_count = 0
    
    # Directories to process
    target_dirs = [
        root_path / "app",
        root_path / "tests",
    ]
    
    print(f"🔍 Searching for __init__.py files in: {root_path}")
    print()
    
    for target_dir in target_dirs:
        if not target_dir.exists():
            print(f"⚠️  Directory not found: {target_dir}")
            continue
            
        print(f"📁 Processing: {target_dir}")
        
        # Find all __init__.py files
        init_files = list(target_dir.rglob("__init__.py"))
        
        for init_file in init_files:
            # Skip venv directories
            if "venv" in init_file.parts or "site-packages" in init_file.parts:
                skipped_count += 1
                continue
            
            try:
                # Check if file has content (more than just comments/docstrings)
                with open(init_file, 'r') as f:
                    content = f.read().strip()
                    
                # Remove the file
                init_file.unlink()
                removed_count += 1
                
                rel_path = init_file.relative_to(root_path)
                if content:
                    print(f"  ✅ Removed (had content): {rel_path}")
                else:
                    print(f"  ✅ Removed (empty): {rel_path}")
                    
            except Exception as e:
                print(f"  ❌ Error removing {init_file}: {e}")
    
    print()
    print(f"📊 Summary:")
    print(f"  - Removed: {removed_count} files")
    print(f"  - Skipped (venv): {skipped_count} files")
    print()
    print("✨ Done! Your codebase now follows Python 3.3+ implicit namespace packages (PEP 420)")
    print("   No more __init__.py files, no more circular import issues!")


if __name__ == "__main__":
    remove_init_files()
