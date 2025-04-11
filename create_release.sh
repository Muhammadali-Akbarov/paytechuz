#!/bin/bash
# Script to create a new release of the package

# Set -e to exit immediately if a command exits with a non-zero status
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_message "Git is not installed. Please install it and try again." "${RED}"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    print_message "Not in a git repository. Please run this script from the root of your git repository." "${RED}"
    exit 1
fi

# Get the current version from setup.py
current_version=$(grep -o "version='[^']*'" setup.py | cut -d "'" -f 2)
print_message "Current version: $current_version" "${YELLOW}"

# Ask for the new version
print_message "Enter the new version number (e.g., 0.1.1):" "${YELLOW}"
read -r new_version

# Validate the version format (simple check)
if ! [[ $new_version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_message "Invalid version format. Please use semantic versioning (e.g., 0.1.1)." "${RED}"
    exit 1
fi

# Update the version in setup.py
print_message "Updating version in setup.py..." "${YELLOW}"
sed -i.bak "s/version='$current_version'/version='$new_version'/" setup.py
rm setup.py.bak

# Ask for release notes
print_message "Enter release notes (press Ctrl+D when done):" "${YELLOW}"
release_notes=$(cat)

# Create a new branch for the release
branch_name="release-$new_version"
print_message "Creating branch $branch_name..." "${YELLOW}"
git checkout -b "$branch_name"

# Commit the changes
print_message "Committing changes..." "${YELLOW}"
git add setup.py
git commit -m "Bump version to $new_version"

# Create a tag for the release
print_message "Creating tag v$new_version..." "${YELLOW}"
git tag -a "v$new_version" -m "Version $new_version

$release_notes"

# Push the branch and tag
print_message "Do you want to push the branch and tag to remote? (y/n)" "${YELLOW}"
read -r push_confirmation

if [ "$push_confirmation" = "y" ] || [ "$push_confirmation" = "Y" ]; then
    print_message "Pushing branch and tag to remote..." "${YELLOW}"
    git push origin "$branch_name"
    git push origin "v$new_version"
    
    print_message "\n✅ Branch and tag pushed to remote!" "${GREEN}"
    print_message "Now you can create a pull request and merge it to main." "${GREEN}"
    print_message "After merging, create a release on GitHub using the tag v$new_version." "${GREEN}"
    print_message "The GitHub Actions workflow will automatically publish the package to PyPI." "${GREEN}"
else
    print_message "\n✅ Branch and tag created locally!" "${GREEN}"
    print_message "To push them later, run:" "${GREEN}"
    print_message "git push origin $branch_name" "${YELLOW}"
    print_message "git push origin v$new_version" "${YELLOW}"
fi

print_message "\nDone!" "${GREEN}"
