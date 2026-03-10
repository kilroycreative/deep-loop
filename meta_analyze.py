#!/usr/bin/env python3
"""
meta_analyze.py v2 — Second-order research process evolution.

Reads knowledge_index.tsv + program.md + process_log.md to:
1. Measure current cohort quality (citation density, confidence, search efficiency)
2. Compare to previous cohort (before/after delta)
3. Identify which question types yield the best results (second-order learning)
4. Rewrite program.md strategy section based on learned patterns
5. Append reflection to process_log.md
6. Git commit both files

Usage:
  python meta_analyze.py [--workspace DIR] [--cohort-size N] [--dry-run]
"""

import argparse
import csv
import io
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime


def parse_knowledge_index(workspace: pathlib.Path) -> list[dict]:
    """Parse knowledge_index.tsv into list of dicts."""
    tsv_path = workspace / "knowledge_index.tsv"
    if not tsv_path.exists():
        return []

    entries = []
    content = tsv_path.read_text()
    reader = csv.DictReader(io.StringIO(content), delimiter="\t")
    for row in reader:
        # Normalize field names (strip whitespace)
        row = {k.strip(): v.strip() if v else "" for k, v in row.items()}
        entries.append(row)
    return entries


def get_program_version(workspace: pathlib.Path) -> str:
    """Extract current program.md version."""
    program_path = workspace / "program.md"
    if not program_path.exists():
        return "v0"
    content = program_path.read_text()
    match = re.search(r"\*\*Version:\*\*\s*(v\d+)", content)
    return match.group(1) if match else "v0"


def compute_cohort_metrics(entries: list[dict]) -> dict:
    """Compute quality metrics for a cohort of entries."""
    if not entries:
        return {
            "count": 0,
            "high_pct": 0, "medium_pct": 0, "low_pct": 0,
            "avg_sources": 0, "avg_searches": 0,
            "question_types": {},
        }

    n = len(entries)

    # Confidence distribution
    high = sum(1 for e in entries if e.get("confidence", "").upper() == "HIGH")
    medium = sum(1 for e in entries if e.get("confidence", "").upper() == "MEDIUM")
    low = sum(1 for e in entries if e.get("confidence", "").upper() == "LOW")

    # Source density
    source_counts = []
    for e in entries:
        sources = e.get("sources", "")
        count = len([s for s in sources.split("|") if s.strip()]) if sources else 0
        source_counts.append(count)
    avg_sources = sum(source_counts) / n if n else 0

    # Search efficiency (if tracked)
    search_counts = []
    for e in entries:
        sc = e.get("search_count", "")
        if sc and sc.isdigit():
            search_counts.append(int(sc))
    avg_searches = sum(search_counts) / len(search_counts) if search_counts else 0

    # Question type classification (heuristic)
    type_counts: dict[str, list[dict]] = {}
    for e in entries:
        qtype = classify_question(e.get("question", ""))
        type_counts.setdefault(qtype, []).append(e)

    question_types = {}
    for qtype, qentries in type_counts.items():
        qn = len(qentries)
        qhigh = sum(1 for qe in qentries if qe.get("confidence", "").upper() == "HIGH")
        qsources = []
        for qe in qentries:
            sources = qe.get("sources", "")
            qsources.append(len([s for s in sources.split("|") if s.strip()]) if sources else 0)
        question_types[qtype] = {
            "count": qn,
            "high_pct": round(qhigh / qn * 100) if qn else 0,
            "avg_sources": round(sum(qsources) / qn, 1) if qn else 0,
        }

    return {
        "count": n,
        "high_pct": round(high / n * 100) if n else 0,
        "medium_pct": round(medium / n * 100) if n else 0,
        "low_pct": round(low / n * 100) if n else 0,
        "avg_sources": round(avg_sources, 1),
        "avg_searches": round(avg_searches, 1),
        "question_types": question_types,
    }


def classify_question(question: str) -> str:
    """Heuristic classification of question type."""
    q = question.lower()

    # Order matters — more specific patterns first
    if any(w in q for w in ["security", "attack", "vulnerability", "threat", "mitigation", "abuse", "injection", "revocation", "failure mode"]):
        return "security-threat"
    if any(w in q for w in ["production", "implement", "deploy", "how does", "work in detail", "handle", "in practice", "actually"]):
        return "production-implementation"
    if any(w in q for w in ["compare", "vs", "differ", "interop", "across", "gap between"]):
        return "comparative-analysis"
    if any(w in q for w in ["rfc", "standard", "spec", "draft", "ietf", "oidc", "oauth", "protocol", "claim", "token exchange"]):
        return "standards-specs"
    if any(w in q for w in ["enterprise", "customer", "rfp", "compliance", "soc2", "market", "pricing", "business", "need"]):
        return "market-enterprise"
    if any(w in q for w in ["who", "player", "vendor", "landscape", "ecosystem", "framework"]):
        return "landscape-survey"
    if any(w in q for w in ["what", "exist", "pattern", "approach", "say about"]):
        return "foundational-survey"

    return "other"


def build_meta_task(
    workspace: pathlib.Path,
    current_cohort: list[dict],
    previous_cohort: list[dict],
    current_metrics: dict,
    previous_metrics: dict,
    current_version: str,
    process_log_content: str,
    program_content: str,
) -> str:
    """Build the prompt for the meta-analysis agent."""

    # Format cohort entries compactly
    def fmt_entries(entries: list[dict]) -> str:
        lines = []
        for e in entries:
            lines.append(
                f"- Q: {e.get('question', '?')}\n"
                f"  Confidence: {e.get('confidence', '?')} | "
                f"Sources: {len([s for s in e.get('sources', '').split('|') if s.strip()])} | "
                f"Status: {e.get('status', '?')}"
            )
        return "\n".join(lines)

    return f"""You are a research methodology strategist. Your job is NOT to suggest research questions.
Your job is to analyze HOW research is being conducted and rewrite the research process to make it better.

## Context

The research system studies: **AI agent credential delegation**.
It runs in a loop: pick a question → web search → synthesize → write to knowledge_index.tsv → repeat.
Every {len(current_cohort)} entries, you (the meta-agent) analyze the cohort and rewrite program.md.

## Current program.md version: {current_version}

```markdown
{program_content}
```

## Previous Cohort Metrics (entries before this batch)
{json.dumps(previous_metrics, indent=2)}

## Current Cohort (latest {len(current_cohort)} entries)
{fmt_entries(current_cohort)}

## Current Cohort Metrics
{json.dumps(current_metrics, indent=2)}

## Process Log (methodology reflections so far)
{process_log_content[:3000]}

## Your Task — Two Outputs

### Output 1: Process Log Entry

Write a cohort analysis following this format EXACTLY:

```
### Cohort <N> Analysis (YYYY-MM-DD)

**program.md version:** {current_version}

**Cohort metrics:**
| Metric | Previous | Current | Delta |
|--------|----------|---------|-------|
| Entries | ... | ... | ... |
| HIGH confidence % | ... | ... | ... |
| Avg sources per entry | ... | ... | ... |
| Avg searches per entry | ... | ... | ... |

**Question type breakdown:**
- <type>: <count> entries, <avg confidence>, <avg sources>

**What worked:**
<which strategies/question types yielded HIGH confidence with fewer searches>

**What didn't:**
<which strategies/question types produced LOW confidence or needed many searches>

**Strategy change:**
<what you're changing in program.md and why — be specific>

**Hypothesis for next cohort:**
<what you expect to see if the change works>
```

### Output 2: Revised program.md Section 4

Rewrite ONLY section 4 ("Current Research Strategy") of program.md based on what you learned.
Be specific. If production-implementation questions outperform standards-spec questions,
say that and reorder priorities. If a stopping heuristic isn't working, change it.

Also increment the version number and update the metadata at the top.

Format your response as:

```
===PROCESS_LOG===
<the process log entry>
===END_PROCESS_LOG===

===PROGRAM_SECTION_4===
<the revised section 4 content>
===END_PROGRAM_SECTION_4===

===VERSION===
<new version string, e.g., v1>
===END_VERSION===

===COMMIT_MESSAGE===
<one-line commit message starting with "meta: ">
===END_COMMIT_MESSAGE===
```
"""


def try_openplanter(task: str, workspace: pathlib.Path) -> str | None:
    """Try to run OpenPlanter agent. Returns output string or None on failure."""
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
        max_tokens=3000,
        messages=[{"role": "user", "content": task}]
    )
    return response.content[0].text


def parse_meta_output(output: str) -> dict:
    """Parse structured meta-agent output."""
    result = {}

    for tag in ["PROCESS_LOG", "PROGRAM_SECTION_4", "VERSION", "COMMIT_MESSAGE"]:
        pattern = rf"==={tag}===\s*\n(.*?)\n===END_{tag}==="
        match = re.search(pattern, output, re.DOTALL)
        result[tag.lower()] = match.group(1).strip() if match else None

    return result


def apply_program_rewrite(
    workspace: pathlib.Path,
    new_section_4: str,
    new_version: str,
) -> None:
    """Rewrite program.md with new section 4 and version."""
    program_path = workspace / "program.md"
    content = program_path.read_text()

    # Update version
    content = re.sub(
        r"\*\*Version:\*\*\s*v\d+",
        f"**Version:** {new_version}",
        content,
    )

    # Update "Last rewritten by"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = re.sub(
        r"\*\*Last rewritten by:\*\*.*",
        f"**Last rewritten by:** meta-agent ({ts})",
        content,
    )

    # Update cohort
    content = re.sub(
        r"\*\*Cohort:\*\*.*",
        f"**Cohort:** {new_version}",
        content,
    )

    # Replace section 4
    # Match from "## 4." to the next "## 5." or "## 6."
    section_4_pattern = r"(## 4\. Current Research Strategy\n)(.*?)((?=\n## [56]\.))"
    if re.search(section_4_pattern, content, re.DOTALL):
        content = re.sub(
            section_4_pattern,
            rf"## 4. Current Research Strategy\n\n{new_section_4}\n\n",
            content,
            flags=re.DOTALL,
        )
    else:
        print("[meta_analyze] WARNING: Could not find section 4 boundary, appending.", file=sys.stderr)

    program_path.write_text(content)


def append_process_log(workspace: pathlib.Path, entry: str) -> None:
    """Append a new entry to process_log.md."""
    log_path = workspace / "process_log.md"
    if not log_path.exists():
        log_path.write_text("# deep-loop Process Log\n\n## Entries\n\n")

    content = log_path.read_text()
    content += f"\n{entry}\n"
    log_path.write_text(content)


def git_commit(workspace: pathlib.Path, message: str) -> bool:
    """Stage program.md + process_log.md and commit."""
    try:
        subprocess.run(
            ["git", "add", "program.md", "process_log.md"],
            cwd=workspace,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=workspace,
            check=True,
            capture_output=True,
        )
        print(f"[meta_analyze] Committed: {message}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[meta_analyze] Git commit failed: {e.stderr}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="deep-loop meta-analysis v2")
    parser.add_argument("--workspace", default=".", help="Workspace directory")
    parser.add_argument("--cohort-size", type=int, default=5, help="Entries per cohort")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing")
    # Legacy compat
    parser.add_argument("--write-hypotheses", default=None, help="(deprecated, ignored)")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    cohort_size = args.cohort_size

    print(f"[meta_analyze v2] Workspace: {workspace}")
    print(f"[meta_analyze v2] Cohort size: {cohort_size}")

    # Load state
    entries = parse_knowledge_index(workspace)
    if len(entries) < cohort_size:
        print(f"[meta_analyze v2] Only {len(entries)} entries, need {cohort_size}. Skipping.")
        return

    current_version = get_program_version(workspace)
    program_content = (workspace / "program.md").read_text() if (workspace / "program.md").exists() else ""
    process_log_content = (workspace / "process_log.md").read_text() if (workspace / "process_log.md").exists() else ""

    # Split into cohorts
    current_cohort = entries[-cohort_size:]
    previous_cohort = entries[-(2 * cohort_size):-cohort_size] if len(entries) >= 2 * cohort_size else []

    current_metrics = compute_cohort_metrics(current_cohort)
    previous_metrics = compute_cohort_metrics(previous_cohort)

    print(f"[meta_analyze v2] Current cohort: {len(current_cohort)} entries")
    print(f"[meta_analyze v2] Previous cohort: {len(previous_cohort)} entries")
    print(f"[meta_analyze v2] Current metrics: {json.dumps(current_metrics, indent=2)}")

    # Build and run meta-analysis
    task = build_meta_task(
        workspace, current_cohort, previous_cohort,
        current_metrics, previous_metrics,
        current_version, process_log_content, program_content,
    )

    print("[meta_analyze v2] Running meta-analysis...")
    result = try_openplanter(task, workspace)
    if result is None:
        print("[meta_analyze v2] Falling back to direct Anthropic API...")
        result = try_anthropic_direct(task)

    # Parse structured output
    parsed = parse_meta_output(result)

    if args.dry_run:
        print("\n=== DRY RUN OUTPUT ===")
        print(f"Process log entry:\n{parsed.get('process_log', '(none)')}")
        print(f"\nNew section 4:\n{parsed.get('program_section_4', '(none)')}")
        print(f"\nNew version: {parsed.get('version', '(none)')}")
        print(f"\nCommit message: {parsed.get('commit_message', '(none)')}")
        return

    # Apply changes
    if parsed.get("process_log"):
        append_process_log(workspace, parsed["process_log"])
        print("[meta_analyze v2] Appended to process_log.md")
    else:
        print("[meta_analyze v2] WARNING: No process log entry generated", file=sys.stderr)

    if parsed.get("program_section_4") and parsed.get("version"):
        apply_program_rewrite(workspace, parsed["program_section_4"], parsed["version"])
        print(f"[meta_analyze v2] Rewrote program.md → {parsed['version']}")
    else:
        print("[meta_analyze v2] WARNING: No program rewrite generated", file=sys.stderr)

    # Commit
    commit_msg = parsed.get("commit_message", f"meta: cohort analysis after {len(entries)} entries")
    git_commit(workspace, commit_msg)

    # Also write next-questions.md for backward compat
    compat_path = workspace / "next-questions.md"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    compat_path.write_text(
        f"# Research Gap Analysis — {ts}\n\n"
        f"See process_log.md for methodology analysis.\n"
        f"See program.md (section 4) for current research strategy.\n"
    )

    print(f"[meta_analyze v2] Done. {len(entries)} total entries processed.")


if __name__ == "__main__":
    main()
