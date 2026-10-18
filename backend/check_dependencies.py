#!/usr/bin/env python3
"""
Script to check and validate dependencies used in the project
"""
import ast
import os
from pathlib import Path

def get_imports_from_file(file_path):
    """Extract all imports from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return set()

def main():
    """Check all Python files for imports"""
    backend_dir = Path(__file__).resolve().parent
    all_imports = set()
    
    # Check all Python files in backend
    for py_file in backend_dir.glob("*.py"):
        if py_file.name.startswith('check_'):
            continue
        
        print(f"Checking {py_file.name}...")
        imports = get_imports_from_file(py_file)
        all_imports.update(imports)
        print(f"  Imports: {sorted(imports)}")
    
    print("\n=== ALL THIRD-PARTY IMPORTS ===")
    # Filter out standard library modules
    stdlib_modules = {
        'os', 'sys', 'logging', 'typing', 'datetime', 'json', 'pathlib',
        'ast', 'collections', 'functools', 'itertools', 'operator',
        'tempfile', 'warnings', 'email', 'random', 'smtplib', 'subprocess',
        'sqlite3', 'hashlib', 'base64', 'secrets', 're', 'uuid'
    }
    local_modules = {
        'database', 'database_config', 'email_utils', 'models', 'sentiment',
        'summarization'
    }
    requirement_import_aliases = {
        'PyJWT': 'jwt',
        'python-dotenv': 'dotenv',
        'torch': 'torch',
        'accelerate': 'accelerate',
        'sentencepiece': 'sentencepiece',
    }

    third_party = sorted(all_imports - stdlib_modules - local_modules)
    print(f"Third-party modules found: {third_party}")
    
    # Check against requirements.txt
    try:
        with open(backend_dir / 'requirements.txt', 'r') as f:
            requirements = [
                line.strip().split("==")[0].split(">=")[0].split("[")[0]
                for line in f
                if line.strip() and not line.startswith("#")
            ]
        
        print(f"\nRequirements in requirements.txt: {sorted(requirements)}")
        
        # Check for unused requirements
        expected_imports = set(third_party)
        expected_imports.update(
            requirement_import_aliases[name]
            for name in requirements
            if name in requirement_import_aliases
        )
        unused = set(requirements) - {
            name for name in requirements
            if name in expected_imports or requirement_import_aliases.get(name) in expected_imports
        }
        if unused:
            print(f"\nPotentially unused requirements: {sorted(unused)}")
        else:
            print("\nAll requirements appear to be used!")
            
    except FileNotFoundError:
        print("requirements.txt not found")

if __name__ == "__main__":
    main()
