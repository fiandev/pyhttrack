.PHONY: help install test clean build

PYHT := pyhttrack.py
PYTHON := python
PIP := pip

help:
	@echo "PyHttrack Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install Python dependencies (including PyInstaller)"
	@echo "  test         - Run the script locally"
	@echo "  build        - Create binary executable"
	@echo "  clean        - Clean build artifacts"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install pyinstaller

test:
	$(PYTHON) $(PYHT)

build:
	@echo "Building binary..."
	@rm -rf dist build
	@$(PYTHON) -m PyInstaller --onefile --name pyhttrack \
		--add-data "wget:wget" \
		--add-data "web.json:." \
		--hidden-import colorama \
		--console \
		$(PYHT)
	@rm -rf build pyhttrack.spec
	@echo "Binary created: dist/pyhttrack"

clean:
	rm -rf web/*.log web/*.html web/**/*.html 2>/dev/null || true
	rm -f log.txt
	rm -rf dist build pyhttrack.spec 2>/dev/null || true
