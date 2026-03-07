#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== deep-loop test suite ==="
echo ""

# Determine Python runner (uv if available, else python3)
if command -v uv >/dev/null 2>&1; then
    PYTHON="uv run python"
    PYTEST="uv run pytest"
    echo "Using uv runner"
else
    PYTHON="python3"
    PYTEST="python3 -m pytest"
    echo "Using system python3"
fi
echo ""

# Check dependencies
echo "[1/4] Checking dependencies..."
$PYTHON -c "import anthropic; print('  ✓ anthropic')" 2>/dev/null || echo "  ⚠ anthropic not installed (some tests will skip)"
command -v tmux >/dev/null && echo "  ✓ tmux" || echo "  ✗ tmux NOT FOUND — install it"
command -v claude >/dev/null && echo "  ✓ claude" || echo "  ⚠ claude not found"
echo ""

# Unit tests
echo "[2/4] Running unit tests (pytest)..."
$PYTEST tests/test_unit.py -v --tb=short 2>&1
echo ""

# Mock train smoke test
echo "[3/4] Smoke testing mock_train.py..."
$PYTHON tests/mock_train.py > /tmp/mock_run.log 2>&1
if grep -q "^val_bpb:" /tmp/mock_run.log; then
    VAL=$(grep "^val_bpb:" /tmp/mock_run.log | awk '{print $2}')
    echo "  ✓ mock_train.py outputs val_bpb: $VAL"
else
    echo "  ✗ mock_train.py failed — no val_bpb in output"
    cat /tmp/mock_run.log
    exit 1
fi

MOCK_CRASH=1 $PYTHON tests/mock_train.py > /tmp/mock_crash.log 2>&1 || true
if ! grep -q "^val_bpb:" /tmp/mock_crash.log; then
    echo "  ✓ crash mode works — no val_bpb in crash output"
else
    echo "  ✗ crash mode broken — val_bpb appeared in crash output"
    exit 1
fi
echo ""

# Notify smoke test
echo "[4/4] Smoke testing notify.py..."
$PYTHON notify.py --event breakthrough --val 0.9876 2>&1
echo "  ✓ notify.py ran without error"
echo ""

echo "=== All tests passed ==="
echo ""
echo "Next: python orchestrate.py --tag test --dry-run"
