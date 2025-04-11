#!/bin/bash
# Script to build and upload the package to PyPI

# Set -e to exit immediately if a command exits with a non-zero status
# Set -x to print each command before executing it
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if required tools are installed
print_message "Checking required tools..." "${YELLOW}"

# Check for Python
if ! command_exists python3; then
    print_message "Python 3 is not installed. Please install it and try again." "${RED}"
    exit 1
fi

# Check for pip
if ! command_exists pip3; then
    print_message "pip3 is not installed. Please install it and try again." "${RED}"
    exit 1
fi

# Check for twine
if ! command_exists twine; then
    print_message "twine is not installed. Installing it now..." "${YELLOW}"
    pip3 install twine
fi

# Check for build
if ! python3 -c "import build" &>/dev/null; then
    print_message "build package is not installed. Installing it now..." "${YELLOW}"
    pip3 install build
fi

# Clean up previous builds
print_message "Cleaning up previous builds..." "${YELLOW}"
rm -rf build/ dist/ *.egg-info/

# Run tests if they exist
if [ -d "tests" ]; then
    print_message "Running tests..." "${YELLOW}"
    python3 -m unittest discover tests
fi

# Build the package
print_message "Building the package..." "${YELLOW}"
python3 -m build

# Check the built package
print_message "Checking the built package with twine..." "${YELLOW}"
twine check dist/*

# Ask for confirmation before uploading
print_message "\nPackage is ready to be uploaded to PyPI." "${GREEN}"
print_message "Do you want to upload the package to PyPI? (y/n)" "${YELLOW}"
read -r upload_confirmation

if [ "$upload_confirmation" != "y" ] && [ "$upload_confirmation" != "Y" ]; then
    print_message "Upload cancelled." "${RED}"
    exit 0
fi

# Ask for PyPI credentials if not using keyring
print_message "\nDo you have PyPI credentials stored in keyring? (y/n)" "${YELLOW}"
read -r keyring_confirmation

if [ "$keyring_confirmation" != "y" ] && [ "$keyring_confirmation" != "Y" ]; then
    print_message "Please enter your PyPI username:" "${YELLOW}"
    read -r pypi_username
    
    print_message "Please enter your PyPI password (input will be hidden):" "${YELLOW}"
    read -rs pypi_password
    echo
    
    # Upload to PyPI with provided credentials
    print_message "Uploading to PyPI..." "${YELLOW}"
    twine upload dist/* -u "$pypi_username" -p "$pypi_password"
else
    # Upload to PyPI using keyring
    print_message "Uploading to PyPI using stored credentials..." "${YELLOW}"
    twine upload dist/*
fi

# Check if upload was successful
if [ $? -eq 0 ]; then
    print_message "\n✅ Package successfully uploaded to PyPI!" "${GREEN}"
    
    # Get the version from setup.py
    version=$(grep -o "version='[^']*'" setup.py | cut -d "'" -f 2)
    
    print_message "Package: paytechuz" "${GREEN}"
    print_message "Version: $version" "${GREEN}"
    print_message "PyPI URL: https://pypi.org/project/paytechuz/$version/" "${GREEN}"
    
    print_message "\nUsers can now install your package with:" "${GREEN}"
    print_message "pip install paytechuz" "${YELLOW}"
    print_message "pip install paytechuz[django]  # For Django integration" "${YELLOW}"
    print_message "pip install paytechuz[fastapi]  # For FastAPI integration" "${YELLOW}"
    print_message "pip install paytechuz[flask]  # For Flask integration" "${YELLOW}"
else
    print_message "\n❌ Failed to upload package to PyPI." "${RED}"
    print_message "Please check your credentials and try again." "${RED}"
fi

# Clean up
print_message "\nDo you want to clean up the build files? (y/n)" "${YELLOW}"
read -r cleanup_confirmation

if [ "$cleanup_confirmation" = "y" ] || [ "$cleanup_confirmation" = "Y" ]; then
    print_message "Cleaning up build files..." "${YELLOW}"
    rm -rf build/ dist/ *.egg-info/
    print_message "Clean up complete." "${GREEN}"
fi

print_message "\nDone!" "${GREEN}"
