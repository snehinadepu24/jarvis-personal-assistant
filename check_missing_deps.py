#!/usr/bin/env python3
"""
Check for missing dependencies in requirements.txt
"""
import ast
import os
from pathlib import Path
from typing import Set

# Standard library modules (don't need to be in requirements.txt)
STDLIB = {
    '__future__', 'abc', 'argparse', 'asyncio', 'base64', 'collections', 'contextlib',
    'copy', 'ctypes', 'dataclasses', 'datetime', 'enum', 'functools', 'hashlib',
    'http', 'importlib', 'inspect', 'io', 'itertools', 'json', 'logging', 'math',
    'os', 'pathlib', 'pickle', 're', 'socket', 'sqlite3', 'statistics', 'string',
    'struct', 'sys', 'tempfile', 'time', 'typing', 'unittest', 'urllib', 'uuid',
    'warnings', 'weakref', 'webbrowser', 'xml', 'traceback',
}

# Internal project modules
INTERNAL = {'backend', 'jarvis', 'tests'}

def get_imports_from_file(filepath: Path) -> Set[str]:
    """Extract all import statements from a Python file."""
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get top-level module name
                    module = alias.name.split('.')[0]
                    imports.add(module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get top-level module name
                    module = node.module.split('.')[0]
                    imports.add(module)
    except Exception as e:
        print(f"  ⚠ Error parsing {filepath}: {e}")
    
    return imports

def get_all_imports(directory: Path) -> Set[str]:
    """Get all imports from all Python files in directory."""
    all_imports = set()
    
    for py_file in directory.rglob('*.py'):
        # Skip __pycache__ and .venv
        if '__pycache__' in str(py_file) or '.venv' in str(py_file):
            continue
        imports = get_imports_from_file(py_file)
        all_imports.update(imports)
    
    return all_imports

def get_requirements(req_file: Path) -> Set[str]:
    """Parse requirements.txt and extract package names."""
    packages = set()
    
    if not req_file.exists():
        return packages
    
    with open(req_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Extract package name (before ==, >=, etc.)
            pkg = line.split('==')[0].split('>=')[0].split('<')[0].split('[')[0].strip()
            # Normalize package name (replace - with _)
            pkg_normalized = pkg.replace('-', '_').lower()
            packages.add(pkg_normalized)
            # Also add the original name
            packages.add(pkg.lower())
    
    return packages

def main():
    project_root = Path(__file__).parent
    
    print("=" * 70)
    print("Checking for Missing Dependencies")
    print("=" * 70)
    
    # Get all imports from backend
    print("\n[1] Scanning backend code...")
    backend_imports = get_all_imports(project_root / "backend")
    
    # Get all imports from jarvis (since backend uses jarvis)
    print("[2] Scanning jarvis code...")
    jarvis_imports = get_all_imports(project_root / "jarvis" / "jarvis")
    
    all_imports = backend_imports | jarvis_imports
    
    # Filter out standard library and internal modules
    third_party = {
        imp for imp in all_imports 
        if imp not in STDLIB and imp not in INTERNAL
    }
    
    print(f"[3] Found {len(third_party)} third-party imports")
    
    # Get current requirements
    req_file = project_root / "backend" / "requirements.txt"
    requirements = get_requirements(req_file)
    
    print(f"[4] Found {len(requirements)} packages in requirements.txt")
    
    # Find missing
    missing = []
    for imp in sorted(third_party):
        # Normalize for comparison
        imp_normalized = imp.replace('-', '_').lower()
        
        # Check if package is in requirements (handle common name variations)
        found = False
        for req in requirements:
            if imp_normalized in req or req in imp_normalized:
                found = True
                break
        
        # Special mappings
        if imp in ['PIL', 'pil']:
            imp = 'Pillow'
            found = 'pillow' in requirements
        elif imp in ['yaml']:
            imp = 'PyYAML'
            found = 'pyyaml' in requirements
        elif imp in ['win32gui', 'win32con', 'win32api', 'pywintypes']:
            imp = 'pywin32'
            found = 'pywin32' in requirements
        elif imp == 'starlette':
            found = True  # comes with fastapi
        elif imp == 'motor':
            found = 'motor' in requirements
        
        if not found:
            missing.append(imp)
    
    # Report results
    print("\n" + "=" * 70)
    if missing:
        print(f"⚠ Found {len(missing)} potentially missing packages:")
        print("=" * 70)
        for pkg in sorted(missing):
            print(f"  - {pkg}")
        print("\n" + "=" * 70)
        print("Note: Some may be sub-modules of installed packages.")
    else:
        print("✓ All third-party imports are in requirements.txt!")
        print("=" * 70)
    
    # Show what's imported
    print(f"\nThird-party modules used ({len(third_party)}):")
    for imp in sorted(third_party):
        status = "✓" if imp not in missing else "✗"
        print(f"  {status} {imp}")

if __name__ == "__main__":
    main()
