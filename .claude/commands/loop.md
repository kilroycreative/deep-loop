# /loop — Autonomous Research Loop

Load all context, verify setup, and run the deep-loop experiment loop autonomously.

## Context Loading

Run these commands to load state before starting any experiments:

```bash
# 1. Read the research constitution (invariants and rules)
cat CLAUDE.md

# 2. Read the research direction (hypothesis queue)
cat program.md

# 3. Check current branch and experiment count
git branch --show-current
git log --oneline -5

# 4. Read current results
cat results.tsv 2>/dev/null || echo "(no results yet — will initialize)"

# 5. Check if next-hypotheses.md exists from prior meta-analysis
cat next-hypotheses.md 2>/dev/null || echo "(no meta-analysis yet)"

# 6. Read current train.py architecture summary (first 80 lines = config + key classes)
head -80 train.py

# 7. Verify training data exists
ls ~/.cache/autoresearch/data/*.parquet 2>/dev/null | wc -l
```

## Setup Verification

Before starting the loop, verify:

- [ ] Branch is `deep-loop/<tag>` (not master/main). If not: propose a tag and create the branch.
- [ ] results.tsv exists with baseline row (val_bpb=0.997900). If not: create it.
- [ ] Training data exists (at least 1 .parquet file in ~/.cache/autoresearch/). If not: run `uv run prepare.py --num-shards 5` and wait.
- [ ] `uv run python -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count())"` returns `True`. If not: CUDA not available, alert and stop.

## Gap Analysis (run once at session start)

Before the first experiment, do a quick gap analysis between program.md hypotheses and results.tsv:

1. Which hypotheses from program.md have NOT been tried yet?
2. Which prior attempts (if any) came close to improvement but missed?
3. Does next-hypotheses.md (from meta-analysis) suggest anything not in program.md?

State your starting hypothesis clearly: "I will try [X] because [reason]. Expected: val_bpb [improves/degrades/uncertain] because [reasoning]."

## Experiment Loop

LOOP FOREVER (until interrupted):

1. **Propose** — State the next hypothesis clearly in one sentence. Reference CLAUDE.md invariants.
2. **Verify syntax before commit** — `python -c "import ast; ast.parse(open('train.py').read())"`
3. **Commit** — `git add train.py && git commit -m "[hypothesis description]"`
4. **Run** — `uv run train.py > run.log 2>&1`
   - If run takes >10 minutes: kill it (`kill %1`), treat as crash, revert.
5. **Extract results:**
   ```bash
   grep "^val_bpb:\|^peak_vram_mb:\|^training_seconds:\|^total_seconds:" run.log
   ```
6. **Evaluate:**
   - If grep returns nothing → CRASH: record crash row in TSV, `git reset --hard HEAD~1`
   - If val_bpb improved → KEEP: record keep row in TSV
   - If val_bpb same or worse → DISCARD: `git reset --hard HEAD~1`, record discard row in TSV
7. **Check thresholds:**
   - If val_bpb < 0.990: `python notify.py --event breakthrough --val <val>`
   - If val_bpb < 0.985: `python notify.py --event major_breakthrough --val <val>`
8. **Check meta-analysis trigger:**
   - Count: `tail -n +2 results.tsv | grep -v "^baseline" | wc -l`
   - If count is a multiple of 12: `python meta_analyze.py --workspace . --write-hypotheses next-hypotheses.md`
   - Then read next-hypotheses.md and incorporate into next proposal

REPEAT from step 1.

## Stopping Criteria

There are none. Run until interrupted by the user. If you run out of ideas from program.md and next-hypotheses.md, think harder — revisit discarded experiments for combinations, try more radical architectural changes, re-read train.py for untapped levers.

**NEVER ask "should I continue?" — the answer is always yes.**
