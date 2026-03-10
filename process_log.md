# deep-loop Process Log

> This file is the meta-agent's working memory about methodology.
> It tracks what the system is learning about *how to research*, not *what it's researching*.
> The research agent reads this; only meta_analyze.py writes to it.

---

## Log Format

Each entry follows this structure:

```
### Cohort <N> → <N+1> Analysis (YYYY-MM-DD)

**program.md version:** vN → vN+1

**Cohort metrics:**
| Metric | Cohort N | Cohort N+1 | Delta |
|--------|----------|------------|-------|
| Entries | | | |
| HIGH confidence % | | | |
| MEDIUM confidence % | | | |
| LOW confidence % | | | |
| Avg sources per entry | | | |
| Avg searches per entry | | | |

**Question type breakdown:**
- <type>: <count> entries, <avg confidence>, <avg sources>

**What worked:**
- <observation>

**What didn't work:**
- <observation>

**Strategy change:**
- <what was changed and why>
```

---

## Entries

_No cohort analyses yet. Entries will appear here after the first meta-analysis run._
