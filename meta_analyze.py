#!/usr/bin/env python3
"""
meta_analyze.py — OpenPlanter meta-analysis integration.

Reads results.tsv + git log + current train.py state to identify
patterns in experiment results and propose next hypotheses.

Usage:
  python meta_analyze.py [--workspace DIR] [--write-hypotheses PATH]
"""

import argparse
import pathlib
import subprocess
import sys
from datetime import datetime


def build_analysis_task(workspace: pathlib.Path) -> str:
    """Build the investigation task string from available experiment data."""
    results_tsv = workspace / "results.tsv"
    train_py = workspace / "train.py"

    # Read results
    results_content = results_tsv.read_text() if results_tsv.exists() else "(no results yet)"

    # Read git log
    try:
        git_log = subprocess.check_output(
            ["git", "log", "--oneline", "-20"],
            cwd=workspace,
            text=True,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        git_log = "(git log unavailable)"

    # Read last 60 lines of train.py (agent's most recent changes)
    if train_py.exists():
        lines = train_py.read_text().splitlines()
        train_snippet = "\n".join(lines[-60:])
    else:
        train_snippet = "(train.py not found)"

    return f"""You are a research analyst for an autonomous ML training experiment system.

## Context
The autoresearch system modifies a 50M parameter GPT model (train.py) and trains for exactly 5 minutes.
The metric is val_bpb (validation bits per byte) — LOWER IS BETTER. Baseline: 0.997900.
The model uses: RoPE, RMS Norm, GQA attention, Muon+AdamW optimizer, Flash Attention 3, Value Embeddings.

## Experiment Results (results.tsv)
{results_content}

## Git Log (recent commits)
{git_log}

## Current train.py (last 60 lines — most recent agent changes)
```python
{train_snippet}
```

## Your Task
Analyze the experiment history and produce a meta-analysis report. Specifically:

1. **What worked**: Identify which experiments improved val_bpb vs baseline (0.997900). What did they have in common architecturally?

2. **What failed and why**: Identify patterns in discarded experiments. Are there systematic failure modes?

3. **Untried combinations**: Were there two individually-weak changes that might compound positively?

4. **Proposed hypotheses** (EXACTLY 5): For each, specify:
   - The exact Python/config change to make in train.py
   - Expected val_bpb direction (improve/degrade/uncertain)
   - Confidence (high/medium/low) and reasoning

5. **Priority order**: Which hypothesis should be tried first and why?

Format your output as structured markdown with clear headers. Be specific about exact parameter values and code changes.
"""


def try_openplanter(task: str, workspace: pathlib.Path) -> str | None:
    """Try to run OpenPlanter agent. Returns output string or None on failure."""
    # Attempt 1: import directly
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).parent))
        from openplanter.engine import RLMEngine
        from openplanter.model import create_model
        from openplanter.config import AgentConfig
        from openplanter.tools import WorkspaceTools

        config = AgentConfig(
            workspace=workspace,
            provider="anthropic",
            model="claude-sonnet-4-6",
            recursive=False,
            max_steps_per_call=20,
            max_solve_seconds=240,
        )

        model = create_model(config)
        tools = WorkspaceTools(config)
        engine = RLMEngine(model=model, tools=tools, config=config)
        result = engine.solve(task)
        return result
    except Exception as e:
        print(f"[meta_analyze] OpenPlanter direct import failed: {e}", file=sys.stderr)

    # Attempt 2: subprocess CLI
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "openplanter",
                "--headless",
                "--task", task,
                "--workspace", str(workspace),
                "--no-tui"
            ],
            capture_output=True,
            text=True,
            timeout=240
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except Exception as e:
        print(f"[meta_analyze] OpenPlanter subprocess failed: {e}", file=sys.stderr)

    return None


def try_anthropic_direct(task: str) -> str:
    """Direct Anthropic API call — guaranteed fallback."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": task}]
    )
    return response.content[0].text


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenPlanter meta-analysis for deep-loop")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace directory with results.tsv"
    )
    parser.add_argument(
        "--write-hypotheses",
        default="next-hypotheses.md",
        help="Output file for proposed hypotheses"
    )
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    output_path = workspace / args.write_hypotheses

    print(f"[meta_analyze] Workspace: {workspace}")
    print(f"[meta_analyze] Output: {output_path}")

    task = build_analysis_task(workspace)

    # Try OpenPlanter first, fall back to direct Anthropic
    print("[meta_analyze] Attempting OpenPlanter analysis...")
    result = try_openplanter(task, workspace)

    if result is None:
        print("[meta_analyze] Falling back to direct Anthropic API...")
        result = try_anthropic_direct(task)

    # Write output
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"# Meta-Analysis — {ts}\n\n{result}\n"
    output_path.write_text(content)

    print(f"[meta_analyze] Written to {output_path}")
    print(f"[meta_analyze] Summary (first 300 chars): {result[:300]}")


if __name__ == "__main__":
    main()
