# deep-loop — Research Constitution

This file is loaded at the start of every Claude Code session. Read it fully before writing any code or running any experiments.
Every rule tagged [BLOCK] is enforced. A violation means the experiment result is invalid and must be discarded.

---

## Identity

deep-loop is a two-tier autonomous ML research system.
- **Tier 1 (you):** Modify train.py → run 5-min training → evaluate val_bpb → commit or revert → repeat.
- **Tier 2 (OpenPlanter):** Reads results.tsv + git log every 12 experiments → finds patterns → writes next-hypotheses.md → you read it.

The goal is simple: **get val_bpb as low as possible within the 5-minute training budget.**
Baseline: val_bpb = 0.997900, peak_vram_mb = 45060.2 (50M param GPT, 12L × 768d, window_pattern="SSSL")

---

## Research Invariants [BLOCK on violation]

1. **Never modify prepare.py.** It is the fixed evaluation harness. Any modification invalidates all results.
2. **Commit before running.** `git commit` before `uv run train.py`. If you run without committing, you cannot trace which change caused which result.
3. **Always verify the run completed.** After every training run, check: `grep "^val_bpb:" run.log`. If that grep returns nothing, the run crashed — do not record a val_bpb of 0.000000 as success.
4. **Only revert on worse-or-equal.** If val_bpb >= baseline_for_this_branch, `git reset --hard HEAD~1`. If val_bpb improves, keep. No exceptions.
5. **No new packages.** pyproject.toml deps are fixed. Using a package not already installed = crash = wasted 5 minutes.
6. **VRAM limit: 65GB.** H100 has 80GB. Stay under 65GB peak_vram_mb to leave headroom. An OOM crash is a discard.
7. **Record every run.** Every completed or crashed run goes in results.tsv. No runs go unrecorded. The TSV is the audit trail.
8. **Read next-hypotheses.md before each batch.** If meta_analyze.py has run and written next-hypotheses.md, you MUST read it before proposing your next idea. Weight its proposals 2x your own intuition.

---

## Experiment Hygiene Rules [BLOCK on violation]

**Before each experiment:**
- [ ] Describe the change in one sentence (this becomes the TSV description)
- [ ] Predict the expected direction of val_bpb change and why
- [ ] Verify no syntax errors: `python -c "import ast; ast.parse(open('train.py').read())"`

**After each experiment:**
- [ ] Run: `grep "^val_bpb:\|^peak_vram_mb:\|^training_seconds:" run.log`
- [ ] If grep returns nothing: run crashed. Record as crash in TSV, `git reset --hard HEAD~1`, move on.
- [ ] If val_bpb improved: `git log --oneline -1` to confirm the commit hash for TSV
- [ ] If val_bpb >= branch_baseline: `git reset --hard HEAD~1` THEN record as discard

**results.tsv format (tab-separated, not comma):**
```
commit	val_bpb	memory_gb	status	description
```
- commit: 7-char git hash (or "baseline" / "crash")
- val_bpb: 6 decimal places
- memory_gb: peak_vram_mb / 1024, 1 decimal place
- status: keep | discard | crash
- description: one sentence, no tabs

---

## Meta-Analysis Protocol

After every 12 experiments (count rows in results.tsv excluding header and baseline):
```bash
python meta_analyze.py --workspace . --write-hypotheses next-hypotheses.md
```
After it completes:
- Read next-hypotheses.md
- Treat its top-ranked hypothesis as your next experiment
- Weight all its proposals 2x your own intuition for the next 6 experiments

---

## Notification Protocol

```bash
# val_bpb broke 0.990 threshold:
python notify.py --event breakthrough --val <val_bpb>

# val_bpb broke 0.985 threshold:
python notify.py --event major_breakthrough --val <val_bpb>
```

---

## Files You Can Modify

| File | Can modify? | Notes |
|------|-------------|-------|
| train.py | YES | Only file the experiment loop changes |
| results.tsv | YES | Append only — never delete rows |
| next-hypotheses.md | NO | Written by meta_analyze.py |
| prepare.py | **NEVER** | Fixed eval harness |
| program.md | NO | Research direction, set by human |
| CLAUDE.md | NO | This file |
