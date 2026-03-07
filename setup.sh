#!/usr/bin/env bash
set -euo pipefail

echo "=== deep-loop H100 setup ==="
echo "Expected: Ubuntu 22.04, CUDA 12.x, NVIDIA H100"
echo ""

# 1. Install uv
echo "[1/6] Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
source "$HOME/.local/bin/env" 2>/dev/null || true

# 2. Sync Python deps (torch from CUDA index, rest from PyPI)
echo "[2/6] Installing Python dependencies..."
uv sync

# 3. Install package in editable mode (includes openplanter/)
echo "[3/6] Installing deep-loop + openplanter..."
pip install -e . --quiet

# 4. Install Claude Code
echo "[4/6] Installing Claude Code..."
if ! command -v claude &>/dev/null; then
    npm install -g @anthropic-ai/claude-code 2>/dev/null || \
    pip install claude-cli 2>/dev/null || \
    echo "WARNING: Claude Code not auto-installed. Install manually."
fi

# 5. Check API key
echo "[5/6] Checking environment..."
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "  ⚠️  ANTHROPIC_API_KEY not set"
    echo "     export ANTHROPIC_API_KEY=sk-ant-..."
else
    echo "  ✓  ANTHROPIC_API_KEY set"
fi

# 6. Download training data
echo "[6/6] Downloading training data (takes ~5-10 min on first run)..."
if [ -d "$HOME/.cache/autoresearch/data" ]; then
    echo "  ✓  Training data found, skipping download"
else
    uv run prepare.py --num-shards 20
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "To run:"
echo "  tmux new-session -s deep-loop"
echo "  python orchestrate.py --tag mar7"
echo ""
echo "To monitor:"
echo "  python orchestrate.py --status"
echo "  tmux attach -t deep-loop"
