# Makefile for BMAD Workspace
# Common operations across all projects in C:\knosso\Bmad

.PHONY: help status clean test run docs check init

# Default target - show help
help:
	@echo "BMAD Workspace Operations"
	@echo "========================="
	@echo ""
	@echo "Available targets:"
	@echo "  make help              - Show this help message"
	@echo "  make status            - Show workspace status"
	@echo "  make clean             - Clean all outputs and logs"
	@echo "  make test              - Run tests for a project"
	@echo "  make run               - Run a project"
	@echo "  make docs              - Generate/update documentation"
	@echo "  make check             - Run pre-commit checks manually"
	@echo "  make init              - Initialize a new project"
	@echo ""
	@echo "Usage with PROJECT variable:"
	@echo "  make test PROJECT=multi-agent-mvp"
	@echo "  make run PROJECT=multi-agent-mvp"
	@echo "  make clean PROJECT=multi-agent-mvp"
	@echo ""

# Show workspace status
status:
	@echo "[STATUS] BMAD Workspace Overview"
	@echo "================================"
	@echo ""
	@echo "Location: C:\knosso\Bmad"
	@echo ""
	@echo "Projects:"
	@cd projects && for dir in */; do echo "  - $$dir"; done
	@echo ""
	@echo "Git status:"
	@git status --short
	@echo ""
	@echo "Disk usage:"
	@du -sh projects/* 2>/dev/null || echo "  (disk usage unavailable on Windows)"
	@echo ""

# Clean outputs and logs for a specific project or all projects
clean:
ifdef PROJECT
	@echo "[CLEAN] Cleaning project: $(PROJECT)"
	@rm -rf projects/$(PROJECT)/outputs/*
	@rm -rf projects/$(PROJECT)/logs/*
	@echo "[OK] Cleaned outputs/ and logs/ for $(PROJECT)"
else
	@echo "[CLEAN] Cleaning all projects..."
	@for dir in projects/*/; do \
		echo "  Cleaning $$dir"; \
		rm -rf $$dir/outputs/* $$dir/logs/* 2>/dev/null || true; \
	done
	@rm -rf output/* .temp/* 2>/dev/null || true
	@echo "[OK] All outputs and logs cleaned"
endif

# Run tests for a specific project
test:
ifndef PROJECT
	@echo "[ERROR] Please specify PROJECT variable"
	@echo "Usage: make test PROJECT=multi-agent-mvp"
	@exit 1
endif
	@echo "[TEST] Running tests for $(PROJECT)..."
	@cd projects/$(PROJECT) && \
		if [ -f "tests/test_api.py" ]; then \
			python tests/test_api.py; \
		elif [ -d "tests/" ]; then \
			python -m pytest tests/ -v; \
		else \
			echo "[WARN] No tests found in projects/$(PROJECT)/tests/"; \
		fi

# Run a specific project
run:
ifndef PROJECT
	@echo "[ERROR] Please specify PROJECT variable"
	@echo "Usage: make run PROJECT=multi-agent-mvp"
	@exit 1
endif
	@echo "[RUN] Starting $(PROJECT)..."
	@cd projects/$(PROJECT) && \
		if [ -f "run.py" ]; then \
			python run.py; \
		elif [ -f "src/main.py" ]; then \
			python src/main.py; \
		else \
			echo "[ERROR] No run.py or src/main.py found"; \
			exit 1; \
		fi

# Generate or update documentation
docs:
ifdef PROJECT
	@echo "[DOCS] Updating documentation for $(PROJECT)..."
	@cd projects/$(PROJECT)/docs && \
		echo "Project: $(PROJECT)" > STATUS.md && \
		echo "Last Updated: $$(date)" >> STATUS.md && \
		echo "" >> STATUS.md && \
		echo "Files:" >> STATUS.md && \
		ls -lh ../src/ >> STATUS.md
	@echo "[OK] Documentation updated"
else
	@echo "[DOCS] Generating workspace documentation index..."
	@echo "# BMAD Workspace Documentation" > docs/INDEX.md
	@echo "" >> docs/INDEX.md
	@echo "Generated: $$(date)" >> docs/INDEX.md
	@echo "" >> docs/INDEX.md
	@echo "## Core Documents" >> docs/INDEX.md
	@echo "- [Conventions](CONVENTIONS.md)" >> docs/INDEX.md
	@echo "- [BMAD Compliance](BMAD_COMPLIANCE.md)" >> docs/INDEX.md
	@echo "- [Workspace Guide](WORKSPACE_GUIDE.md)" >> docs/INDEX.md
	@echo "" >> docs/INDEX.md
	@echo "## Projects" >> docs/INDEX.md
	@cd projects && for dir in */; do \
		echo "- [$$dir](../projects/$$dir/docs/README.md)" >> ../docs/INDEX.md; \
	done
	@echo "[OK] Documentation index generated at docs/INDEX.md"
endif

# Run pre-commit checks manually
check:
	@echo "[CHECK] Running pre-commit validation..."
	@if [ -f ".git/hooks/pre-commit" ]; then \
		.git/hooks/pre-commit; \
	else \
		echo "[ERROR] Pre-commit hook not found"; \
		echo "Run: git init && cp hooks/pre-commit .git/hooks/"; \
		exit 1; \
	fi

# Initialize a new project with standard structure
init:
ifndef PROJECT
	@echo "[ERROR] Please specify PROJECT variable"
	@echo "Usage: make init PROJECT=my-new-project"
	@exit 1
endif
	@echo "[INIT] Creating new project: $(PROJECT)"
	@mkdir -p projects/$(PROJECT)/{src,config,tests,docs,outputs,logs}
	@touch projects/$(PROJECT)/src/__init__.py
	@echo "# $(PROJECT)" > projects/$(PROJECT)/docs/README.md
	@echo "" >> projects/$(PROJECT)/docs/README.md
	@echo "## Overview" >> projects/$(PROJECT)/docs/README.md
	@echo "TODO: Add project description" >> projects/$(PROJECT)/docs/README.md
	@echo "" >> projects/$(PROJECT)/docs/README.md
	@echo "## Setup" >> projects/$(PROJECT)/docs/README.md
	@echo "TODO: Add setup instructions" >> projects/$(PROJECT)/docs/README.md
	@echo "# Git ignores for $(PROJECT)" > projects/$(PROJECT)/.gitignore
	@echo "outputs/" >> projects/$(PROJECT)/.gitignore
	@echo "logs/" >> projects/$(PROJECT)/.gitignore
	@echo "__pycache__/" >> projects/$(PROJECT)/.gitignore
	@echo "*.pyc" >> projects/$(PROJECT)/.gitignore
	@echo "*.pyo" >> projects/$(PROJECT)/.gitignore
	@echo ".env" >> projects/$(PROJECT)/.gitignore
	@echo "[OK] Project structure created at projects/$(PROJECT)/"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit projects/$(PROJECT)/docs/README.md"
	@echo "  2. Add source code to projects/$(PROJECT)/src/"
	@echo "  3. Create tests in projects/$(PROJECT)/tests/"
	@echo "  4. Run: git add projects/$(PROJECT)"
	@echo "  5. Commit: git commit -m '[STRUCT] Initialize $(PROJECT) project'"

# Additional utility targets

# Validate all JSON files in workspace
validate-json:
	@echo "[VALIDATE] Checking JSON files..."
	@find projects -name "*.json" -type f | while read file; do \
		echo "  Checking $$file"; \
		python -m json.tool "$$file" > /dev/null || echo "    [ERROR] Invalid JSON"; \
	done
	@echo "[OK] JSON validation complete"

# Count lines of code across all projects
loc:
	@echo "[LOC] Lines of Code by Project"
	@echo "=============================="
	@cd projects && for dir in */; do \
		count=$$(find $$dir/src -name "*.py" -type f 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $$1}' || echo "0"); \
		echo "  $$dir: $$count lines"; \
	done

# Show git commit history summary
history:
	@echo "[HISTORY] Recent Commits"
	@echo "======================="
	@git log --oneline --decorate --graph -20

# Create a backup of the workspace (excluding outputs/logs)
backup:
	@echo "[BACKUP] Creating workspace backup..."
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf "../bmad_backup_$$timestamp.tar.gz" \
		--exclude="outputs" \
		--exclude="logs" \
		--exclude=".git" \
		--exclude="__pycache__" \
		--exclude=".temp" \
		. && \
	echo "[OK] Backup created: ../bmad_backup_$$timestamp.tar.gz"
