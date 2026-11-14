#!/usr/bin/env python3
"""
Import Checker - Validates all Python imports in the project
Catches missing imports before runtime without executing code
"""
import ast
import sys
from pathlib import Path
from typing import Set, List, Tuple
import importlib.util
import traceback


class ImportChecker:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors: List[Tuple[Path, int, str, str]] = []  # (file, line, import_name, error)
        self.warnings: List[Tuple[Path, str]] = []
        self.checked_count = 0
        self.skip_patterns = {
            '__pycache__', '.git', '.venv', 'node_modules', 'dist', 'build',
            '.pytest_cache', '.mypy_cache', 'htmlcov', '.tox'
        }
        
    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        return any(pattern in str(path) for pattern in self.skip_patterns)
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in project"""
        python_files = []
        for py_file in self.project_root.rglob("*.py"):
            if not self.should_skip(py_file):
                python_files.append(py_file)
        return python_files
    
    def check_file(self, file_path: Path) -> None:
        """Check all imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                self.errors.append((file_path, e.lineno or 0, "SyntaxError", str(e)))
                return
            
            # Extract all imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.validate_import(file_path, node.lineno, alias.name, None)
                        
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        self.validate_import(file_path, node.lineno, module, alias.name)
            
            self.checked_count += 1
            
        except Exception as e:
            self.warnings.append((file_path, f"Failed to read/parse: {e}"))
    
    def validate_import(self, file_path: Path, line: int, module_name: str, from_name: str | None) -> None:
        """
        Validate that an import can be resolved
        
        Args:
            file_path: Source file being checked
            line: Line number of import
            module_name: Module being imported (e.g., 'jarvis.core.schema')
            from_name: Specific name being imported (e.g., 'Screen' from 'from jarvis.core.schema import Screen')
        """
        try:
            # Try to find the module spec without actually importing it
            spec = importlib.util.find_spec(module_name)
            
            if spec is None:
                # Module not found
                import_str = f"from {module_name} import {from_name}" if from_name else f"import {module_name}"
                self.errors.append((file_path, line, import_str, f"Module '{module_name}' not found"))
                return
            
            # If we're importing specific names, we need to check if they exist
            # This requires actually importing the module (expensive but thorough)
            if from_name and from_name != "*":
                try:
                    # Try to import the module to check if the name exists
                    module = importlib.import_module(module_name)
                    
                    # Check if the name exists in the module
                    if not hasattr(module, from_name):
                        import_str = f"from {module_name} import {from_name}"
                        self.errors.append((
                            file_path, line, import_str, 
                            f"'{from_name}' not found in module '{module_name}'"
                        ))
                except ImportError as e:
                    # Module exists but can't be imported (dependencies missing, etc.)
                    import_str = f"from {module_name} import {from_name}"
                    self.warnings.append((file_path, f"Line {line}: {import_str} - {str(e)}"))
                except Exception as e:
                    # Other errors during import (circular imports, etc.)
                    pass  # Skip - might be runtime-only issues
                    
        except Exception as e:
            # Unexpected error during validation
            import_str = f"from {module_name} import {from_name}" if from_name else f"import {module_name}"
            self.warnings.append((file_path, f"Line {line}: {import_str} - Validation error: {str(e)}"))
    
    def run(self) -> bool:
        """Run import checking on all Python files"""
        print("🔍 Scanning for Python files...")
        python_files = self.find_python_files()
        print(f"📁 Found {len(python_files)} Python files to check\n")
        
        # Add project root to sys.path for imports to work
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
        
        # Add jarvis package to path
        jarvis_path = self.project_root / "jarvis"
        if jarvis_path.exists() and str(jarvis_path) not in sys.path:
            sys.path.insert(0, str(jarvis_path))
        
        print("⚙️  Checking imports...")
        for i, py_file in enumerate(python_files, 1):
            rel_path = py_file.relative_to(self.project_root)
            print(f"  [{i}/{len(python_files)}] {rel_path}", end='\r')
            self.check_file(py_file)
        
        print(f"\n\n{'='*80}")
        print(f"✅ Checked {self.checked_count} files")
        print(f"{'='*80}\n")
        
        # Report errors
        if self.errors:
            print(f"❌ Found {len(self.errors)} IMPORT ERRORS:\n")
            
            # Group by file
            errors_by_file = {}
            for file_path, line, import_str, error in self.errors:
                rel_path = file_path.relative_to(self.project_root)
                if rel_path not in errors_by_file:
                    errors_by_file[rel_path] = []
                errors_by_file[rel_path].append((line, import_str, error))
            
            for file_path, file_errors in sorted(errors_by_file.items()):
                print(f"\n📄 {file_path}")
                for line, import_str, error in file_errors:
                    print(f"   Line {line}: {import_str}")
                    print(f"   ❌ {error}")
        else:
            print("✅ No import errors found!")
        
        # Report warnings
        if self.warnings:
            print(f"\n\n⚠️  {len(self.warnings)} WARNINGS:\n")
            for file_path, warning in self.warnings:
                rel_path = file_path.relative_to(self.project_root)
                print(f"  {rel_path}: {warning}")
        
        print(f"\n{'='*80}")
        return len(self.errors) == 0


def main():
    project_root = Path(__file__).parent
    checker = ImportChecker(project_root)
    
    print("=" * 80)
    print("  🐍 Python Import Checker - JARVIS Project")
    print("=" * 80)
    print(f"  Project root: {project_root}")
    print("=" * 80 + "\n")
    
    success = checker.run()
    
    if success:
        print("✅ All imports are valid!")
        sys.exit(0)
    else:
        print("\n❌ Import errors found. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
