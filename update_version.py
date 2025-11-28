"""
Version management script for paytechuz package.
This script handles automatic version incrementing and updates all version files.
"""
import re
import sys
from pathlib import Path

VERSION_FILES = {
    'setup.py': r"version='([^']+)'",
    'pyproject.toml': r'version = "([^"]+)"',
    'paytechuz_source/__init__.py': r"__version__ = '([^']+)'"
}

def get_current_version():
    """Read current version from setup.py"""
    setup_file = Path('setup.py')
    content = setup_file.read_text()
    match = re.search(r"version='([^']+)'", content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in setup.py")

def parse_version(version_string):
    """Parse version string into components"""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_string)
    if not match:
        raise ValueError(f"Invalid version format: {version_string}")
    return tuple(map(int, match.groups()))

def increment_version(version_string, part='patch'):
    """Increment version number"""
    major, minor, patch = parse_version(version_string)
    
    if part == 'major':
        return f"{major + 1}.0.0"
    elif part == 'minor':
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"

def update_version_in_file(filepath, pattern, new_version):
    """Update version in a specific file"""
    file_path = Path(filepath)
    if not file_path.exists():
        print(f"⚠️  Warning: {filepath} not found, skipping...")
        return False
    
    content = file_path.read_text()
    
    # Create replacement based on the pattern
    if 'setup.py' in str(filepath):
        new_content = re.sub(pattern, f"version='{new_version}'", content)
    elif 'pyproject.toml' in str(filepath):
        new_content = re.sub(pattern, f'version = "{new_version}"', content)
    elif '__init__.py' in str(filepath):
        new_content = re.sub(pattern, f"__version__ = '{new_version}'", content)
    else:
        new_content = content
    
    file_path.write_text(new_content)
    print(f"✅ Updated {filepath} to version {new_version}")
    return True

def update_all_versions(new_version):
    """Update version in all relevant files"""
    print(f"\n🔄 Updating all files to version {new_version}...\n")
    
    for filepath, pattern in VERSION_FILES.items():
        update_version_in_file(filepath, pattern, new_version)
    
    print(f"\n✅ All version files updated to {new_version}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Manual version specified
        new_version = sys.argv[1]
        print(f"📝 Setting version to: {new_version}")
    else:
        # Auto-increment patch version
        current = get_current_version()
        new_version = increment_version(current, 'patch')
        print(f"📝 Auto-incrementing version:")
        print(f"   Current: {current}")
        print(f"   New:     {new_version}")
    
    update_all_versions(new_version)
