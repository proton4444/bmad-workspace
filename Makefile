.PHONY: status audit docs

status:
	@echo "=== git status ==="
	@git status --short
	@echo ""
	@echo "=== folder sizes ==="
	@du -sh . snapshots _bmad _bmad-output releases docs 2>/dev/null || true

audit:
	@echo "=== diff check ==="
	@git diff --check || true
	@echo ""
	@echo "=== secret scan ==="
	@rg -n --hidden --glob '!.git/**' --glob '!node_modules/**' \
	  'api[_-]?key|token|secret|password|bearer|authorization|cookie|session|client_secret|private_key|OPENAI|ANTHROPIC|GEMINI|GITHUB|PATREON' \
	  2>/dev/null | grep -v 'example\|placeholder\|your_\|session-setup\|session_topic\|brainstorm' \
	  || echo "No secrets found."
	@echo ""
	@echo "=== TODO/FIXME scan ==="
	@rg -n --glob '!.git/**' 'TODO|FIXME|XXX|HACK' 2>/dev/null || echo "None found."

docs:
	@echo "=== required root docs ==="
	@for f in README.md AGENTS.md .gitignore; do \
	  if [ -f $$f ]; then echo "  ✓ $$f"; else echo "  ✗ $$f MISSING"; fi; \
	done
	@echo ""
	@echo "=== docs/ index ==="
	@if [ -f docs/INDEX.md ]; then echo "  ✓ docs/INDEX.md"; else echo "  ✗ docs/INDEX.md MISSING"; fi
