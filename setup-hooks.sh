#!/bin/bash
# Setup script for BMAD workspace git hooks
# Run this after cloning: bash setup-hooks.sh

set -e

echo "[SETUP] Installing BMAD workspace git hooks..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$SCRIPT_DIR/.git/hooks"

# Check if we're in a git repository
if [ ! -d "$SCRIPT_DIR/.git" ]; then
    echo "[ERROR] Not in a git repository. Run 'git init' first."
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install pre-commit hook
echo "[INSTALL] Creating pre-commit hook..."
cat > "$HOOKS_DIR/pre-commit" << 'HOOK_EOF'
#!/bin/bash
# Pre-commit hook for BMAD multi-agent system
# Enforces naming conventions and quality standards from CONVENTIONS.md

set -e
echo "[HOOK] Running pre-commit checks..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "[OK] No files to check"
    exit 0
fi

echo "[CHECK] Validating staged files..."

# Check 1: No debug print statements in Python files
echo -n "[CHECK] Debug statements... "
DEBUG_FOUND=$(echo "$STAGED_FILES" | grep '\.py$' | xargs grep -n "print('DEBUG" 2>/dev/null || true)
if [ ! -z "$DEBUG_FOUND" ]; then
    echo -e "${RED}[FAIL]${NC}"
    echo "Found debug print statements:"
    echo "$DEBUG_FOUND"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}[OK]${NC}"
fi

# Check 2: Python file naming (snake_case)
echo -n "[CHECK] Python file naming... "
INVALID_PY_NAMES=$(echo "$STAGED_FILES" | grep '\.py$' | grep -v '^[a-z_][a-z0-9_]*\.py$' || true)
if [ ! -z "$INVALID_PY_NAMES" ]; then
    echo -e "${RED}[FAIL]${NC}"
    echo "Python files must use snake_case naming:"
    echo "$INVALID_PY_NAMES"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}[OK]${NC}"
fi

# Check 3: No large files (>1MB)
echo -n "[CHECK] File sizes... "
LARGE_FILES=""
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "0")
        if [ "$size" -gt 1048576 ]; then
            LARGE_FILES="$LARGE_FILES\n$file ($(($size / 1024))KB)"
        fi
    fi
done
if [ ! -z "$LARGE_FILES" ]; then
    echo -e "${RED}[FAIL]${NC}"
    echo "Files larger than 1MB detected:"
    echo -e "$LARGE_FILES"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}[OK]${NC}"
fi

# Check 4: No secrets in code (basic patterns)
echo -n "[CHECK] Secrets... "
SECRETS_FOUND=$(echo "$STAGED_FILES" | xargs grep -n "AIzaSy" 2>/dev/null || true)
if [ ! -z "$SECRETS_FOUND" ]; then
    echo -e "${YELLOW}[WARN]${NC}"
    echo "Possible API keys detected:"
    echo "$SECRETS_FOUND"
    echo "Consider using environment variables instead"
    # Don't block commit, just warn
else
    echo -e "${GREEN}[OK]${NC}"
fi

# Check 5: JSON files are valid
echo -n "[CHECK] JSON validity... "
JSON_INVALID=""
for file in $(echo "$STAGED_FILES" | grep '\.json$'); do
    if [ -f "$file" ]; then
        python -m json.tool "$file" > /dev/null 2>&1 || JSON_INVALID="$JSON_INVALID\n$file"
    fi
done
if [ ! -z "$JSON_INVALID" ]; then
    echo -e "${RED}[FAIL]${NC}"
    echo "Invalid JSON files:"
    echo -e "$JSON_INVALID"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}[OK]${NC}"
fi

# Check 6: No trailing whitespace
echo -n "[CHECK] Trailing whitespace... "
WHITESPACE_FOUND=$(echo "$STAGED_FILES" | xargs grep -n " $" 2>/dev/null || true)
if [ ! -z "$WHITESPACE_FOUND" ]; then
    echo -e "${YELLOW}[WARN]${NC}"
    echo "Trailing whitespace found (not blocking):"
    echo "$WHITESPACE_FOUND" | head -5
    # Don't block commit, just warn
else
    echo -e "${GREEN}[OK]${NC}"
fi

# Final verdict
echo ""
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}[BLOCKED] Pre-commit checks failed with $ERRORS error(s)${NC}"
    echo "Fix the issues above and try again"
    exit 1
else
    echo -e "${GREEN}[PASS] All pre-commit checks passed${NC}"
    exit 0
fi
HOOK_EOF

chmod +x "$HOOKS_DIR/pre-commit"
echo "[OK] Pre-commit hook installed"

# Install commit-msg hook
echo "[INSTALL] Creating commit-msg hook..."
cat > "$HOOKS_DIR/commit-msg" << 'HOOK_EOF'
#!/bin/bash
# Commit message hook for BMAD multi-agent system
# Enforces commit message format from CONVENTIONS.md

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Valid commit areas as per CONVENTIONS.md
valid_areas="CORE|API|EXEC|DOCS|TEST|FIX|CLEAN|STRUCT|EMERGENCY"

# Check format: [AREA] Description
if [[ ! "$commit_msg" =~ ^\[($valid_areas)\]\ .+ ]]; then
    echo -e "${RED}[BLOCKED] Invalid commit message format${NC}"
    echo ""
    echo "Required format: [AREA] Description"
    echo ""
    echo "Valid areas:"
    echo "  [CORE]      - Core system changes (coordinator, queue, locking)"
    echo "  [API]       - API client changes (Gemini, OpenRouter)"
    echo "  [EXEC]      - Executor changes (agent implementations)"
    echo "  [DOCS]      - Documentation updates"
    echo "  [TEST]      - Test additions or changes"
    echo "  [FIX]       - Bug fixes"
    echo "  [CLEAN]     - Code cleanup, refactoring"
    echo "  [STRUCT]    - Project structure changes"
    echo "  [EMERGENCY] - Hotfixes for broken builds"
    echo ""
    echo "Your message: $commit_msg"
    echo ""
    exit 1
fi

# Extract area and description
area=$(echo "$commit_msg" | sed -n 's/^\[\([A-Z]*\)\].*/\1/p')
description=$(echo "$commit_msg" | sed -n 's/^\[[A-Z]*\] \(.*\)/\1/p')

# Check description is not empty
if [ -z "$description" ]; then
    echo -e "${RED}[BLOCKED] Commit message must have a description after [AREA]${NC}"
    exit 1
fi

# Check description length (warn if >72 chars)
desc_length=${#description}
if [ $desc_length -gt 72 ]; then
    echo -e "${YELLOW}[WARN] Commit message is $desc_length characters (recommended: <72)${NC}"
    echo "Consider shortening for better readability"
    # Don't block, just warn
fi

# All checks passed
echo -e "${GREEN}[OK] Commit message format valid: [$area]${NC}"
exit 0
HOOK_EOF

chmod +x "$HOOKS_DIR/commit-msg"
echo "[OK] Commit-msg hook installed"

# Summary
echo ""
echo "[SUCCESS] Git hooks installed successfully!"
echo ""
echo "Hooks installed:"
echo "  - pre-commit: Validates code quality and naming conventions"
echo "  - commit-msg: Enforces [AREA] Description format"
echo ""
echo "Test the hooks by making a commit:"
echo "  git commit -m \"[TEST] Verify hooks are working\""
echo ""
