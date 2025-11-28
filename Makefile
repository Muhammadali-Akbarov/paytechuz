update:
	@rm -rf build dist *.egg-info
	@echo "🚀 Starting full update cycle..."
	@echo ""
	@echo "Step 1/7: Auto-incrementing version..."
	@python3 update_version.py
	@echo ""
	@echo "Step 2/7: Cleaning src/paytechuz module..."
	@rm -rf src/paytechuz
	@echo "✅ src/paytechuz deleted"
	@echo ""
	@echo "Step 3/7: Restoring from paytechuz_source with new changes..."
	@if [ ! -d "paytechuz_source" ]; then \
		echo "❌ Error: paytechuz_source/ not found!"; \
		exit 1; \
	fi
	@mkdir -p src/paytechuz
	@cp -r paytechuz_source/* src/paytechuz/
	@echo "✅ Codebase copied from paytechuz_source/ to src/paytechuz/"
	@echo ""
	@echo "Step 4/7: Backing up and compiling with Cython..."
	@pip install Cython setuptools wheel
	@python3 build_cython.py
	@if [ $$? -ne 0 ]; then \
		echo "❌ Compilation failed!"; \
		exit 1; \
	fi
	@echo ""
	@echo "Step 5/7: Building distribution packages..."
	@python3 setup.py sdist bdist_wheel
	@echo ""
	@echo "Step 6/7: Uploading to PyPI..."
	@twine upload dist/*
	@if [ $$? -ne 0 ]; then \
		echo "❌ Upload failed!"; \
		exit 1; \
	fi
	@echo ""
	@echo "Step 7/7: Cleaning up - removing src/paytechuz module..."
	@rm -rf src/paytechuz
	@rm -rf build dist *.egg-info
	@echo "✅ src/paytechuz deleted"
	@echo ""
	@echo "=================================================="
	@echo "✅ UPDATE COMPLETED SUCCESSFULLY!"
	@echo "=================================================="
	@echo "- Compiled with new changes from paytechuz_source/"
	@echo "- Uploaded to PyPI"
	@echo "- Cleaned up src/paytechuz/ module"
	@echo ""
	@echo "Note: paytechuz_source/ still contains your source code"
