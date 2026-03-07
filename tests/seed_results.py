#!/usr/bin/env python3
"""Seed results.tsv with fake experiment history for testing."""
import pathlib, sys, random

WORKSPACE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
TSV = WORKSPACE / "results.tsv"

rows = [
    ("commit", "val_bpb", "memory_gb", "status", "description"),
    ("baseline", "0.997900", "44.0", "keep", "baseline — autoresearch default"),
    ("a1b2c3d", "0.994200", "44.1", "keep", "window_pattern SSSSL: more global attention"),
    ("b2c3d4e", "1.002100", "44.0", "discard", "window_pattern SSL: too few global layers"),
    ("c3d4e5f", "0.997800", "43.9", "discard", "n_kv_head=3 GQA: marginal improvement"),
    ("d4e5f6g", "0.991500", "44.3", "keep", "16 layers x 640 embd: depth over width wins"),
    ("e5f6g7h", "0.000000", "0.0", "crash", "vocab_size=16384: OOM on H100"),
    ("f6g7h8i", "0.990800", "44.5", "keep", "Muon LR 0.02 cosine decay: better convergence"),
    ("g7h8i9j", "0.993100", "44.2", "discard", "value embedding every layer: too slow"),
    ("h8i9j0k", "0.989200", "44.6", "keep", "combined: 16L + cosine decay + SSSSL pattern"),
    ("i9j0k1l", "0.988800", "44.7", "keep", "n_kv_head=2 with 16L: GQA savings enable deeper"),
    ("j0k1l2m", "0.988900", "44.8", "discard", "warmup 200 steps: no improvement over current"),
    ("k1l2m3n", "0.987400", "45.0", "keep", "sequence packing: fills padding waste"),
]

TSV.write_text("\n".join("\t".join(r) for r in rows) + "\n")
print(f"Seeded {len(rows)-1} rows to {TSV}")
