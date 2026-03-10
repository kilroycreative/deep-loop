# /loop — Autonomous Research Loop

Load all context, verify setup, and run the deep-loop domain research loop autonomously.

## Context Loading

Run these commands before starting:

```bash
# 1. Read the research constitution
cat CLAUDE.md

# 2. Read the research program (strategy + topic)
cat program.md

# 3. Check current branch
git branch --show-current

# 4. Load existing research state
cat knowledge_index.tsv 2>/dev/null || echo "(no entries yet)"
cat report.md 2>/dev/null || echo "(no report yet)"

# 5. Check for meta-analysis context
cat process_log.md 2>/dev/null || echo "(no process log yet)"
```

## Setup Verification

Before starting the loop, verify:

- [ ] Branch is `research/<tag>`. If not: propose a tag and create the branch.
- [ ] `knowledge_index.tsv` exists with header row. If not: create it:
  ```
  question	answer_summary	sources	confidence	gaps_identified	status	program_version	search_count
  ```
- [ ] `report.md` exists with section headers from program.md. If not: create it with empty sections.

## Gap Analysis (run once at session start)

Before the first question:
1. Which seed questions from program.md have NOT been answered yet in knowledge_index.tsv?
2. Does process_log.md suggest anything not yet covered?
3. State your starting question clearly: "I will research [X] because [reason]."

## Research Loop

LOOP FOREVER (until interrupted):

1. **Pick a question** — from seed queue, gaps_identified column, or process_log.md recommendations (weight 2x). State it clearly.
2. **Search** — run web searches for the question. Read at least 2-3 sources before writing.
   - Search strategies: direct query, look for specs/RFCs/GitHub repos, find competing products, find academic papers
   - For standards: look for official spec pages, IETF drafts, official specs
   - For market players: search Product Hunt, GitHub, HN, recent news
3. **Synthesize** — identify what's known, what's contested, what's unknown. Flag confidence level.
4. **Write to report.md** — find the right section and append/update. All claims cited. Uncertain things flagged.
5. **Record in knowledge_index.tsv** — append one row. If answer is partial, mark status=partial and list gaps.
6. **Check breakthrough** — if this finding significantly changes the picture (e.g., found a dominant standard, discovered an unsolved problem, found a key competitor): `python notify.py --event breakthrough --val "insight: <one-line description>"`
7. **Check meta-analysis trigger** — count answered rows in knowledge_index.tsv. If count is a multiple of 5: `python meta_analyze.py --workspace . --write-hypotheses next-questions.md` then read process_log.md for updated strategy.

REPEAT from step 1.

## Stopping Criteria

There are none. Run until interrupted by the user.

**NEVER ask "should I continue?" — the answer is always yes.**

If you run out of seed questions, generate new ones from:
- gaps_identified entries in knowledge_index.tsv
- Adjacent topics that emerged during research
- Specific players or standards worth deeper investigation
