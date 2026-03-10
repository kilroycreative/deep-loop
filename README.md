# deep-loop

**Autonomous research with self-evolving methodology**

An AI agent researches a domain. A meta-agent watches the research, measures what's working, rewrites the research strategy, and commits it. The git log of `program.md` becomes the genealogy of how the methodology evolved.

Two tiers, one feedback loop. The system gets smarter over time — not because the model improves, but because the process does.

## How It Works

```
 ┌──────────────────────────────────────────────────────────┐
 │                    Research Agent                         │
 │                                                          │
 │   reads: program.md (strategy), process_log.md (context) │
 │   searches: web (verified, cited sources only)            │
 │   writes: knowledge_index.tsv + report.md                 │
 │                                                          │
 │   Every 5 entries:                                        │
 │   ─────────────────                                       │
 │          │                                                │
 │          ▼                                                │
 │   ┌──────────────────────────────────────────────────┐    │
 │   │              Meta-Analysis Agent                  │    │
 │   │                                                   │    │
 │   │  measures: cohort quality, confidence, efficiency │    │
 │   │  compares: this cohort vs previous cohort         │    │
 │   │  identifies: which question types work best       │    │
 │   │  rewrites: program.md section 4 (strategy)        │    │
 │   │  appends: process_log.md (reasoning)              │    │
 │   │  commits: both files with meta: prefix            │    │
 │   └──────────────────────────────────────────────────┘    │
 │          │                                                │
 │          ▼                                                │
 │   Research agent reads new program.md → adapts            │
 └──────────────────────────────────────────────────────────┘
```

The research agent follows the strategy in `program.md`. Every 5 entries, `meta_analyze.py` fires: it measures cohort quality (citation density, confidence distribution, search efficiency), compares to the previous cohort, identifies which question types yielded the richest findings, rewrites the strategy section of `program.md`, logs its reasoning to `process_log.md`, and commits both.

The research agent picks up the new strategy on its next iteration. The process evolves.

## What Makes This Different

Most AI research loops optimize the *output*. deep-loop optimizes the *process*.

- **`program.md` is mutable.** The strategy section gets rewritten by meta-analysis after every cohort. Version-tracked. Each rewrite is a commit.
- **`process_log.md` is the methodology memory.** Structured cohort comparisons with before/after metrics, explicit hypotheses, and testable predictions about what the next strategy change will produce.
- **Question type classification.** `meta_analyze.py` categorizes questions (comparative, failure-mode, production-implementation, etc.) and measures which types yield HIGH-confidence, well-cited entries. Strategy rewrites promote what works and deprioritize what doesn't.
- **The git log is the genealogy.** `git log program.md` shows how the research methodology evolved — which strategies were tried, which worked, and why they changed.

## Example: What the System Learned

Over 36 entries researching AI agent credential delegation:

| Cohort | Strategy | Result |
|--------|----------|--------|
| v0 (Q1-Q26) | Static seed questions, no prioritization | 88% HIGH confidence, but diminishing returns on standards questions |
| v1 (Q27-Q31) | Promoted comparative + failure-mode, killed market/survey | 100% HIGH confidence, comparative analysis consistently richest |
| v2 (Q32-Q36) | Diversified entity sets, added efficiency tracking | Maintained 100% HIGH, discovered failure-mode questions reveal architectural truths |
| v3 (Q37+) | Co-promoted failure-mode to #1, added developer-experience track | In progress |

The system discovered on its own that "what breaks when X happens?" questions produce higher-quality findings than "how does X work?" questions — and rewrote its strategy accordingly.

## Quick Start

```bash
git clone https://github.com/kilroycreative/deep-loop.git
cd deep-loop

# Set up Python environment
python -m venv .venv && source .venv/bin/activate
pip install anthropic pytest

# Export your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Launch in tmux
tmux new-session -s deep-loop
python orchestrate.py --tag my-research
```

The agent runs in a Claude Code tmux session. It will:
1. Read `CLAUDE.md` (research constitution — invariants, quality bar)
2. Read `program.md` (current strategy) and `process_log.md` (methodology context)
3. Pick a question based on strategy priorities
4. Search the web, synthesize, cite, log to `knowledge_index.tsv` + `report.md`
5. Every 5 entries: trigger meta-analysis → strategy rewrite → commit → adapt

## Files

| File | Who writes it | Role |
|------|--------------|------|
| `program.md` | Meta-agent | Research strategy (mutable). Versioned. Section 4 is the evolving surface. |
| `process_log.md` | Meta-agent | Methodology memory. Cohort comparisons, strategy reasoning. |
| `CLAUDE.md` | Human | Research constitution. Invariants, quality bar, [BLOCK] rules. |
| `knowledge_index.tsv` | Research agent | Structured index of every question answered. Audit trail. |
| `report.md` | Research agent | Growing research document. Cited, confidence-flagged. |
| `meta_analyze.py` | Human | Cohort analysis, question classification, program.md rewriter. |
| `orchestrate.py` | Human | Launches research agent in tmux, triggers meta-analysis. |
| `notify.py` | System | Sends notifications on breakthroughs/completion. |
| `results.tsv` | Research agent | Experiment log (ML mode). |

## Commands

```bash
# Start research loop
python orchestrate.py --tag <name>

# Check status
python orchestrate.py --status

# Run meta-analysis manually
python meta_analyze.py [--workspace .] [--cohort-size 5] [--dry-run]

# Dry run (see what meta-analysis would do without committing)
python meta_analyze.py --dry-run
```

## Adapting to Your Domain

deep-loop is domain-agnostic. To research something else:

1. Edit `program.md` — change the problem statement and seed question
2. Edit `CLAUDE.md` — update the identity section to describe your domain
3. Clear `knowledge_index.tsv` and `report.md`
4. Run `python orchestrate.py --tag your-topic`

The meta-analysis machinery works on any domain. It measures research quality and evolves the strategy regardless of what's being researched.

## Architecture Decisions

- **Claude Code as the research agent.** It has web search, file I/O, and git built in. No custom tooling needed for the inner loop.
- **Separate meta-analysis process.** `meta_analyze.py` runs as a standalone script, not inside the research agent. This prevents the agent from gaming its own evaluation.
- **TSV over database.** Flat files are diffable, greppable, and git-friendly. The research agent appends rows; meta-analysis reads them. No state synchronization needed.
- **Fail-closed constitution.** `CLAUDE.md` uses `[BLOCK]` tags on invariants. Violations invalidate the entry. The research agent cannot modify its own constitution or the meta-analysis code.
- **Surgical rewrites.** Meta-analysis only touches Section 4 of `program.md`. The problem statement, setup protocol, and research rules are stable. This keeps the versioning meaningful — each diff shows exactly what strategic choice changed.

## Cost

For an overnight research run (~50 entries):

| Component | Estimate |
|-----------|----------|
| Claude Opus (research agent) | ~$15-25 |
| Claude Sonnet (meta-analysis, ~10 runs) | ~$1 |
| **Total** | **~$16-26** |

No GPU required. This is pure research — web search, synthesis, and writing.

## License

MIT
