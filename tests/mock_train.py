#!/usr/bin/env python3
"""
Mock training script for deep-loop tests.
Outputs the same format as train.py but runs in ~1 second.
Controlled by environment variables:
  MOCK_VAL_BPB=0.994 (default: random improvement 50% of the time)
  MOCK_VRAM_MB=44000 (default: 44000)
  MOCK_CRASH=1 (simulate a crash — exits non-zero with no output)
  MOCK_SLOW=1 (sleep 12s to simulate timeout)
"""
import os, sys, time, random

if os.environ.get("MOCK_CRASH"):
    print("RuntimeError: CUDA out of memory", file=sys.stderr)
    sys.exit(1)

if os.environ.get("MOCK_SLOW"):
    time.sleep(12)

time.sleep(1.0)  # simulate real training time

val_bpb = float(os.environ.get("MOCK_VAL_BPB",
    str(round(random.uniform(0.985, 1.005), 6))))
vram_mb = float(os.environ.get("MOCK_VRAM_MB", "44000"))
training_seconds = round(random.uniform(295, 305), 1)
total_seconds = round(training_seconds + 20, 1)

print(f"""
---
val_bpb:          {val_bpb:.6f}
training_seconds: {training_seconds}
total_seconds:    {total_seconds}
peak_vram_mb:     {vram_mb}
mfu_percent:      39.80
total_tokens_M:   499.6
num_steps:        953
num_params_M:     50.3
depth:            8
""")
