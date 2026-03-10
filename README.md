# deep-loop

**Two-tier autonomous research: experiments + meta-analysis**

Built on [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) and [ShinMegamiBoson's OpenPlanter](https://github.com/ShinMegamiBoson/OpenPlanter). deep-loop combines both into a single system where one agent runs experiments and another periodically steps back to find what's working and generate smarter hypotheses.

## What It Does

deep-loop has two modes:

### Mode 1: ML Experiments (autoresearch + meta-analysis)
A Claude Code agent modifies `train.py`, runs 5-minute training jobs on GPU, logs results, and iterates. Every 12 experiments (or after a significant improvement), OpenPlanter analyzes all results to identify patterns and propose smarter hypotheses.

### Mode 2: Domain Research (web search + synthesis)
A Claude Code agent picks questions from `program.md`, searches the web, synthesizes findings into `report.md`, and records entries in `knowledge_index.tsv`. Every 5 entries, the meta-analysis tier evaluates research quality and rewrites the strategy.

Both modes share the same core loop: **experiment → record → meta-analyze → adapt → repeat.**

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
│   reads: program.md (research direction / hypotheses)           │
│   edits: train.py (ML mode) or report.md (research mode)       │
│   runs:  uv run train.py (ML) or web search (research)         │
│   logs:  results.tsv (ML) or knowledge_index.tsv (research)    │
│                                                                 │
│   At regular intervals:                                         │
│   ───────────────────────────────────────────────────────────   │
│                               │                                 │
│                               ▼                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │               meta_analyze.py                           │   │
│   │                                                         │   │
│   │   reads: results + git log + current state              │   │
│   │   calls: OpenPlanter or Anthropic API                   │   │
│   │   writes: next-hypotheses.md / rewrites program.md      │   │
│   └─────────────────────────────────────────────────────────┘   │
│                               │                                 │
│                               ▼                                 │
│   Agent adapts strategy based on meta-analysis output           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### ML Mode (GPU required)

```bash
# Clone and setup
git clone https://github.com/kilroycreative/deep-loop && cd deep-loop
./setup.sh

# Run in tmux
tmux new-session -s deep-loop
python orchestrate.py --tag exp1

# Monitor from another terminal
python orchestrate.py --status
```

### Domain Research Mode

1. Edit `program.md` — replace `YOUR_TOPIC_HERE` with your research topic
2. Run `/loop` in Claude Code (reads `.claude/commands/loop.md`)
3. The agent will search, synthesize, and build `report.md` autonomously
4. Every 5 entries, meta-analysis evaluates and adapts the strategy

## Files

| File | Role | Modify? |
|------|------|---------|
| `program.md` | Research direction + strategy (mutable by meta-agent) | Set topic, then let meta-agent evolve |
| `CLAUDE.md` | Research constitution (invariants) | Rarely |
| `train.py` | Model + training loop (ML mode) | Agent only |
| `prepare.py` | Data pipeline + eval (from autoresearch) | **NEVER** |
| `orchestrate.py` | Main entry point, launches agent | No |
| `meta_analyze.py` | Meta-analysis integration | No |
| `notify.py` | Sends events on breakthroughs | No |
| `report.md` | Research output (research mode) | Agent only |
| `knowledge_index.tsv` | Research audit trail | Agent only |
| `process_log.md` | Meta-analysis methodology log | meta_analyze.py only |
| `results.tsv` | Experiment log (ML mode) | Agent only |
| `openplanter/` | OpenPlanter agent source | No |

## Cost Estimate

For an overnight ML run (~12 hours, ~100+ experiments):

| Component | Cost |
|-----------|------|
| H100 compute (~12h @ $2/hr) | ~$24 |
| Claude Opus agent (experiments) | ~$20 |
| Claude Sonnet meta-analysis (~8 runs) | ~$0.50 |
| **Total** | **~$45** |

Domain research mode costs vary by topic breadth — roughly $5–15 of API usage per 20-entry research session.

## Notifications

When breakthroughs occur, `notify.py` pings OpenClaw:

```bash
# ML mode — val_bpb threshold crossed
python notify.py --event breakthrough --val 0.9891

# Research mode — significant insight
python notify.py --event breakthrough --val "insight: discovered dominant standard"
```

## Commands

```bash
# ML: Start experiment loop
python orchestrate.py --tag <name>

# ML: Check progress
python orchestrate.py --status

# ML: Run meta-analysis manually
python orchestrate.py --meta-only

# Research: Start autonomous research loop
# (run /loop in Claude Code)
```

## Attribution

- **[autoresearch](https://github.com/karpathy/autoresearch)** by Andrej Karpathy — the autonomous ML experiment loop that deep-loop's inner tier is built on
- **[OpenPlanter](https://github.com/ShinMegamiBoson/OpenPlanter)** by ShinMegamiBoson — the meta-analysis agent that powers deep-loop's outer tier

## License

MIT
