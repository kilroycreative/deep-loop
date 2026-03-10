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
import time
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


def run_meta_analysis(dry_run: bool = False) -> bool:
    """Run second-order meta-analysis. Rewrites program.md + process_log.md."""
    print("Running meta-analysis v2 (second-order process evolution)...")
    cmd = [
        sys.executable, "meta_analyze.py",
        "--workspace", ".",
        "--cohort-size", "5",
    ]
    if dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(cmd, timeout=300)
    return result.returncode == 0


def run_agent(tag: str, dry_run: bool = False) -> None:
    """Launch Claude Code in a tmux session and send /loop."""
    branch = f"deep-loop/{tag}"
    session = "deep-loop"

    if dry_run:
        print(f"[dry-run] Would: git checkout -B {branch}")
        print(f"[dry-run] Would: init results.tsv if missing")
        print(f"[dry-run] Would: tmux new-session -d -s {session}")
        print(f"[dry-run] Would: tmux send-keys claude --dangerously-skip-permissions Enter")
        print(f"[dry-run] Would: tmux send-keys /loop Enter")
        print(f"[dry-run] Attach: tmux attach -t {session}")
        return

    subprocess.run(["git", "checkout", "-B", branch], check=True)
    print(f"Branch: {branch}")
    init_results_tsv()

    # Kill any existing session with this name
    subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True)

    # Create new detached tmux session
    subprocess.run([
        "tmux", "new-session", "-d", "-s", session,
        "-x", "220", "-y", "50"
    ], check=True)
    print(f"tmux session '{session}' created")

    # Start Claude Code
    subprocess.run([
        "tmux", "send-keys", "-t", session,
        "claude --dangerously-skip-permissions", "Enter"
    ], check=True)

    print("Waiting for Claude Code to initialize...")
    time.sleep(4)

    # Send /loop
    subprocess.run([
        "tmux", "send-keys", "-t", session,
        "/loop", "Enter"
    ], check=True)

    print()
    print(f"✓ Claude Code is running /loop in tmux session '{session}'")
    print(f"  Attach:   tmux attach -t {session}")
    print(f"  Detach:   Ctrl+B then D (while attached)")
    print(f"  Status:   python orchestrate.py --status")
    print(f"  Meta:     python orchestrate.py --meta-only")
    print(f"  Stop:     tmux kill-session -t {session}")


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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without actually running"
    )
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.meta_only:
        run_meta_analysis()
        return

    run_agent(args.tag, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
