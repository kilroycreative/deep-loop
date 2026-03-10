# deep-loop research program

> **This file is mutable.** The meta-agent rewrites it after every cohort analysis.
> Each version is committed with a `meta:` prefix. The git log of this file IS the
> research methodology genealogy.

**Version:** v0
**Last rewritten by:** human (initial)

---

## Problem Statement

Build comprehensive, verified, cited coverage of **YOUR_TOPIC_HERE**.

Replace this with a single sentence describing the domain you want to research.
This is the only invariant. Everything below — the strategy, the question types, the priorities — is subject to revision by meta-analysis.

---

## 1. Setup Protocol

1. **Agree on a tag** with the user (e.g., `mar7`, `quantum-computing`).
2. **Create branch**: `git checkout -b research/<tag>`
3. **Read the research constitution**: `cat CLAUDE.md`
4. **Load existing state**:
   - `cat knowledge_index.tsv 2>/dev/null || echo "(no entries yet)"`
   - `cat report.md 2>/dev/null || echo "(no report yet)"`
   - `cat process_log.md 2>/dev/null || echo "(no process log yet)"`
5. **Confirm starting question** and begin the research loop.

---

## 2. Research Rules

- **Web search before synthesizing** — never assert facts you haven't verified in this session
- **Cite every source** — URL and access date for every claim in report.md
- **Flag confidence** — HIGH / MEDIUM / LOW on every knowledge_index.tsv entry
- **One question at a time** — finish a question before starting the next
- **LOOP FOREVER** — do not stop until the user interrupts you
- **Read process_log.md before generating a new question** — if meta-analysis has run, weight its strategy recommendations when choosing what to investigate next

---

## 3. Output Files

### knowledge_index.tsv (tab-separated)
```
question	answer_summary	sources	confidence	gaps_identified	status	program_version	search_count
```
- question: the research question answered
- answer_summary: 1-2 sentence summary
- sources: pipe-separated URLs
- confidence: HIGH | MEDIUM | LOW
- gaps_identified: follow-on questions this answer raised (pipe-separated)
- status: answered | partial | conflicting
- program_version: which version of program.md was active (e.g., v0, v1, v2)
- search_count: number of web searches performed to answer this question

### report.md (growing document)
Maintain and expand these sections as you learn:

```
# [Your Topic] — Research Report

## Executive Summary
## The Problem Space
## Current Approaches & Patterns
## Key Players & Projects
## Standards & Protocols
## Security Models & Attack Surfaces
## Open Problems & Gaps
## Implications & Recommendations
## Sources
```

### process_log.md (methodology reflection — read-only for research agent)
Written by meta-analysis. Contains cohort comparisons, strategy observations, and
recommendations for program.md rewrites. Read this before each new question to
incorporate learned methodology preferences.

---

## 4. Current Research Strategy

> This section is rewritten by meta-analysis after every cohort (5 entries).
> Before the first cohort, it contains the initial strategy.

**Question generation approach:** Start with the seed question below. Each answer will surface gaps — follow those gaps. After the first meta-analysis run, this section will be rewritten with data-driven priorities.

**Question type priorities (initial — will be rewritten by meta-analysis):**
1. **Foundational survey** — map the landscape. Who are the players? What exists?
2. **Comparative analysis** — how do approaches differ? What tradeoffs do they make?
3. **Production implementation** — what's actually deployed vs. theoretical?
4. **Failure-mode analysis** — what breaks? Where are the gaps?
5. **Standards and specification analysis** — what's codified? What's in draft?

---

## 5. Seed

Start with a single broad question to bootstrap the research:

**Q1: What is the current state of [YOUR_TOPIC_HERE]?**

That's it. Discover the rest.

---

## 6. Meta-Analysis Contract

Every 5 knowledge_index.tsv entries, meta_analyze.py runs. It will:

1. **Measure this cohort** — citation density, confidence distribution, search efficiency (searches per HIGH-confidence answer)
2. **Compare to previous cohort** — did the strategy change improve or degrade quality?
3. **Identify second-order patterns** — which question types yielded the richest findings?
4. **Rewrite this file** — strategy section, question type priorities, stopping heuristics
5. **Write to process_log.md** — the reasoning behind changes
6. **Commit both files** — `git commit -m "meta: <what changed and why>"`

The research agent reads the new program.md on its next iteration and adapts.
