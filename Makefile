# ============================================================
# Polyglot Makefile
# - Builds and installs the shared Rust CLI for local development
# - Retains older Python CLI commands and Rust/JS placeholders
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

# Shared CLI development build/install (independent of legacy LANG selection).
INSTALL_DIR ?= $(HOME)/.local/bin
TARGET_DIR ?= $(or $(CARGO_TARGET_DIR),target)

.PHONY: build
build:
	$(CARGO) build --locked --bin polyglot --target-dir "$(TARGET_DIR)"

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
	@echo "Shared CLI development commands:"
	@echo "  make build                     - Build the debug polyglot binary"
	@echo "  make install                   - Install it to $(INSTALL_DIR)/polyglot"
	@echo "  make install-dev               - Alias for make install"
	@echo "  make install INSTALL_DIR=...    - Override the local binary directory"
	@echo "  make install-hooks             - Opt in to the main exercise commit guard"
	@echo ""
	@echo "Legacy CLI commands (LANG controls only these):"
	@echo ""
	@echo "Supported LANG values (now/future):"
	@echo "  LANG=python   -> $(CLI_python)"
	@echo "  LANG=rust     -> $(CLI_rust)   (future)"
	@echo "  LANG=js       -> $(CLI_js)     (future)"
	@echo ""
	@echo "Common commands:"
	@echo "  make sync LANG=python          - Sync deps for Python CLI via uv"
	@echo "  make run LANG=python ARGS='list --type concept'"
	@echo "  make install-python            - Install the older pylearn uv tool"
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

# Keep help as the default even though the shared build target appears first.
.DEFAULT_GOAL := help

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

.PHONY: install install-dev
install: build
	install -d "$(INSTALL_DIR)"
	install -m 0755 "$(TARGET_DIR)/debug/polyglot" "$(INSTALL_DIR)/polyglot"

install-dev: install

.PHONY: install-hooks
install-hooks:
	sh .githooks/install.sh

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
	$(UV) tool install .

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
	@echo "TODO: add JS install (e.g., global npm/pnpm link)"

.PHONY: reinstall-js
reinstall-js:
	$(MAKE) reinstall LANG=js

.PHONY: uninstall-js
uninstall-js:
	$(MAKE) uninstall LANG=js
