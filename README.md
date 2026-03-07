# deep-loop

**Autonomous ML research with a meta-analysis tier**

One-liner: autoresearch runs experiments. OpenPlanter steps back every hour to find what's working and generate smarter hypotheses. Two agents, one loop.

## What It Does

deep-loop combines two autonomous systems:

1. **autoresearch (inner loop)**: A Claude Code agent that modifies `train.py`, runs 5-minute training jobs on H100, logs results, and iterates. It never stops until you interrupt it.

2. **OpenPlanter (meta-analysis)**: Every 12 experiments (or after a significant improvement), a second agent analyzes all results to identify patterns and propose smarter hypotheses.

The result: an experiment loop that gets smarter over time.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         orchestrate.py                          │
│                    (launches and monitors)                      │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code Agent                           │
│                                                                 │
│   reads: program.md (research direction)                        │
│   edits: train.py (model architecture, hyperparams)             │
│   runs:  uv run train.py (5-min training on H100)               │
│   logs:  results.tsv (experiment record)                        │
│                                                                 │
│   Every 12 experiments OR after >0.003 val_bpb improvement:     │
│   ───────────────────────────────────────────────────────────   │
│                               │                                 │
│                               ▼                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │               meta_analyze.py                           │   │
│   │                                                         │   │
│   │   reads: results.tsv, git log, train.py                 │   │
│   │   calls: OpenPlanter or Anthropic API                   │   │
│   │   writes: next-hypotheses.md                            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                               │                                 │
│                               ▼                                 │
│   Claude Code weights next-hypotheses.md 2x in next batch       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Local GPU (H100/A100)

```bash
# Clone and setup
git clone <repo> && cd deep-loop
./setup.sh

# Run in tmux (so it persists)
tmux new-session -s deep-loop
python orchestrate.py --tag mar7

# Monitor from another terminal
python orchestrate.py --status
```

### H100 Rental (Lambda, RunPod, etc.)

```bash
# SSH in and clone
ssh user@gpu-server
git clone <repo> && cd deep-loop

# Run setup (installs uv, torch, downloads data)
./setup.sh

# Export your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Launch in tmux
tmux new-session -s deep-loop
python orchestrate.py --tag exp1
```

## Files

| File | Role | Modify? |
|------|------|---------|
| `prepare.py` | Data pipeline + eval (from autoresearch) | **NEVER** |
| `train.py` | Model + training loop (agent modifies this) | Agent only |
| `program.md` | Research direction + experiment protocol | Rarely |
| `orchestrate.py` | Main entry point, launches agent | No |
| `meta_analyze.py` | OpenPlanter integration for meta-analysis | No |
| `notify.py` | Sends OpenClaw events on breakthroughs | No |
| `results.tsv` | Experiment log (created at runtime) | Agent only |
| `next-hypotheses.md` | Meta-analysis output (created at runtime) | Never |
| `openplanter/` | OpenPlanter agent source | No |

## Cost Estimate

For an overnight run (~12 hours, ~100+ experiments):

| Component | Cost |
|-----------|------|
| H100 compute (~12h @ $2/hr) | ~$24 |
| Claude Opus agent (experiments) | ~$20 |
| Claude Sonnet meta-analysis (~8 runs) | ~$0.50 |
| **Total** | **~$45** |

## The Research Direction

The agent starts with these hypotheses (from `program.md`):

1. **Window patterns**: Try "SSSSL", "SSL", "SLSL" instead of "SSSL"
2. **Depth vs width**: 16L×640d, 8L×896d, 10L×832d
3. **GQA ratio**: n_kv_head = 2, 3, or 4
4. **Muon LR**: Try 0.02, 0.06, 0.08
5. **Value Embedding frequency**: All layers, every 3rd, first/last only
6. **Vocab size**: 16384 tokens (requires tokenizer retrain)
7. **Sequence packing**: Different buffer sizes

After 12 experiments, OpenPlanter analyzes results and proposes new hypotheses, which the agent weights 2x.

## Notifications

When val_bpb crosses thresholds, `notify.py` pings OpenClaw:

- `val_bpb < 0.990`: "deep-loop: val_bpb=X.XXXXXX broke threshold 0.990"
- `val_bpb < 0.985`: "deep-loop MAJOR: val_bpb=X.XXXXXX broke 0.985"

## Baseline

| Metric | Value |
|--------|-------|
| val_bpb | 0.997900 |
| Parameters | ~50M |
| Layers | 8 (configurable) |
| Model dim | 512 (8 × 64 aspect ratio) |
| Training time | 300 seconds |
| Peak VRAM | ~45 GB |

Goal: beat val_bpb < 0.990 within the 5-minute budget.

## Commands

```bash
# Start experiment loop
python orchestrate.py --tag <name>

# Check progress
python orchestrate.py --status

# Run meta-analysis manually
python orchestrate.py --meta-only

# Send test notification
python notify.py --event breakthrough --val 0.9891
```

## License

MIT
