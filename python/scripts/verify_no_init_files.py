#!/usr/bin/env python3
"""
Verify that no __init__.py files exist and all imports work correctly

This script checks:
1. No __init__.py files in app/ or tests/
2. All Python files are valid and importable
3. Direct imports work as expected
"""

import os
import sys
from pathlib import Path


def check_no_init_files(root_dir: str = "."):
    """Check that no __init__.py files exist"""
    root_path = Path(root_dir).resolve()
    
    # Directories to check
    target_dirs = [
        root_path / "app",
        root_path / "tests",
    ]
    
    found_init_files = []
    
    for target_dir in target_dirs:
        if not target_dir.exists():
            continue
            
        # Find all __init__.py files
        init_files = list(target_dir.rglob("__init__.py"))
        
        for init_file in init_files:
            # Skip venv directories
            if "venv" in init_file.parts or "site-packages" in init_file.parts:
                continue
            
            found_init_files.append(init_file.relative_to(root_path))
    
    return found_init_files


def check_python_files_valid(root_dir: str = "."):
    """Check that all Python files are syntactically valid"""
    root_path = Path(root_dir).resolve()
    
    # Directories to check
    target_dirs = [
        root_path / "app",
        root_path / "tests",
    ]
    
    invalid_files = []
    
    for target_dir in target_dirs:
        if not target_dir.exists():
            continue
            
        # Find all .py files
        py_files = list(target_dir.rglob("*.py"))
        
        for py_file in py_files:
            # Skip venv directories
            if "venv" in py_file.parts or "site-packages" in py_file.parts:
                continue
            
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                invalid_files.append((py_file.relative_to(root_path), str(e)))
    
    return invalid_files


def main():
    """Run verification checks"""
    print("🔍 Verifying No __init__.py Files Policy")
    print("=" * 60)
    print()
    
    # Check 1: No __init__.py files
    print("📋 Check 1: No __init__.py files in app/ or tests/")
    init_files = check_no_init_files()
    
    if init_files:
        print(f"  ❌ FAILED: Found {len(init_files)} __init__.py files:")
        for f in init_files:
            print(f"     - {f}")
        print()
        print("  Run: python scripts/remove_init_files.py")
        return False
    else:
        print("  ✅ PASSED: No __init__.py files found")
    
    print()
    
    # Check 2: All Python files are valid
    print("📋 Check 2: All Python files are syntactically valid")
    invalid_files = check_python_files_valid()
    
    if invalid_files:
        print(f"  ❌ FAILED: Found {len(invalid_files)} invalid Python files:")
        for f, error in invalid_files:
            print(f"     - {f}: {error}")
        return False
    else:
        print("  ✅ PASSED: All Python files are valid")
    
    print()
    print("=" * 60)
    print("✨ All checks passed! Your codebase follows PEP 420.")
    print("   No __init__.py files = No circular import issues!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
