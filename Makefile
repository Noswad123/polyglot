# ============================================================
# Polyglot Makefile
# - Manages multiple language CLIs: pylearn, rustlearn, jslearn
# - Uses uv for Python, and leaves hooks for Rust/JS
# ============================================================

# --------------- CONFIG -------------------------------------

# Default language (can override with LANG=rust or LANG=js)
LANG ?= python

# CLI names per language
CLI_python := pylearn
CLI_rust := rustlearn
CLI_js := jslearn

# Project roots per language
ROOT_python := src/python
ROOT_rust := src/rust
ROOT_js := src/javascript

# Tooling commands
UV := uv
CARGO := cargo
NODE := node
NPM := npm
PNPM := pnpm

# Resolve language-specific values
CLI := $(CLI_$(LANG))
ROOT := $(ROOT_$(LANG))

# pyproject/cargo/package paths (for future extensibility)
PYPROJECT := pyproject.toml
CARGO_TOML := $(ROOT_rust)/$(CLI_rust)/Cargo.toml
PACKAGE_JSON := $(ROOT_js)/$(CLI_js)/package.json

# --------------- META / HELP --------------------------------

.PHONY: help
help:
	@echo ""
	@echo "Polyglot Makefile"
	@echo "------------------"
	@echo "LANG variable controls which CLI you target (default: python)."
	@echo ""
	@echo "Supported LANG values (now/future):"
	@echo "  LANG=python   -> $(CLI_python)"
	@echo "  LANG=rust     -> $(CLI_rust)   (future)"
	@echo "  LANG=js       -> $(CLI_js)     (future)"
	@echo ""
	@echo "Common commands:"
	@echo "  make sync LANG=python          - Sync deps for Python CLI via uv"
	@echo "  make run LANG=python ARGS='list --type concept'"
	@echo "  make install LANG=python       - Install CLI as a global uv tool"
	@echo "  make reinstall LANG=python     - Force reinstall global tool"
	@echo "  make uninstall LANG=python     - Uninstall global tool"
	@echo ""
	@echo "Python-specific convenience:"
	@echo "  make sync-python"
	@echo "  make install-python"
	@echo "  make run-python ARGS='list --type concept'"
	@echo ""
	@echo "Rust/JS hooks (for later wiring):"
	@echo "  make sync LANG=rust            - TODO: add cargo command"
	@echo "  make sync LANG=js              - TODO: add npm/pnpm command"
	@echo ""

# --------------- DISPATCHERS --------------------------------
# High-level targets that branch on LANG.
# Only python is fully wired; others are placeholders for now.

.PHONY: sync
sync:
ifeq ($(LANG),python)
	$(UV) sync
else ifeq ($(LANG),rust)
	@echo "TODO: add Rust sync (e.g., 'cd $(ROOT_rust)/$(CLI_rust) && $(CARGO) build')"
else ifeq ($(LANG),js)
	@echo "TODO: add JS sync (e.g., 'cd $(ROOT_js)/$(CLI_js) && $(PNPM) install')"
else
	$(error Unsupported LANG='$(LANG)'; use LANG=python|rust|js)
endif

.PHONY: run
run:
ifeq ($(LANG),python)
	$(UV) run $(CLI) $(ARGS)
else ifeq ($(LANG),rust)
	@echo "TODO: add Rust run (e.g., 'cd $(ROOT_rust)/$(CLI_rust) && $(CARGO) run -- $(ARGS)')"
else ifeq ($(LANG),js)
	@echo "TODO: add JS run (e.g., 'cd $(ROOT_js)/$(CLI_js) && $(NODE) dist/index.js $(ARGS)')"
else
	$(error Unsupported LANG='$(LANG)'; use LANG=python|rust|js)
endif

.PHONY: install
install:
ifeq ($(LANG),python)
	$(UV) tool install .
else ifeq ($(LANG),rust)
	@echo "TODO: add Rust install (e.g., 'cd $(ROOT_rust)/$(CLI_rust) && $(CARGO) install --path .')"
else ifeq ($(LANG),js)
	@echo "TODO: add JS install (e.g., global npm/pnpm link)"
else
	$(error Unsupported LANG='$(LANG)'; use LANG=python|rust|js)
endif

.PHONY: reinstall
reinstall:
ifeq ($(LANG),python)
	$(UV) tool install --force .
else ifeq ($(LANG),rust)
	@echo "TODO: add Rust reinstall logic"
else ifeq ($(LANG),js)
	@echo "TODO: add JS reinstall logic"
else
	$(error Unsupported LANG='$(LANG)'; use LANG=python|rust|js)
endif

.PHONY: uninstall
uninstall:
ifeq ($(LANG),python)
	$(UV) tool uninstall $(CLI_python)
else ifeq ($(LANG),rust)
	@echo "TODO: add Rust uninstall logic"
else ifeq ($(LANG),js)
	@echo "TODO: add JS uninstall logic"
else
	$(error Unsupported LANG='$(LANG)'; use LANG=python|rust|js)
endif

# --------------- PYTHON SHORTCUTS ---------------------------

.PHONY: sync-python
sync-python:
	$(MAKE) sync LANG=python

.PHONY: run-python
run-python:
	$(MAKE) run LANG=python ARGS="$(ARGS)"

.PHONY: install-python
install-python:
	$(MAKE) install LANG=python

.PHONY: reinstall-python
reinstall-python:
	$(MAKE) reinstall LANG=python

.PHONY: uninstall-python
uninstall-python:
	$(MAKE) uninstall LANG=python

# --------------- FUTURE: RUST SHORTCUTS ---------------------
# These are stubs for when rustlearn exists.

.PHONY: sync-rust
sync-rust:
	$(MAKE) sync LANG=rust

.PHONY: run-rust
run-rust:
	$(MAKE) run LANG=rust ARGS="$(ARGS)"

.PHONY: install-rust
install-rust:
	$(MAKE) install LANG=rust

.PHONY: reinstall-rust
reinstall-rust:
	$(MAKE) reinstall LANG=rust

.PHONY: uninstall-rust
uninstall-rust:
	$(MAKE) uninstall LANG=rust

# --------------- FUTURE: JS SHORTCUTS -----------------------
# These are stubs for when jslearn exists.

.PHONY: sync-js
sync-js:
	$(MAKE) sync LANG=js

.PHONY: run-js
run-js:
	$(MAKE) run LANG=js ARGS="$(ARGS)"

.PHONY: install-js
install-js:
	$(MAKE) install LANG=js

.PHONY: reinstall-js
reinstall-js:
	$(MAKE) reinstall LANG=js

.PHONY: uninstall-js
uninstall-js:
	$(MAKE) uninstall LANG=js
