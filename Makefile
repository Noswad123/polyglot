# ============================================================
# Polyglot Makefile
# - Builds and installs the shared Rust CLI for local development
# ============================================================

# --------------- CONFIG -------------------------------------

# Tooling commands
UV := uv
CARGO := cargo

# Shared CLI development build/install.
INSTALL_DIR ?= $(HOME)/.local/bin
TARGET_DIR ?= $(or $(CARGO_TARGET_DIR),target)

.PHONY: build
build:
	$(CARGO) build --locked --bin polyglot --target-dir "$(TARGET_DIR)"

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
	@echo "  make install-rust              - Shared CLI alias for make install"
	@echo "  make install INSTALL_DIR=...    - Override the local binary directory"
	@echo "  make install-hooks             - Opt in to the main exercise commit guard"
	@echo "  make run ARGS='--help'         - Build and run the shared Rust CLI"
	@echo "  make sync                      - Sync Python development dependencies only"
	@echo ""

# Keep help as the default even though the shared build target appears first.
.DEFAULT_GOAL := help

# --------------- DEVELOPMENT --------------------------------

.PHONY: sync
sync:
	$(UV) sync

.PHONY: run
run: build
	"$(TARGET_DIR)/debug/polyglot" $(ARGS)

.PHONY: install install-dev install-rust
install: build
	install -d "$(INSTALL_DIR)"
	install -m 0755 "$(TARGET_DIR)/debug/polyglot" "$(INSTALL_DIR)/polyglot"

install-dev: install

install-rust: install

.PHONY: install-hooks
install-hooks:
	sh .githooks/install.sh
