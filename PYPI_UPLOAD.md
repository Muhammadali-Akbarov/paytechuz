# Uploading to PyPI

This document explains how to use the `upload_to_pypi.sh` script to build and upload the PayTechUZ package to PyPI.

## Prerequisites

Before using the script, make sure you have:

1. A PyPI account (register at [https://pypi.org/account/register/](https://pypi.org/account/register/))
2. Python 3.6 or higher installed
3. pip installed
4. Git installed (optional, for version control)

## Using the Upload Script

### Step 1: Make the script executable

```bash
chmod +x upload_to_pypi.sh
```

### Step 2: Update the version number

Before uploading, make sure to update the version number in `setup.py`. PyPI does not allow re-uploading the same version, so you need to increment the version number for each new upload.

```python
# In setup.py
setup(
    name='paytechuz',
    version='0.1.1',  # Update this version number
    # ...
)
```

### Step 3: Run the script

```bash
./upload_to_pypi.sh
```

The script will:
1. Check for required tools and install them if needed
2. Clean up previous builds
3. Run tests if they exist
4. Build the package
5. Check the built package with twine
6. Ask for confirmation before uploading
7. Upload the package to PyPI
8. Provide information about the uploaded package

### Step 4: Enter your PyPI credentials

When prompted, enter your PyPI username and password. If you have credentials stored in keyring, you can use those instead.

## Using Keyring for Credentials (Optional)

To avoid entering your PyPI credentials each time, you can store them in keyring:

```bash
pip install keyring
keyring set https://upload.pypi.org/legacy/ your-username
```

You will be prompted to enter your password, which will be securely stored in your system's keyring.

## Troubleshooting

If you encounter any issues:

1. **Authentication errors**: Make sure your PyPI username and password are correct.
2. **Version conflicts**: Ensure you've updated the version number in `setup.py`.
3. **Build errors**: Check that your package structure is correct and all required files are present.
4. **Missing dependencies**: The script will attempt to install required tools, but if it fails, install them manually:
   ```bash
   pip install twine build
   ```

## Additional Resources

- [PyPI documentation](https://pypi.org/help/)
- [Python Packaging User Guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [Twine documentation](https://twine.readthedocs.io/en/latest/)
