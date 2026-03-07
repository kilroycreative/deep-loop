#!/usr/bin/env python3
"""
notify.py — Send experiment milestone events to OpenClaw.

Usage:
  python notify.py --event breakthrough --val 0.9876
  python notify.py --event major_breakthrough --val 0.9823
  python notify.py --event done --val 0.9901 --experiments 87
"""

import argparse
import subprocess
import pathlib
from datetime import datetime


LOG = pathlib.Path("notify.log")

MESSAGES = {
    "breakthrough": "deep-loop: val_bpb={val:.6f} broke threshold 0.990",
    "major_breakthrough": "deep-loop MAJOR: val_bpb={val:.6f} broke 0.985",
    "done": "deep-loop complete: {experiments} experiments, best val_bpb={val:.6f}",
    "crash": "deep-loop: agent crashed after {experiments} experiments (best={val:.6f})",
}


def send(message: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    log_line = f"[{ts}] {message}"
    print(log_line)
    with open(LOG, "a") as f:
        f.write(log_line + "\n")

    try:
        subprocess.run(
            ["openclaw", "system", "event", "--text", message, "--mode", "now"],
            timeout=15,
            capture_output=True
        )
    except Exception as e:
        print(f"[notify] openclaw send failed: {e}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, choices=list(MESSAGES.keys()))
    parser.add_argument("--val", type=float, default=0.0)
    parser.add_argument("--experiments", type=int, default=0)
    args = parser.parse_args()

    template = MESSAGES[args.event]
    message = template.format(val=args.val, experiments=args.experiments)
    send(message)


if __name__ == "__main__":
    main()
