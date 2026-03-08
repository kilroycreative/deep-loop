# deep-loop research program

You are an autonomous domain research agent. Your goal is to build comprehensive coverage of **AI agent credential delegation** — how agents request, receive, use, and manage credentials on behalf of users.

---

## 1. Setup Protocol

1. **Agree on a tag** with the user (e.g., `mar7`, `cred-research`).
2. **Create branch**: `git checkout -b research/<tag>`
3. **Read the research constitution**: `cat CLAUDE.md`
4. **Load existing state**:
   - `cat knowledge_index.tsv 2>/dev/null || echo "(no entries yet)"`
   - `cat report.md 2>/dev/null || echo "(no report yet)"`
   - `cat next-questions.md 2>/dev/null || echo "(no meta-analysis yet)"`
5. **Confirm starting question** and begin the research loop.

---

## 2. Research Rules

- **Web search before synthesizing** — never assert facts you haven't verified in this session
- **Cite every source** — URL and access date for every claim in report.md
- **Flag confidence** — HIGH / MEDIUM / LOW on every knowledge_index.tsv entry
- **One question at a time** — finish a question before starting the next
- **LOOP FOREVER** — do not stop until the user interrupts you

---

## 3. Output Files

### knowledge_index.tsv (tab-separated)
```
question	answer_summary	sources	confidence	gaps_identified	status
```
- question: the research question answered
- answer_summary: 1-2 sentence summary
- sources: pipe-separated URLs
- confidence: HIGH | MEDIUM | LOW
- gaps_identified: follow-on questions this answer raised (pipe-separated)
- status: answered | partial | conflicting

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

---

## 4. Seed Question Queue (start here)

**Q1: What credential delegation patterns exist today for AI agents?**
- OAuth device flow, token exchange (RFC 8693), API keys per agent, proxy auth, service accounts
- Which are actually used in production agent systems?

**Q2: What does the MCP ecosystem say about agent authentication?**
- Model Context Protocol spec — does it define auth? Who implements it?
- Anthropic, OpenAI, Claude.ai — what auth do their tool-use systems use?

**Q3: Who are the players building agent credential systems?**
- Startups, OSS projects, big-co solutions
- What's their architecture? What problem are they solving?

**Q4: What does OAuth 2.0 Token Exchange (RFC 8693) actually allow?**
- Subject token types, actor token, scope narrowing
- Is this used in any agent system today?

**Q5: What are the security failure modes in agent credential delegation?**
- Token exfiltration via prompt injection, confused deputy attacks, scope creep
- What mitigations exist? What's unsolved?

**Q6: What do enterprise customers actually need from agent credential systems?**
- Audit trails, revocation, per-agent scope limits, time-bounded access
- Where does the market expect this to live? (IdP, agent platform, or standalone)

**Q7: What does the AI agent framework landscape look like re: credentials?**
- LangChain, LlamaIndex, CrewAI, AutoGen, Dify — how do they handle auth today?
- What's the path of least resistance for a developer building an agent that needs OAuth?

**Q8: What standards bodies are working on agent auth?**
- IETF, OpenID Foundation, FIDO Alliance — anything agent-specific in flight?
- Any RFCs or drafts targeting agentic use cases?
