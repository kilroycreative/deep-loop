# deep-loop research program

> **This file is mutable.** The meta-agent rewrites it after every cohort analysis.
> Each version is committed with a `meta:` prefix. The git log of this file IS the
> research methodology genealogy.

**Version:** v3
**Last rewritten by:** meta-agent (2026-03-09)
**Cohort:** v3 (post-v2-cohort, 35 entries total — 25 v0 + 5 v1 + 5 v2)

---

## Problem Statement

Build comprehensive, verified, cited coverage of **AI agent credential delegation** — how agents request, receive, use, and manage credentials on behalf of users.

This is the only invariant. Everything below — the strategy, the question types, the priorities — is subject to revision by meta-analysis.

---

## 1. Setup Protocol

1. **Agree on a tag** with the user (e.g., `mar7`, `cred-research`).
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
# AI Agent Credential Delegation — Research Report

## Executive Summary
## The Problem Space
## Current Approaches & Patterns
## Key Players & Projects
## Standards & Protocols
## Security Models & Attack Surfaces
## Open Problems & Gaps
## Implications for Cred
## Sources
```

### process_log.md (methodology reflection — read-only for research agent)
Written by meta-analysis. Contains cohort comparisons, strategy observations, and
recommendations for program.md rewrites. Read this before each new question to
incorporate learned methodology preferences.

---

## 4. Current Research Strategy

> Rewritten by meta-analysis on 2026-03-09 based on v2 cohort analysis (5 entries, Q32-Q36).
> See process_log.md "v2 → v3 Analysis" for reasoning.

**Question generation approach:** Apply the connective-value test before every question: "Will answering this bridge 2+ existing topics in knowledge_index.tsv?" If it only extends a single thread, defer unless that thread has <3 entries.

Maintain comparative framing and failure-mode framing as co-equal top priorities. **Diversify comparison targets** — do not re-compare entity sets already covered (Cedar/CA/FGA, AgentCore/XAA/Entra, cloud-provider IAM engines). **Prioritize newly emerging topics** — IETF WIMSE, graduated/continuous authorization, SPIFFE-MCP integration, lifecycle-aware credentials. These are more likely to yield novel findings than established topics.

**Question type priorities:**
1. **Comparative analysis** (co-#1) — 100% HIGH across all cohorts. Fresh entity sets only. v2 showed entity diversification maintains quality without repetition.
2. **Failure-mode analysis** (co-#1, promoted from #3) — v2 demonstrated failure-mode questions produce the highest-impact findings. Q32 (IdP outage) revealed a critical spec gap; Q36 (stale permissions) unified 4 prior topics into a coherent failure analysis. Ask "what breaks when X happens?" — these reveal architectural truths that happy-path documentation obscures. Target ≥1 of 5 entries.
3. **Production implementation** — v2 confirmed these anchor findings in reality. Target ≥1 of 5 entries. Frame comparatively when possible.
4. **Developer experience** (NEW) — How do the new primitives (CIMD, SPIFFE, XAA, graduated authorization) change the developer journey from env vars to production auth? This thread has been neglected since v0. Target ≥1 of 5 entries.
5. **Security and threat modeling** — Fold into failure-mode or comparative framing when possible. Do not pursue as standalone unless a production finding raises a specific threat question.
6. **Standards and specification analysis** — Only pursue when a production or failure-mode finding raises a specific unanswered spec question. Prioritize WIMSE (newly active) over established specs.

**Deprioritized:**
- **Market-enterprise** — Eliminated since v1, no loss. Continue avoiding.
- **Landscape-survey** — Domain is mapped. No more survey questions.
- **Foundational-survey** — Bootstrap complete.
- **Repeated comparisons** — If the same 2+ entities have already been compared, do not re-compare on a different dimension.
- **Measurement-frontier gaps** — When a gap asks for "measured latency/performance of X" and 2+ entries have failed to find published data, mark it as "measurement-frontier" and deprioritize. The data may not exist publicly yet.

**Stopping heuristic:** A topic is "covered" when report.md has a section with ≥3 independent sources, HIGH confidence, AND at least one comparative entry connecting it to another topic. Isolated coverage doesn't count.

**Efficiency tracking:** Every entry MUST include search_count. v2 baseline: 5.0 searches per HIGH-confidence answer. Target ≤6.0 for v3 (relaxed from ≤5.0 — v2 data showed 5.0 was constraining). If a question requires >7 searches, it's too broad — split it.

**Type classification rule:** Questions with 2+ named entities in comparative framing ("how does X compare to Y") are classified as comparative-analysis, regardless of domain topic.

**Emerging topic priority list** (investigate these before revisiting established topics):
- IETF WIMSE workload identity JWT specification
- Graduated/continuous authorization (beyond binary grant/deny)
- SPIFFE integration with MCP OAuth
- Lifecycle-aware credential management patterns
- Developer experience of CIMD/XAA onboarding

---

## 5. Seed

Start from the current state of knowledge_index.tsv. Pick the highest-priority gap from the most recent answered questions' `gaps_identified` column, or from process_log.md recommendations if available.

If knowledge_index.tsv is empty, start here:

**Q1: What credential delegation patterns exist today for AI agents?**

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
