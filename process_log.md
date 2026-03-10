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
<observation about which strategies yielded high-quality entries>

**What didn't:**
<observation about which strategies produced low-confidence or partial entries>

**Strategy change:**
<what was changed in program.md and why>

**Hypothesis for next cohort:**
<what the meta-agent expects to see if the strategy change is correct>
```

---

## Retrospective: Cohort 0 (Bootstrap — Q1-Q26)

> This entry is a one-time retrospective on the pre-v1 research, written to bootstrap
> the process log with observations about the initial run.

**program.md version:** v0 (static, human-written)

**Cohort metrics:**
| Metric | Value |
|--------|-------|
| Entries | 26 |
| HIGH confidence % | 88% (23/26) |
| MEDIUM confidence % | 8% (2/26) |
| LOW confidence % | 0% (0/26) |
| Avg sources per entry | 4.5 |

**Question type breakdown (estimated):**
- Standards/specs: 6 entries (Q4, Q8, Q10-Q13) — HIGH confidence, high source density
- Production implementations: 5 entries (Q14, Q18, Q22, Q24, Q26) — HIGH confidence, most actionable
- Market/enterprise: 5 entries (Q6, Q16, Q17, Q23, Q25) — mixed confidence, harder to verify
- Player landscape: 4 entries (Q3, Q7, Q19, Q20) — HIGH confidence, survey-style
- Security: 4 entries (Q5, Q9, Q15, Q21) — HIGH confidence, well-sourced
- MCP-specific: 2 entries (Q2, Q18) — HIGH confidence, primary sources available

**Observations:**
- Production implementation questions (Q14, Q18, Q26) produced the densest, most actionable findings.
  These connected multiple threads (standards + vendors + architecture) in single entries.
- Standards/spec questions had the highest citation reliability but lower marginal insight after Q4.
  Diminishing returns on "what does RFC X say" after the first 2-3.
- Market/enterprise questions (Q23 pricing, Q25 RFPs) were hardest to verify — fewer authoritative sources,
  more vendor marketing disguised as research.
- The linear Q1→Q26 execution followed seed questions then gaps. No strategic prioritization occurred.
  The system never decided "stop asking about standards, go deeper on production patterns."

**Missing from v0:**
- No search_count tracking — can't measure research efficiency
- No program_version tracking — can't attribute entry quality to methodology
- No second-order analysis — the system never asked "which question types are most productive?"
- program.md never changed — the research process was static while knowledge grew

---

## Entries

(meta_analyze.py appends below this line)

### Cohort 0 → v1 Full Analysis (2026-03-09)

**program.md version:** v0 → v1

**Cohort metrics (all 25 parsed entries under v0):**
| Metric | Value |
|--------|-------|
| Entries | 25 |
| HIGH confidence % | 92% |
| MEDIUM confidence % | 8% |
| LOW confidence % | 0% |
| Avg sources per entry | 4.2 |
| Avg searches per entry | unknown (not tracked in v0) |

**Cohort trend (groups of 5):**
| Metric | Q1-5 | Q6-10 | Q11-15 | Q16-20 | Q21-25 |
|--------|------|-------|--------|--------|--------|
| HIGH % | 100% | 80% | 100% | 100% | 80% |
| Avg sources | 5.0 | 4.6 | 3.6 | 3.8 | 4.0 |

Source density declined from 5.0 to 3.6 through the middle of the run, then stabilized around 4.0. The two MEDIUM-confidence entries (Q6-10 and Q21-25 cohorts) were both market-enterprise type: "What's the pricing/business model" (Q23) and the RFC 8693 auth server survey (Q11). Market questions have verifiably lower source authority.

**Question type yield (second-order analysis):**
| Type | Count | HIGH % | Avg Sources | Observation |
|------|-------|--------|-------------|-------------|
| security-threat | 5 | 100% | 4.2 | Highest reliability. Primary sources (OWASP, IETF) abundant. |
| standards-specs | 3 | 100% | 4.3 | High source density but diminishing marginal insight after Q4. |
| landscape-survey | 3 | 100% | 5.3 | Highest source density — many vendors to cite. But least actionable. |
| production-implementation | 7 | 86% | 3.9 | Most entries, slightly lower source density. But produced the most *connective* findings — entries that bridged standards, vendors, and architecture. |
| comparative-analysis | 2 | 100% | 3.5 | Lowest source density but highest information density per entry. Comparing forces synthesis. |
| market-enterprise | 2 | 50% | 4.0 | **Weakest type.** Only 50% HIGH confidence. Vendor marketing pollutes sources. |
| foundational-survey | 2 | 100% | 4.5 | Bootstrap-only value. No more needed. |

**What worked:**
- Security-threat questions had 100% HIGH confidence with 4.2 avg sources. Rich primary source ecosystem (OWASP, IETF security advisories, CVE databases).
- Production-implementation questions, despite being only 86% HIGH, produced the densest *connective* findings — entries like Q14 (chain integrity validation) and Q18 (MCP token propagation) bridged 3+ subtopics per entry.
- Comparative-analysis questions (Q16 gap analysis, Q20 interoperability) had the lowest source count but forced synthesis across domains, producing higher insight-per-source.

**What didn't:**
- Market-enterprise questions (Q23 pricing, Q25 RFPs) had 50% HIGH confidence — the worst of any type. Vendor marketing sites appear authoritative but contain unverifiable claims. The system had no mechanism to discount these sources.
- Landscape-survey questions (Q3 players, Q7 frameworks, Q19 detection vendors) had the highest source density (5.3) but lowest actionability. Listing vendors doesn't generate insight.
- The linear execution from seed questions created front-loaded breadth. Q1-Q8 mapped the terrain. Q9-Q26 followed gaps_identified without strategic prioritization. The system never decided to go deep on a productive thread vs. wide on an unproductive one.

**Strategy change for v1:**
1. **Deprioritize market-enterprise and landscape-survey questions.** These produce the weakest entries. Only pursue them when they directly connect to a production-implementation finding.
2. **Prioritize comparative-analysis.** Despite low source counts, these force cross-domain synthesis. Reframe future questions as "how does X compare to Y" rather than "what does X do."
3. **Introduce a connective-value heuristic.** Before starting a question, ask: "Will this entry bridge 2+ existing topics?" If not, defer it.
4. **Cap standards-spec deep-dives.** Diminishing returns after 3 entries per spec. Only go deeper if a production-implementation finding raises a specific spec question.
5. **Begin tracking search_count.** Essential for measuring research efficiency in v1 cohort.

**Hypothesis for next cohort:**
Under v1 strategy, the next 5 entries should show: (a) higher comparative-analysis representation (≥2 of 5), (b) maintained HIGH confidence ≥90%, (c) fewer landscape-survey entries (0-1 of 5), and (d) measurable search_count data for efficiency analysis.

### v1 → v2 Analysis (2026-03-09)

**program.md version:** v1 → v2

**Cohort metrics (5 entries under v1: Q27-Q31):**
| Metric | v0 (25 entries) | v1 (5 entries) | Delta |
|--------|-----------------|----------------|-------|
| Entries | 25 | 5 | — |
| HIGH confidence % | 92% | 100% | +8% |
| MEDIUM confidence % | 8% | 0% | -8% |
| LOW confidence % | 0% | 0% | — |
| Avg sources per entry | 4.2 | 5.6 | +1.4 |
| Avg searches per entry | unknown | 4.8 | (first measurement) |

**Question type breakdown (v1 cohort):**
| Type | Count | HIGH % | Avg Sources | Avg Searches |
|------|-------|--------|-------------|--------------|
| comparative-analysis | 2 | 100% | 6.0 | 5.0 |
| security-threat | 2 | 100% | 5.5 | 4.5 |
| production-implementation | 1 | 100% | 5.0 | 5.0 |

Note: meta_analyze.py classified Q28 (Cedar vs CA vs FGA authorization engines) and Q31 (revocation comparison) as security-threat due to their security-focused content, but both are structurally comparative. A more accurate classification: 4 comparative, 1 production-implementation. The type classifier should weight framing ("how does X compare to Y") over topic domain.

**v1 hypothesis evaluation:**
| Hypothesis | Result | Evidence |
|------------|--------|----------|
| ≥2 comparative-analysis entries | ✅ CONFIRMED | 2-4 of 5 depending on classification (Q27, Q28, Q31 are comparative; Q29 bridges specs to production) |
| HIGH confidence ≥90% | ✅ CONFIRMED | 100% HIGH (5/5) |
| 0-1 landscape-survey | ✅ CONFIRMED | 0 landscape-survey entries |
| Measurable search_count | ✅ CONFIRMED | All 5 entries have search_count (avg 4.8) |

All four hypotheses confirmed. The v1 strategy change was successful.

**What worked:**
- **Comparative framing dramatically increased source density.** v1 comparative entries averaged 6.0 sources vs 3.5 in v0 — a 71% increase. The v0 observation that comparisons had the "lowest source density" was wrong. Comparisons had low source density when they were ad-hoc; when they were the *primary strategy*, researchers invest more search effort per question, finding more authoritative sources.
- **Connective-value test eliminated low-value entries.** Every v1 entry bridged 4-5 existing topics. No entry extended only a single thread. This produced a denser report graph where new findings reinforced and contextualized earlier ones.
- **Search efficiency is measurable and reasonable.** 4.8 searches per HIGH-confidence answer. This becomes the baseline for v2 optimization.
- **100% HIGH confidence with zero MEDIUM.** Eliminating market-enterprise questions entirely removed the primary source of MEDIUM-confidence entries.

**What could improve:**
- **Question type classifier needs work.** The automated classifier relies on topic keywords, not question structure. "How does X compare to Y for security" gets classified as security-threat, not comparative-analysis. A better heuristic: if the question names 2+ entities and uses comparative framing, classify as comparative regardless of domain.
- **Diminishing comparative returns within a single sub-domain.** Q28 (authorization policy engines) and Q31 (revocation in delegation chains) both compare Cedar vs CA vs FGA. The marginal insight of the second comparison was lower than the first — the architectural difference was established in Q28, and Q31 extended it to revocation specifically. Future comparisons should span different entity sets, not re-compare the same entities on different dimensions.
- **Production-implementation is underrepresented.** Only 1 of 5 entries (Q30 on latency). The v0 analysis showed production-implementation had the highest connective value. The comparative-framing mandate may have pulled attention away from "how does this actually work in deployment" questions.
- **No new question types emerged.** v1 stayed within the type taxonomy from v0. Worth considering whether "architectural-pattern" or "failure-mode" types would yield better results than current categories.

**Strategy change for v2:**
1. **Maintain comparative priority but diversify comparison targets.** Don't re-compare the same 3 entities (Cedar, CA, FGA or AgentCore, XAA, Entra). Instead, compare across categories: e.g., MCP gateway architectures vs cloud-native approaches, or OSS vs vendor solutions for the same problem.
2. **Increase production-implementation representation.** Target 2 of 5 entries as production-implementation, framed comparatively when possible. Focus on how systems actually behave at scale, not just how they're designed.
3. **Introduce "failure-mode" question type.** Ask "what breaks when X happens?" rather than "how does X work?" Failure modes often reveal architectural truths that happy-path descriptions obscure. Example: "What happens when the enterprise IdP is down during MCP XAA flow?"
4. **Search efficiency target: ≤5 searches per HIGH-confidence answer.** v1 baseline is 4.8. Maintain or improve. If a question requires >6 searches, it may be too broad — split it.
5. **Connective-value test remains mandatory.** It's the strongest contributor to entry quality.
6. **Fix type classification.** Questions with 2+ named entities in comparative framing are comparative-analysis, regardless of domain topic.

**Hypothesis for next cohort:**
Under v2 strategy, the next 5 entries should show: (a) no repeated comparison sets (e.g., no more Cedar vs CA vs FGA), (b) ≥2 production-implementation entries, (c) ≥1 failure-mode entry, (d) maintained 100% HIGH confidence, (e) avg search_count ≤5.0.

### v2 → v3 Analysis (2026-03-09)

**program.md version:** v2 → v3

**Cohort metrics (5 entries under v2: Q32-Q36):**
| Metric | v0 (25 entries) | v1 (5 entries) | v2 (5 entries) | v1→v2 Delta |
|--------|-----------------|----------------|----------------|-------------|
| Entries | 25 | 5 | 5 | — |
| HIGH confidence % | 92% | 100% | 100% | 0% |
| MEDIUM confidence % | 8% | 0% | 0% | 0% |
| LOW confidence % | 0% | 0% | 0% | — |
| Avg sources per entry | 4.2 | 5.6 | 5.2 | -0.4 |
| Avg searches per entry | unknown | 4.8 | 5.0 | +0.2 |

Source density dropped slightly from 5.6 to 5.2 — still well above v0 baseline (4.2). Search efficiency at exactly 5.0 — at the upper bound of the v2 target. Every entry used exactly 5 searches except none exceeded the cap, indicating the 5-search heuristic was internalized but acting as a ceiling rather than a guide.

**Question type breakdown (v2 cohort):**
| Type | Count | HIGH % | Avg Sources | Avg Searches |
|------|-------|--------|-------------|--------------|
| failure-mode | 2 | 100% | 5.0 | 5.0 |
| production-implementation | 2 | 100% | 5.0 | 5.0 |
| comparative-analysis | 1 | 100% | 6.0 | 5.0 |

Classification notes: Q34 (gateway vs cloud-native) is structurally comparative but classified as production-implementation because its primary finding was operational tradeoffs, not architectural differences. Q35 (multi-cloud agent auth) is purely comparative with a fresh entity set (cloud providers). Q33 (CIMD/XAA adoption) is production-implementation focused on real-world SDK adoption status.

**v2 hypothesis evaluation:**
| Hypothesis | Result | Evidence |
|------------|--------|----------|
| No repeated comparison sets | ✅ CONFIRMED | Q35 compares cloud-provider federation patterns (AWS/Azure/GCP + SPIFFE) — entirely new entity set. No Cedar/CA/FGA re-comparisons. |
| ≥2 production-implementation entries | ✅ CONFIRMED | Q33 (CIMD/XAA adoption) and Q34 (gateway vs cloud-native operational tradeoffs) |
| ≥1 failure-mode entry | ✅ CONFIRMED | Q32 (IdP outage during XAA) and Q36 (stale cached permissions) — exceeded target with 2 |
| Maintained 100% HIGH confidence | ✅ CONFIRMED | 5/5 HIGH |
| Avg search_count ≤5.0 | ✅ CONFIRMED | Exactly 5.0 (at boundary) |

All five hypotheses confirmed. v2 strategy was successful.

**What worked:**
- **Failure-mode questions produced the highest-impact findings.** Q32 (IdP outage) revealed that NO XAA-specific resilience pattern exists — a critical architectural gap that happy-path documentation obscures. Q36 (stale permissions) connected token exchange latency (Q30), revocation tradeoffs (Q31), and CAE propagation windows into a unified failure analysis. Both entries generated 4 follow-on gaps each, the most of any type.
- **Entity set diversification maintained quality without repetition.** Q35 introduced SPIFFE, WIMSE, and cloud-provider IAM engines as new comparison targets. No diminishing returns observed because the entities and the comparison dimensions were both novel.
- **Production-implementation entries anchored findings in reality.** Q33 (CIMD adoption) revealed the gap between spec-level changes and SDK-level implementation — FastMCP shipped CIMD in 3 weeks, MCP Python SDK still hasn't. Q34 showed the convergence of gateway and platform architectures (AgentCore now supports MCP servers as targets). These "what's actually happening" entries ground the research in current state rather than aspirational design.
- **Connective-value test continues to be the strongest quality signal.** Every v2 entry bridged 4+ existing topics. Q36 connected Q30, Q31, Q32, and enterprise requirements into a single coherent failure analysis.

**What could improve:**
- **Search efficiency hit the ceiling.** Every entry used exactly 5 searches. The ≤5.0 target may be functioning as a constraint rather than a guide. Some questions (Q35 on multi-cloud) could have benefited from a 6th search for WIMSE working group specifics. The efficiency target should be relaxed slightly to allow 6 searches when the question genuinely requires it, with the split heuristic kicking in at >7.
- **Source density declined slightly.** 5.2 vs 5.6 in v1. This may be an artifact of the search ceiling — fewer searches = fewer unique sources. Alternatively, failure-mode questions naturally draw from fewer published sources (gaps in documentation are themselves the finding). Not concerning at current level but worth monitoring.
- **Report.md structure is becoming unwieldy.** 1200+ lines with subsections added chronologically rather than thematically. The "Current Approaches & Patterns" and "Security Models & Attack Surfaces" sections have outgrown their original scope. A structural reorganization pass would improve readability without changing content.
- **Gap identification is producing diminishing returns on some threads.** The "measured latency of X at scale" gaps appear frequently but rarely have published answers. The research may be approaching the frontier of publicly available information on agent-specific auth performance. Future questions should focus on newly emerging topics (WIMSE, graduated authorization, SPIFFE-MCP integration) rather than seeking measurements that don't exist yet.
- **No entry addressed the developer experience dimension.** All v2 entries focused on enterprise/security/architecture concerns. The DX gap (env vars → proper auth) identified in the framework landscape section hasn't been revisited since v0. Worth investigating how the new primitives (CIMD, SPIFFE, XAA) change the developer onboarding story.

**Strategy change for v3:**
1. **Relax search ceiling to ≤6.** v2 data shows 5.0 is achievable but constraining. Allow 6 searches per question. Split heuristic at >7 (up from >6).
2. **Maintain failure-mode as equal priority to comparative.** v2 demonstrated failure-mode questions produce the highest-impact findings (gap discovery, cross-topic synthesis). Promote to co-#1 priority alongside comparative.
3. **Introduce "developer-experience" question type.** Target ≥1 per cohort. How do the new primitives (CIMD, SPIFFE, XAA, graduated authorization) change the developer journey from env vars to production auth? This thread has been neglected since v0.
4. **Prioritize newly emerging topics.** Several v2 gaps point to topics with nascent but growing documentation: IETF WIMSE, graduated/continuous authorization, SPIFFE-MCP integration, and lifecycle-aware credentials. These are likely to yield novel findings vs rehashing established topics.
5. **Flag "measurement frontier" gaps.** When a gap asks for "measured latency/performance of X" and 2+ entries have failed to find published data, mark it as "measurement-frontier" in gaps_identified and deprioritize. The information may simply not exist publicly yet.
6. **Consider a report.md reorganization pass.** Not a research question but a maintenance task. The report has grown organically and would benefit from thematic restructuring.

**Hypothesis for next cohort:**
Under v3 strategy, the next 5 entries should show: (a) ≥1 developer-experience entry, (b) ≥1 entry on a newly emerging topic (WIMSE, graduated auth, SPIFFE-MCP), (c) maintained 100% HIGH confidence, (d) avg search_count between 4.5 and 5.5 (relaxed ceiling), (e) at least one entry should cite a source published in 2026 Q1 (testing freshness of emerging topics).

### v3 → v4 Analysis (2026-03-09)

**program.md version:** v3 → v4

**Cohort metrics (5 entries under v3: Q37-Q41):**
| Metric | v0 (25 entries) | v1 (5 entries) | v2 (5 entries) | v3 (5 entries) | v2→v3 Delta |
|--------|-----------------|----------------|----------------|----------------|-------------|
| Entries | 25 | 5 | 5 | 5 | — |
| HIGH confidence % | 92% | 100% | 100% | 100% | 0% |
| MEDIUM confidence % | 8% | 0% | 0% | 0% | 0% |
| LOW confidence % | 0% | 0% | 0% | 0% | — |
| Avg sources per entry | 4.2 | 5.6 | 5.2 | 6.0 | +0.8 |
| Avg searches per entry | unknown | 4.8 | 5.0 | 6.0 | +1.0 |

Source density jumped from 5.2 to 6.0 — the highest of any cohort. Search efficiency at exactly 6.0 — every entry used the maximum allowed. The relaxed ceiling (≤6, up from ≤5) was fully consumed, suggesting the questions genuinely required the additional search or the ceiling acts as a target rather than a limit.

**Question type breakdown (v3 cohort):**
| Type | Count | HIGH % | Avg Sources | Avg Searches |
|------|-------|--------|-------------|--------------|
| failure-mode | 2 | 100% | 6.0 | 6.0 |
| comparative-analysis | 2 | 100% | 6.0 | 6.0 |
| developer-experience | 1 | 100% | 6.0 | 6.0 |

Classification notes: Q38 (WIMSE vs SPIFFE vs OAuth JWT) is purely comparative with a fresh three-way entity set. Q40 (Token Vault vs AgentCore vs Aembit) is comparative with production grounding — classified as comparative because the primary finding is architectural pattern differences, though it draws heavily on production documentation. Q39 (graduated auth failure modes) and Q41 (SPIRE federation failures) are failure-mode, each revealing architectural gaps that happy-path documentation obscures.

**v3 hypothesis evaluation:**
| Hypothesis | Result | Evidence |
|------------|--------|----------|
| ≥1 developer-experience entry | ✅ CONFIRMED | Q37 (CIMD/SPIFFE DX vs env-var baseline) — first DX entry since v0 |
| ≥1 emerging topic entry | ✅ CONFIRMED | Q38 (WIMSE), Q39 (graduated auth), Q41 (SPIFFE federation) — 3 of 5 entries on emerging topics |
| Maintained 100% HIGH confidence | ✅ CONFIRMED | 5/5 HIGH |
| Avg search_count 4.5-5.5 | ❌ EXCEEDED | 6.0 — every entry used the full ≤6 allowance |
| ≥1 source from 2026 Q1 | ✅ CONFIRMED | Q40 cites Delinea/StrongDM acquisition (March 5, 2026), Q39 cites Sondera (2026) |

Four of five hypotheses confirmed. The search count exceeded the predicted range — not because questions were too broad (none required splitting) but because the ≤6 ceiling again functioned as a target. This is a consistent pattern across v2 (5.0 against ≤5 ceiling) and v3 (6.0 against ≤6 ceiling).

**What worked:**

- **Developer-experience entry filled a critical gap.** Q37 identified the three-tier complexity landscape (env-var → OAuth/CIMD → SPIFFE) and the absence of any managed service bridging CIMD to per-agent identity. This connected the spec-level findings (Q29, Q33) to the developer reality and produced the report's first actionable onboarding analysis.

- **Emerging topics yielded the highest novelty per entry.** Q38 (WIMSE) documented the WIT proof-of-possession mechanism and its convergence with SPIFFE — information not present in any previous entry and not widely synthesized elsewhere. Q39 (graduated auth) identified three failure modes (response ambiguity, HITL bottleneck, policy complexity explosion) that are entirely absent from vendor documentation. Q41 (SPIFFE federation) surfaced five production failure modes including the Indeed OIDC JWKS key proliferation finding.

- **Source density improved.** 6.0 avg sources (up from 5.2) — the relaxed search ceiling allowed more thorough source triangulation. Every entry drew from 6 independent sources, up from the v2 pattern of 5.

- **Failure-mode questions continue to be the highest-impact type.** Q39 and Q41 both revealed architectural gaps that no vendor documentation addresses. Q39's graduated-response-ambiguity finding (agent frameworks have no protocol for partial authorization) is arguably the most actionable finding since Q32 (IdP outage gap).

- **Comparative questions with 3+ entities produced richer findings than 2-entity comparisons.** Q38 (WIMSE vs SPIFFE vs OAuth JWT) and Q40 (Token Vault vs AgentCore vs Aembit) both had three-way structures that forced the analysis to identify where each approach falls short relative to the others, rather than just "X is better than Y."

**What could improve:**

- **Search ceiling is still functioning as a target.** The system used exactly 6 searches for every entry. This means either (a) every question genuinely required 6 searches, or (b) the system filled the budget regardless. Given that v2 used exactly 5/5 and v3 used exactly 6/6, pattern (b) is more likely. Options: remove the ceiling entirely (trust the split heuristic for overly broad questions) or keep it but stop measuring it as an efficiency metric since it's not actually variable.

- **Report.md is now 1700+ lines.** The reorganization pass recommended in v2 analysis has not happened. Subsections are added chronologically before "## Open Problems & Gaps" without thematic grouping. A reader would have difficulty navigating from the executive summary to a specific topic. This is now urgent — the report has doubled since the recommendation was first made.

- **Measurement-frontier gaps are accumulating.** Q39, Q40, and Q41 all produced gaps asking for "measured latency/throughput of X under agent-scale load." This is the same pattern flagged in v2 — the data doesn't exist publicly. These should be explicitly tagged and deprioritized per v3 strategy, but the tagging isn't happening in practice.

- **No entry addressed regulatory/compliance implications in depth.** Q40 surfaced the EU AI Act Article 14 deadline (August 2026) in passing, but no entry has systematically analyzed how credential delegation patterns interact with compliance requirements (SOC 2, ISO 42001, EU AI Act, NIST AI Agent Standards). This is a significant coverage gap given that compliance often drives enterprise adoption decisions.

- **Question generation is converging.** All v3 entries naturally clustered around SPIFFE, WIMSE, graduated auth, and lifecycle management — the emerging topics prioritized in the strategy. This produced excellent depth but at the cost of breadth. Topics that remain thin in the report: delegation chain patterns beyond OAuth token exchange, agent-to-agent authentication (no entry addresses multi-agent orchestration auth), and the consumer/non-enterprise use case.

**Strategy change for v4:**
1. **Remove the search ceiling.** Replace ≤6 with the split heuristic only: if a question requires >8 searches, it's too broad. Otherwise, use as many searches as the question needs. Stop tracking search_count as a quality metric — it's a budget, not a signal.
2. **Introduce "regulatory-compliance" question type.** Target ≥1 per cohort. How do credential delegation patterns interact with EU AI Act, SOC 2, ISO 42001, and NIST AI agent standards? This is the biggest coverage gap.
3. **Broaden topic coverage.** At least 2 of 5 entries should address topics NOT on the v3 emerging topic list. Candidates: agent-to-agent authentication in multi-agent orchestration, delegation chain patterns beyond OAuth (e.g., CAEP/SSF event streams), non-enterprise consumer agent auth patterns, or hardware-backed agent identity (TPM, TEE).
4. **Tag measurement-frontier gaps explicitly.** Any gap asking for "measured X under agent-scale load" where 2+ prior entries failed to find data gets tagged `[measurement-frontier]` in gaps_identified. Do not select these as primary questions.
5. **Maintain failure-mode and comparative as co-#1.** Both continue to produce the highest-impact findings.
6. **Three-way comparisons preferred over two-way.** v3 data shows three-entity comparisons produce richer findings. When formulating comparative questions, include 3+ named entities when possible.
7. **Report reorganization is overdue.** This should happen before v4 research begins, but it's a maintenance task, not a research question. Consider doing a single pass to group subsections thematically rather than chronologically.

**Hypothesis for next cohort:**
Under v4 strategy, the next 5 entries should show: (a) ≥1 regulatory-compliance entry, (b) ≥2 entries on topics NOT from the v3 emerging topic list, (c) maintained 100% HIGH confidence, (d) at least one three-way comparative with a fresh entity set, (e) no gaps_identified containing measurement-frontier patterns selected as primary questions.
