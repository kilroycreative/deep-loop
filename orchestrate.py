#!/usr/bin/env python3
"""
deep-loop orchestrator.

Usage:
  python orchestrate.py [--tag TAG] [--meta-interval N]
  python orchestrate.py --meta-only       # run one meta-analysis and exit
  python orchestrate.py --status          # show results.tsv summary
"""

import argparse
import subprocess
import sys
import pathlib
from datetime import datetime


RESULTS_TSV = pathlib.Path("results.tsv")
BASELINE_VAL_BPB = 0.997900
BASELINE_VRAM_MB = 45060.2


def count_experiments(tsv: pathlib.Path = RESULTS_TSV) -> int:
    """Count completed experiment rows (excluding header and baseline)."""
    if not tsv.exists():
        return 0
    rows = [
        line for line in tsv.read_text().splitlines()
        if line.strip()
        and not line.startswith("commit")
        and not line.startswith("baseline")
    ]
    return len(rows)


def get_best_val_bpb(tsv: pathlib.Path = RESULTS_TSV) -> float:
    """Return lowest val_bpb from results.tsv."""
    if not tsv.exists():
        return float("inf")
    best = float("inf")
    for line in tsv.read_text().splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            try:
                v = float(parts[1])
                if 0 < v < best:
                    best = v
            except ValueError:
                pass
    return best


def init_results_tsv() -> None:
    """Create results.tsv with baseline row if it doesn't exist."""
    if not RESULTS_TSV.exists():
        RESULTS_TSV.write_text(
            "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
            f"baseline\t{BASELINE_VAL_BPB}\t{BASELINE_VRAM_MB / 1024:.1f}\tkeep\tbaseline — autoresearch default\n"
        )
        print(f"Initialized {RESULTS_TSV} with baseline")


def show_status() -> None:
    """Print a summary of experiment progress."""
    n = count_experiments()
    best = get_best_val_bpb()
    delta = BASELINE_VAL_BPB - best if best < float("inf") else 0
    print(f"Experiments: {n}")
    print(f"Best val_bpb: {best:.6f} (baseline: {BASELINE_VAL_BPB}, delta: {delta:+.6f})")
    if RESULTS_TSV.exists():
        rows = [
            line for line in RESULTS_TSV.read_text().splitlines()
            if line.strip() and not line.startswith("commit")
        ]
        kept = sum(1 for r in rows if "\tkeep\t" in r)
        discarded = sum(1 for r in rows if "\tdiscard\t" in r)
        crashed = sum(1 for r in rows if "\tcrash\t" in r)
        print(f"  kept={kept} discarded={discarded} crashed={crashed}")


def run_meta_analysis() -> bool:
    """Run OpenPlanter meta-analysis."""
    print("Running OpenPlanter meta-analysis...")
    result = subprocess.run(
        [
            sys.executable, "meta_analyze.py",
            "--workspace", ".",
            "--write-hypotheses", "next-hypotheses.md"
        ],
        timeout=300
    )
    return result.returncode == 0


def run_agent(tag: str) -> None:
    """Launch the Claude Code autoresearch agent."""
    branch = f"deep-loop/{tag}"
    subprocess.run(["git", "checkout", "-B", branch], check=True)
    print(f"Branch: {branch}")

    init_results_tsv()

    prompt = (
        "Read program.md carefully. Follow the Setup Protocol to set up the experiment. "
        "Then run the experiment loop described in the Experimentation section. "
        "Follow the Meta-Analysis Protocol and Notification Protocol exactly as written. "
        "NEVER STOP running experiments until I interrupt you."
    )
    print("Launching Claude Code research agent...")
    subprocess.run(["claude", "--dangerously-skip-permissions", "-p", prompt])


def main() -> None:
    parser = argparse.ArgumentParser(description="deep-loop: autoresearch + OpenPlanter")
    parser.add_argument(
        "--tag",
        default=datetime.now().strftime("mar%d"),
        help="Experiment tag (used for branch name)"
    )
    parser.add_argument(
        "--meta-interval",
        type=int,
        default=12,
        help="Run meta-analysis every N experiments"
    )
    parser.add_argument(
        "--meta-only",
        action="store_true",
        help="Run one OpenPlanter meta-analysis and exit"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show experiment progress and exit"
    )
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.meta_only:
        run_meta_analysis()
        return

    run_agent(args.tag)


if __name__ == "__main__":
    main()
