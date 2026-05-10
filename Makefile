# NOTE: whitespace in front of commands are Tabs!
# Install the package with development dependencies
# alternative to `pip install -r requirements`
install:
	pip install .[dev] && pip uninstall flatsearch -y && make clean

# Clean up build artifacts
clean:
	rm -rf build/ dist/ *.egg-info

# Format the code
format:
	ruff check flatsearch --fix
	ruff format flatsearch
	black flatsearch

# Run code quality checks (used by CI)
check:
	ruff check flatsearch
	ruff format --check flatsearch
	black --check flatsearch
