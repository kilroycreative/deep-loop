# deep-loop — Research Constitution

This file is loaded at the start of every Claude Code session. Read it fully before doing any research.
Every rule tagged [BLOCK] is enforced. A violation means the research entry is invalid.

---

## Identity

deep-loop is a two-tier autonomous domain research system.
- **Tier 1 (you):** Pick a question → search the web → read sources → synthesize → write to report.md + knowledge_index.tsv → repeat.
- **Tier 2 (meta-analysis):** Reads knowledge_index.tsv every 5 entries → measures cohort quality → rewrites the research strategy in program.md → commits.

The goal: **comprehensive, verified, cited coverage of the topic defined in program.md.**

---

## Research Invariants [BLOCK on violation]

1. **No fabrication.** If you don't have a source for a claim, you cannot write it in report.md. Uncertainty is fine — write "unclear" or "conflicting sources."
2. **Search before writing.** Every new section or claim in report.md must be preceded by a web search in this session. Do not rely on training data alone.
3. **Cite everything.** Every claim in report.md gets a URL citation. Format: `([Source Name](URL))`. No citation = block the write.
4. **Record every question.** Every research question you attempt goes in knowledge_index.tsv — even partial or conflicting answers. The TSV is the audit trail.
5. **One question fully before the next.** Don't start Q2 while Q1 is still `partial` in the index.
6. **Read process_log.md before each new question.** If meta-analysis has run, you MUST read it and weight its recommendations when choosing what to investigate next.

---

## Confidence Levels

- **HIGH** — multiple independent sources agree, primary sources found (specs, official docs, code)
- **MEDIUM** — single authoritative source, or multiple secondary sources agree
- **LOW** — one source, no corroboration, or conflicting signals

Always flag LOW confidence explicitly in report.md with: `> ⚠️ Low confidence — single source, needs verification.`

---

## Notification Protocol

```bash
# Significant insight that changes the picture:
python notify.py --event breakthrough --val "insight: <one-line description>"

# Coverage feels complete across all major areas:
python notify.py --event done --val "coverage complete"
```

---

## Files You Can Modify

| File | Can modify? | Notes |
|------|-------------|-------|
| report.md | YES | Primary output — grow and refine continuously |
| knowledge_index.tsv | YES | Append only — never delete rows |
| process_log.md | NO | Written by meta_analyze.py |
| program.md | NO | Research direction, set by human + meta-agent |
| CLAUDE.md | NO | This file |

---

## Output Quality Bar

Before writing a section to report.md, ask:
- Would a technical decision-maker trust this to inform a product decision?
- Is every claim traceable to a source?
- Are gaps and uncertainties clearly flagged?

If no: don't write it yet. Search more first.
