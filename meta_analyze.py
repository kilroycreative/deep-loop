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
    """Build the gap analysis task string from knowledge index and report."""
    knowledge_tsv = workspace / "knowledge_index.tsv"
    report_md = workspace / "report.md"

    # Read knowledge index
    knowledge_content = knowledge_tsv.read_text() if knowledge_tsv.exists() else "(no entries yet)"

    # Read report (first 100 lines for context)
    if report_md.exists():
        lines = report_md.read_text().splitlines()
        report_snippet = "\n".join(lines[:100])
    else:
        report_snippet = "(no report yet)"

    return f"""You are a research strategist for an autonomous domain research system.

## Context
The research topic is: **AI agent credential delegation** — how AI agents request, receive, use, and manage credentials (OAuth tokens, API keys, etc.) on behalf of users.

The goal is comprehensive, verified, cited coverage of this domain. The agent has been running a research loop and recording findings.

## Current Knowledge Index (knowledge_index.tsv)
{knowledge_content}

## Report Progress (first 100 lines of report.md)
{report_snippet}

## Your Task
Analyze the research progress and identify the highest-value next questions to investigate. Specifically:

1. **Coverage gaps**: Which major sub-topics of agent credential delegation have NOT been covered or are only partially covered?

2. **Weak entries**: Which answered questions have LOW confidence or marked as partial/conflicting? What would strengthen them?

3. **Emerging threads**: What topics appear in gaps_identified entries that haven't been followed up on?

4. **Proposed questions** (EXACTLY 5): For each, specify:
   - The exact research question to answer
   - Why it matters for understanding agent credential delegation
   - What to search for (suggested search queries or sources)
   - Priority: HIGH | MEDIUM | LOW

5. **Priority order**: Which question should be investigated first and why?

Format your output as structured markdown with clear headers. Be specific and actionable.
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
        default="next-questions.md",
        help="Output file for proposed next research questions"
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
    content = f"# Research Gap Analysis — {ts}\n\n{result}\n"
    output_path.write_text(content)

    print(f"[meta_analyze] Written to {output_path}")
    print(f"[meta_analyze] Summary (first 300 chars): {result[:300]}")


if __name__ == "__main__":
    main()
