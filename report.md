# AI Agent Credential Delegation — Research Report

## Executive Summary

**AI agent credential delegation is an emerging but fragmented field with no ratified standard yet.** The industry is converging on OAuth 2.1 + MCP as the de facto baseline, but significant gaps remain in security, interoperability, and enterprise readiness.

### Key Findings

**1. Patterns Emerging**
- **OAuth On-Behalf-Of (OBO) delegation** with nested identity claims is the dominant pattern for user-delegated actions
- **RFC 8693 Token Exchange** enables scope narrowing and delegation chains, but lacks front-channel user consent
- **SPIFFE/SPIRE** for workload identity and **short-lived dynamic secrets** (HashiCorp Vault) address machine-to-machine auth
- **Gateway-based credential management** centralizes enforcement but creates single points of failure

**2. Market Players**
- **Enterprise IdPs** (Microsoft Entra Agent ID, Okta, Auth0) are adding agent identity to existing fabrics
- **Startups** (Descope, Scalekit, Aembit) offer purpose-built solutions with MCP integration
- **Open source** (Nango, Arcade.dev) fills integration gaps but with limited auth sophistication

**3. MCP Authentication**
- MCP mandates OAuth 2.1 with PKCE for remote servers
- Dynamic Client Registration (DCR) solves the M×N client/server problem
- **Critical gap:** MCP defines client-to-server auth but NOT downstream propagation — each server must implement token exchange independently

**4. Security Challenges**
- **Prompt injection → credential exfiltration** is OWASP #1 (2025), affecting 73% of deployments
- **Long-lived tokens** remain prevalent; major breaches (Drift, $2.3M wire fraud) demonstrate risk
- No standard mechanism prevents prompt injection from triggering credential abuse

**5. Enterprise Requirements**
- SSO/IdP integration, task-scoped credentials (5-15 min TTL), immutable audit trails
- Kill switch capability, non-custodial architecture
- Token refresh for long-running tasks remains unsolved

**6. Standards Activity**
- **NIST AI Agent Standards Initiative** (concept paper, comments open April 2026)
- **IETF drafts** for agent auth (draft-klrc-aiagent-auth) and OBO consent (draft-oauth-ai-agents-obo)
- **OIDC-A 1.0 proposal** adds agent-specific claims and attestation endpoints
- **No ratified standard yet** — timeline unclear

**7. Framework Landscape**
- Most OSS frameworks (LangGraph, LlamaIndex, CrewAI) rely on environment variables
- AWS Bedrock AgentCore Identity is enterprise-ready with full OAuth 2.0 and audit trails
- Third-party solutions (Arcade, Nango, Auth0) fill the credential brokering gap

### Implications
The market is ready for a purpose-built solution that:
1. Bridges MCP's downstream authorization gap with standardized token exchange
2. Provides enterprise-grade audit trails without requiring custom implementation
3. Offers kill switch and revocation that works across multi-agent delegation chains
4. Addresses the developer experience gap between "env vars" and "enterprise auth"

## The Problem Space

AI agents increasingly need to access external services (APIs, databases, SaaS tools) on behalf of users. The core challenge: **how does an agent prove it has authority to act for a specific user, with appropriate scope limits, in a way that's auditable and revocable?**

Traditional approaches fail in several ways:
- **API keys** authenticate the service, not the user — systems see "trusted service account with broad permissions" rather than the context of individual user requests ([Christian Posta](https://blog.christianposta.com/api-keys-are-a-bad-idea-for-enterprise-llm-agent-and-mcp-access/))
- **Static credentials** are "toxic data" — they persist indefinitely, proliferate through configs and CI pipelines, and agents "will eventually find a reason to use them" even when inappropriate ([Christian Posta](https://blog.christianposta.com/api-keys-are-a-bad-idea-for-enterprise-llm-agent-and-mcp-access/))
- **No context awareness** — target systems cannot determine which employee made a request, whether they should access specific information, or the intent behind queries

The probabilistic, autonomous behavior of AI systems amplifies these risks. An HR chatbot with broad API keys could access salary data across departments or retrieve confidential reorganization plans — capabilities the key permits but the user shouldn't be able to request.

## Current Approaches & Patterns

### Pattern 1: On-Behalf-Of (OBO) Token Delegation

The dominant emerging pattern uses OAuth 2.0 with nested identity claims. Agents authenticate with their own credentials but present a "subject token" representing the human user. The resulting access token cryptographically encodes both identities ([Scalekit](https://www.scalekit.com/blog/delegated-agent-access)).

Token structure example:
```json
{
  "sub": "agent:infrabot",
  "act": {
    "sub": "user:sam",
    "scope": ["monitoring:read", "deploy:comment"]
  }
}
```

Benefits:
- **Attribution clarity**: Every action logs both `performed_by` (agent) and `on_behalf_of` (user)
- **Scope enforcement**: Agents receive only permissions the user actually possesses
- **Revocation**: Short-lived tokens (5-15 minutes) combined with revocation registries enable real-time permission invalidation

### Pattern 2: OAuth 2.0 Token Exchange (RFC 8693)

RFC 8693 defines two modes ([DEV Community](https://dev.to/kanywst/rfc-8693-deep-dive-token-exchange-310i)):

- **Impersonation**: Client presents only a subject_token; new token represents the original user but scoped for a new audience
- **Delegation**: Client presents both subject_token and actor_token; new "composite" token represents the actor acting on behalf of the subject

Limitation: RFC 8693 is designed for server-side communication and lacks native support for obtaining explicit user consent via front channel. This led to the IETF draft extension (see Standards section).

### Pattern 3: Gateway-Based Credential Management

An AI Gateway acts as centralized enforcement layer between applications and model providers ([TrueFoundry](https://www.truefoundry.com/blog/llm-access-control)):
- Provider credentials stored securely within the gateway, not distributed across application code
- Access control evaluated at runtime before requests reach models
- Single point for authentication, authorization, and audit logging

### Pattern 4: SPIFFE/SPIRE for Workload Identity

SPIFFE (Secure Production Identity Framework For Everyone) assigns each service a cryptographic identity without relying on long-lived secrets ([HashiCorp](https://www.hashicorp.com/en/blog/spiffe-securing-the-identity-of-agentic-ai-and-non-human-actors)):
- Automated issuance of short-lived identity documents (SVIDs — certificates or JWTs)
- Automatic rotation and revocation
- Eliminates need for static secrets in runtime

SPIFFE can serve as first-class authentication for OAuth clients, including MCP clients ([Christian Posta](https://blog.christianposta.com/authenticating-mcp-oauth-clients-with-spiffe/)).

### Pattern 5: Short-Lived Dynamic Secrets

HashiCorp Vault and similar systems issue ephemeral, just-in-time credentials with automatic expiration ([HashiCorp Developer](https://developer.hashicorp.com/validated-patterns/vault/ai-agent-identity-with-hashicorp-vault)). This aligns with zero-trust principles: continuous verification and contextual access control.

### Authentication Method Hierarchy

Industry consensus emerging ([WorkOS](https://workos.com/blog/best-oauth-oidc-providers-for-authenticating-ai-agents-2025), [Riptides](https://riptides.io/blog-post/spiffe-meets-oauth2-current-landscape-for-secure-workload-identity-in-the-agentic-ai-era)):

| Context | Recommended Approach |
|---------|---------------------|
| Trusted backend / single cloud | Service accounts, workload identities, mTLS (no static secrets) |
| Cross-organization & SaaS | OAuth 2.1/OIDC with short-lived tokens |
| Agent-to-agent within org | SPIFFE + mTLS |
| User-delegated actions | OAuth OBO flow with explicit consent |

## Key Players & Projects

### Enterprise Identity Providers

**Microsoft Entra Agent ID** (Preview, 2025)
Microsoft's flagship solution for AI agent identity management, announced at Ignite 2025. Key features ([Microsoft Learn](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-id), [Microsoft Security](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-agent-id)):
- Agent identities as first-class citizens in Entra ID
- **No passwords or secrets** — agents authenticate only via access tokens issued to their runtime platform
- Conditional Access extends Zero Trust principles to agents
- Identity Governance enables lifecycle management at scale
- Identity Protection detects anomalous agent activities

**Protocol Details** ([Microsoft Learn — Agent OAuth Protocols](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-oauth-protocols)):
- Multi-stage token exchanges using Federated Identity Credentials (FIC)
- Agent identity blueprint impersonates agent identity to perform operations
- Supported grants: `client_credentials`, `jwt-bearer` (OBO), `refresh_token`
- All agents operate as **confidential clients** — no public client flows
- Managed identities are preferred credential type (automatic rotation)

Requires Microsoft 365 Copilot license and Frontier program enrollment.

**Okta for AI Agents** (2025)
Okta announced comprehensive AI agent security capabilities ([Okta](https://www.okta.com/solutions/secure-ai/), [SiliconANGLE](https://siliconangle.com/2025/09/25/okta-expands-identity-fabric-ai-agent-lifecycle-security-cross-app-access-verifiable-credentials/)):
- Discovery, provisioning, authorization, and governance of non-human identities
- Identity Security Posture Management for identifying risky agents and exposed credentials
- **Cross App Access (XAA)** protocol: enables agents to securely access multiple downstream services on behalf of users

**Delegation Chain Security** ([Okta Blog](https://www.okta.com/blog/ai/agent-security-delegation-chain/)):
- XAA tracks and revokes delegation lineage — agent actions are logged and revocable
- **Fine-Grained Authorization (FGA)** based on Google's Zanzibar enforces relationship-based access at every call
- Scope attenuation at every delegation hop (progressive narrowing)
- **Token Vault** requires cryptographic proof of user sessions, not plain identifiers
- **Asynchronous Authorization**: out-of-band approval via push/email for sensitive operations (channels agents cannot manipulate)

**Auth0 for GenAI** (Developer Preview)
Part of Auth0 Platform, focused on developer experience ([Auth0](https://auth0.com/ai), [Okta Newsroom](https://www.okta.com/newsroom/press-releases/auth0-platform-innovation/)):
- **Token Vault**: Securely stores user access tokens for AI agent workflows
- Pre-built integrations with Vercel AI SDK and LangGraph
- MCP Server for tenant configuration via natural language
- Built-in authentication, fine-grained authorization, async workflows

Limited to OAuth APIs (no API key support), smallest API coverage among competitors.

### Startups — Agentic Identity Specialists

**Descope — Agentic Identity Hub** (April 2025)
$53M Series A (Feb 2023). Announced industry-first platform for AI agent authentication ([Descope](https://www.descope.com/press-release/agentic-identity-hub), [SiliconANGLE](https://siliconangle.com/2025/04/22/descope-launches-agentic-identity-hub-simplify-authentication-ai-agents-workflows/)):
- **Inbound Apps**: Make applications OAuth-compatible identity providers
- **Outbound Apps**: 50+ pre-built integrations (Gmail, HubSpot, GitHub, Slack, Notion, Shopify)
- **MCP Auth SDKs**: Secure remote MCP servers with OAuth-based authorization

**Pricing:** Free (7,500 MAU), Pro ($0.05-0.10/user/mo), Growth ($799/mo ~25k MAU), Enterprise custom

**Scalekit**
Auth stack for AI apps ([Scalekit](https://www.scalekit.com)):
- Drop-in OAuth 2.1 for MCP developers
- Token vault layer for secure tool-calling
- On-Behalf-Of delegation support with nested identity claims

**Aembit**
IAM for agentic AI and workloads ([Aembit](https://aembit.io/)):
- Secretless access through infrastructure-asserted identity
- Real-time policy enforcement
- Independent identity broker across clouds, SaaS, and on-premise
- Secretless access cuts 85% of credential issuance/rotation/auditing work

**Pricing:** Starter free, Enterprise custom ($25M Series A, Sep 2024)

### API Integration Platforms

**Nango** (Open Source)
Powers integrations for "hundreds of fast growing AI agent companies" ([Nango](https://nango.dev/blog/best-ai-agent-authentication)):
- 700+ APIs across 30 categories
- Automatic credential refresh with webhook notifications
- Fully white-label authentication flows
- Community-driven API additions (~12 APIs added monthly)

**Pricing:** Open source, self-hostable, no vendor lock-in

**Arcade.dev**
Built explicitly for LLM agents and multi-agent systems:
- Open-source and self-hostable
- Credential brokering and fine-grained permissioning
- Supports both API key and OAuth authentication

### Token Vault / Credential Broker Solutions

**Agent-Vault** (Open Source)
Prevents secrets from flowing through LLM provider servers ([GitHub](https://github.com/botiverse/agent-vault)):
- Secret-aware file I/O layer
- Agents see placeholders like `<agent-vault:api-key>`, never real values

**HashiCorp Vault**
Enterprise-grade dynamic secrets for AI agents ([HashiCorp Developer](https://developer.hashicorp.com/validated-patterns/vault/ai-agent-identity-with-hashicorp-vault)):
- SPIFFE integration for workload identity
- Automatic credential rotation
- Just-in-time secret issuance

### MCP Gateway / Infrastructure

**MintMCP Gateway**
Production-ready MCP infrastructure ([Integrate.io](https://www.integrate.io/blog/best-mcp-gateways-and-ai-agent-security-tools/)):
- SOC 2 Type II compliance
- One-click deployment with OAuth protection
- Comprehensive audit trails

## Standards & Protocols

### Model Context Protocol (MCP) Authentication

MCP, Anthropic's open standard for connecting AI assistants to external tools, has adopted OAuth 2.1 as its authentication framework. The specification establishes a standardized authorization flow for remote MCP servers ([MCP Spec](https://modelcontextprotocol.io/specification/2025-11-25), [MCP Auth Tutorial](https://modelcontextprotocol.io/docs/tutorials/security/authorization)).

**MCP Authentication Architecture:**

1. **Transport-dependent auth**: Local servers (stdio transport) use environment variables or embedded credentials. Remote servers (Streamable HTTP) require OAuth 2.1 with mandatory PKCE ([Stack Overflow Blog](https://stackoverflow.blog/2026/01/21/is-that-allowed-authentication-and-authorization-in-model-context-protocol/))

2. **Protected Resource Metadata (PRM)**: When a client makes an unauthenticated request, the server returns 401 with a `WWW-Authenticate` header pointing to a JSON document containing authorization server info and supported scopes ([MCP Auth Tutorial](https://modelcontextprotocol.io/docs/tutorials/security/authorization))

3. **Dynamic Client Registration (DCR)**: MCP clients can register themselves programmatically with authorization servers at runtime, solving the M×N problem of pre-registering every client/server combination ([Stytch](https://stytch.com/blog/mcp-oauth-dynamic-client-registration/))

4. **Client ID Metadata Documents**: URL-based client registration where clients provide a URL pointing to a self-managed JSON document describing client properties — still in draft but addresses DCR security concerns ([MCP Blog](http://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/))

**Critical Gap — Downstream Authorization:**

> "The exact mechanism for authentication and authorization for requests made by an MCP server is outside the scope of the MCP specification."
> — [Stack Overflow Blog](https://stackoverflow.blog/2026/01/21/is-that-allowed-authentication-and-authorization-in-model-context-protocol/)

MCP defines how clients authenticate *to* MCP servers, but not how those servers propagate user identity *downstream* to the services they call.

**Production Solutions for Downstream Propagation:**

Several production implementations have emerged to solve this gap:

**Three-Layer Authentication Stack** ([Ultrathink](https://ultrathinksolutions.com/the-signal/mcp-gateway-authentication/), [Red Hat](https://developers.redhat.com/articles/2025/12/12/advanced-authentication-authorization-mcp-gateway)):

1. **OIDC Authentication**: Validates JWT, extracts user identity (subject, email, roles)
2. **Authorization (SpiceDB/Kuadrant)**: Relationship-based access checks — `mcp_tool:<name>#invoke@user:<subject>`
3. **RFC 8693 Token Exchange**: Swaps gateway-scoped JWT for platform-specific token

**Identity Propagation Headers:**

| Header | Purpose |
|--------|---------|
| `X-User-Subject` | Unique identifier from OIDC `sub` claim |
| `X-User-Email` | Maps to platform LOGIN_NAME |
| `X-User-Roles` | Comma-separated role list |
| `X-User-Token` | Platform-scoped OAuth token |

**RFC 8693 Implementation with Okta:**

Critical requirement: Token exchange needs **two distinct Okta applications**:
- **Web Application** (subject client): User-facing identity with Authorization Code grant
- **API Services App** (actor client): Machine identity with explicit Token Exchange grant

Okta rejects exchanges where both parties are Web Applications — the actor must be API Services type.

**HashiCorp Vault Integration:**

For services not supporting OAuth2:
- Gateway queries Vault at paths like `/v1/secret/data/alice/github.mcp.local`
- Retrieves PATs or API keys per user per service
- Credentials never exposed in code or config

**Dual-Mode Identity (Graceful Degradation):**
- If `X-User-Token` header present: connect as user via OAuth
- If absent: fall back to configured service account
- Same server operates across authenticated requests, batch jobs, and local development

**Enterprise Extensions (2025):**

- SEP-1046: OAuth client credentials support for machine-to-machine authorization
- SEP-990: Enterprise IdP policy controls enabling single sign-in across multiple MCP servers ([MCP Blog](http://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/))

### IETF OAuth Extension for AI Agents

A new Internet Draft extends OAuth 2.0 specifically for AI agent delegation: `draft-oauth-ai-agents-on-behalf-of-user-01` ([IETF](https://www.ietf.org/archive/id/draft-oauth-ai-agents-on-behalf-of-user-01.html)).

**New Parameters:**

1. **`requested_actor`** (authorization endpoint): Identifies which agent requires delegation
2. **`actor_token`** (token endpoint): Authenticates the agent during code exchange

**Flow:**
1. Agent signals intent to client application
2. Client redirects user to authorization server with `requested_actor` parameter
3. User authenticates and grants consent for that specific agent
4. Authorization server issues code
5. Client exchanges code + `actor_token` for access token with `act` claim documenting delegation chain

**Authors:** Thilina Shashimal Senarath and Ayesha Dissanayaka (WSO2), May 2025

### OAuth 2.0 Token Exchange (RFC 8693) — Deep Dive

RFC 8693 defines a protocol for exchanging one token for another, enabling secure delegation across service boundaries. It's the foundation for AI agent credential propagation ([RFC 8693](https://datatracker.ietf.org/doc/html/rfc8693), [Authlete](https://www.authlete.com/developers/token_exchange/)).

**Request Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `grant_type` | Yes | `urn:ietf:params:oauth:grant-type:token-exchange` |
| `subject_token` | Yes | The token representing the identity on whose behalf the request is made |
| `subject_token_type` | Yes | URN identifying the token format |
| `actor_token` | No | Token representing the acting party (for delegation) |
| `actor_token_type` | No | Required when `actor_token` present |
| `scope` | No | Desired scope for the new token (enables scope narrowing) |
| `resource` | No | Target resource URI |
| `audience` | No | Target service identifier |

**Standardized Token Types:**

- `urn:ietf:params:oauth:token-type:jwt`
- `urn:ietf:params:oauth:token-type:access_token`
- `urn:ietf:params:oauth:token-type:refresh_token`
- `urn:ietf:params:oauth:token-type:id_token`
- `urn:ietf:params:oauth:token-type:saml1`
- `urn:ietf:params:oauth:token-type:saml2`

**Impersonation vs. Delegation:**

| Mode | Tokens Provided | Result | Use Case |
|------|-----------------|--------|----------|
| Impersonation | `subject_token` only | New token represents original user | Agent acts as user; no actor identity preserved |
| Delegation | `subject_token` + `actor_token` | Composite token with `act` claim | Full audit trail; both identities preserved |

**The `act` Claim — Delegation Chain:**

Delegation mode embeds an `act` claim in the issued JWT containing the actor's identity ([ZITADEL](https://zitadel.com/docs/guides/integrate/token-exchange)):

```json
{
  "sub": "user:259241944654282754",
  "iss": "https://auth.example.com",
  "act": {
    "iss": "https://auth.example.com",
    "sub": "agent:infrabot"
  }
}
```

This creates an audit trail: "agent infrabot is acting on behalf of user 259241944654282754." The `act` claim persists through token refreshes, maintaining accountability.

**Nested `act` Claims for Multi-Hop Delegation:**

When Agent A delegates to Agent B which calls Service C, RFC 8693 supports recursive nesting of `act` claims ([RFC 8693](https://datatracker.ietf.org/doc/html/rfc8693)):

```json
{
  "sub": "user:alice",
  "act": {
    "sub": "agent:coordinator",
    "act": {
      "sub": "agent:worker-3"
    }
  }
}
```

The outermost `act` represents the current actor; the most deeply nested is the least recent in the chain. Keycloak 26.2+ preserves nested `act` claims through token refreshes ([Keycloak](https://www.keycloak.org/2025/05/standard-token-exchange-kc-26-2)).

**Limitation:** No auth server natively validates multi-hop chain permissions — resource servers must implement their own logic to verify each link in the chain has appropriate authority.

**Agentic JWT (A-JWT) Extension:**

Research from Stanford introduces a dedicated protocol for delegation chains in AI agent systems ([arXiv](https://arxiv.org/html/2509.13597v1)):

New claims:
- `delegation_chain`: Ordered array of `{delegated_by, delegated_at, purpose, permissions}` objects
- `initiated_by`: Original human user who started the task
- `executed_by`: Agent actually performing the action

The key innovation is **cryptographic binding of intent**: signatures link agent actions back to verifiable user authorization, preventing agents from claiming broader authority than actually delegated.

**Scope Narrowing:**

A key capability for least-privilege: a resource server can exchange a broad access token for one narrowly scoped for a downstream service. "The new token might be an access token that is more narrowly scoped for the downstream service or it could be an entirely different kind of token" ([RFC 8693](https://datatracker.ietf.org/doc/html/rfc8693)).

**AI Agent Use Cases:**

- **Slack summarization agent**: Uses delegated user access to read channels
- **Compliance scanner**: Uses service credentials with narrow scope
- **Workflow orchestrator**: Exchanges tokens when invoking downstream APIs
- **Auth0 Token Vault pattern**: Performs RFC 8693-style exchange to obtain fresh provider access tokens without storing refresh tokens in client applications ([Auth0](https://auth0.com/blog/auth0-token-vault-secure-token-exchange-for-ai-agents/))

**Limitation:** RFC 8693 is server-side only — no native support for obtaining explicit user consent via front channel. This is why the IETF draft extension (see above) was created.

### Authenticated Delegation Framework (Academic)

A research framework from MIT/Harvard extends OAuth 2.0 and OpenID Connect with three token types ([arXiv](https://arxiv.org/html/2501.09674v1)):

1. **User's ID-token**: Human delegator identity from OpenID Provider
2. **Agent-ID token**: Agent metadata including unique identifiers and capability limits
3. **Delegation Token**: Authorizes agent to act on user's behalf, referencing both other tokens with scope limitations

**Authors:** Tobin South, Samuele Marro, Thomas Hardjono, Robert Mahari, et al.

### Standards Bodies Working on Agent Auth

#### NIST AI Agent Standards Initiative

NIST's Center for AI Standards and Innovation (CAISI) launched the AI Agent Standards Initiative in February 2026 ([NIST](https://www.nist.gov/caisi/ai-agent-standards-initiative), [NCCoE](https://www.nccoe.nist.gov/projects/software-and-ai-agent-identity-and-authorization)).

**Concept Paper: "Accelerating the Adoption of Software and AI Agent Identity and Authorization"**
- Comment period through April 2, 2026
- Focus: How agents are authenticated, how permissions are scoped, how activity is logged and audited

**Standards under consideration:**
- Model Context Protocol (MCP)
- OAuth 2.0/2.1 and extensions
- OpenID Connect
- SPIFFE/SPIRE
- SCIM (System for Cross-domain Identity Management)
- NGAC (Next Generation Access Control)

#### IETF Internet-Drafts

**draft-klrc-aiagent-auth-00** (March 2026) — "AI Agent Authentication and Authorization" ([IETF Datatracker](https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/))

Comprehensive model building on:
- WIMSE (Workload Identity in Multi-System Environments) for agent identifiers
- SPIFFE for practical identity management
- OAuth 2.0 family for delegation
- HTTP Message Signatures and WIMSE Proof Tokens

**Authors:** Pieter Kasselman (Defakto), Jeff Lombardo (AWS), Yaroslav Rosomakho (Zscaler), Brian Campbell (Ping Identity)

**Status:** Individual submission, not yet standards track. Expires September 2026.

**draft-oauth-ai-agents-on-behalf-of-user-01** (May 2025) — covered above

**Authors:** Thilina Shashimal Senarath, Ayesha Dissanayaka (WSO2)

**draft-goswami-agentic-jwt-00** (2025) — "Secure Intent Protocol: Agentic JWT" ([IETF Datatracker](https://datatracker.ietf.org/doc/html/draft-goswami-agentic-jwt-00))

Addresses "intent-execution separation" in non-deterministic AI agents. Key innovations:

- **Agent Identity via Checksums**: Cryptographic fingerprints from system prompts, tools, and configs — identity tied to actual implementation
- **New Grant Type**: `urn:ietf:params:oauth:grant-type:agent_checksum`
- **Intent Token Claims**: `workflow_id`, `workflow_step`, `delegation_chain` hash, `step_sequence_hash`
- **Proof-of-Possession**: `cnf` claim with agent's public key prevents token reuse by different agents
- **Chain Integrity**: SHA-256 hashing of delegation sequences (truncated to 16 hex chars) for tamper detection

Resource servers can detect altered delegation paths by comparing submitted hashes against recomputed values.

**Authors:** Goswami et al.

#### OpenID Foundation

**OIDC-A 1.0 Proposal** — "OpenID Connect for Agents" ([arXiv](https://arxiv.org/abs/2509.25974), [Subramanya.ai](https://subramanya.ai/2025/04/28/oidc-a-proposal/))

Extension to OpenID Connect Core 1.0 for LLM-based agents. Key components:

**New Claims:**
- Core: `agent_type`, `agent_model`, `agent_provider`, `agent_instance_id`, `agent_version`
- Delegation: `delegator_sub`, `delegation_chain`, `delegation_purpose`, `delegation_constraints`
- Trust: `agent_capabilities`, `agent_trust_level`, `agent_attestation`

**New Endpoints:**
- **Agent Attestation Endpoint**: Returns verification status, provider info, model details, cryptographic signature
- **Agent Capabilities Endpoint**: Supported constraints, operational characteristics

**Delegation Chain Handling:**
- Chronological order by `delegated_at`
- Scope must be subset of delegator's available scopes
- Multi-step chains with maintained permission constraints

**Attestation:** JWT-based, compatible with IETF RATS Entity Attestation Token (EAT) format

**OpenID Foundation Whitepaper:** "Identity Management for Agentic AI" (October 2025) ([OpenID](https://openid.net/wp-content/uploads/2025/10/Identity-Management-for-Agentic-AI.pdf)) — addresses AI agent identity challenges

#### Summary: Standards Landscape

| Initiative | Organization | Status | Focus |
|------------|-------------|--------|-------|
| AI Agent Standards Initiative | NIST/NCCoE | Concept paper, comments open | Comprehensive guidance |
| draft-klrc-aiagent-auth | IETF (individual) | Internet-Draft | WIMSE + OAuth composition |
| draft-oauth-ai-agents-obo | IETF (individual) | Internet-Draft | User consent for delegation |
| draft-goswami-agentic-jwt | IETF (individual) | Internet-Draft | Intent binding, chain integrity |
| OIDC-A 1.0 | Academic (proposed to OpenID) | Proposal | Agent-specific OIDC claims/endpoints |
| Identity for Agentic AI | OpenID Foundation | Whitepaper | Problem framing |

> **Status:** No ratified standard yet. Multiple overlapping efforts; convergence unclear. MCP + OAuth 2.1 is the de facto baseline.

### Cross-Provider Interoperability

**Cross-App Access (XAA)** is emerging as the interoperability standard for agent token exchange ([Okta Developer Blog](https://developer.okta.com/blog/2025/06/23/enterprise-ai), [Okta AI Agent Token Exchange](https://developer.okta.com/docs/guides/ai-agent-token-exchange/authserver/main/)).

**Protocol Foundation:**
- **Identity and Authorization Chaining Across Domains** (IETF draft)
- **Identity Assertion Authorization Grant** (ID-JAG, co-authored by Aaron Parecki)
- Built on RFC 8693 (Token Exchange) + RFC 7523 (JWT Profile for Authorization Grants)

**XAA Flow:**
1. User authenticates via OIDC, receives ID token
2. AI app exchanges ID token → **ID Assertion JWT** with IdP (policy check)
3. AI app presents ID Assertion JWT to resource app → receives access token

**Provider Maturity:**

| Provider | RFC 8693 Support | XAA/ID-JAG | Notes |
|----------|------------------|------------|-------|
| Keycloak 26.2 | Full | — | First fully compliant OSS |
| Okta | OBO flow | Early Access | AI agent token exchange available |
| Auth0 | Custom Token Exchange | — | Supports RFC 8693 semantics |
| Azure Entra | Proprietary OBO | — | No RFC 8693 grant type |

**Key Advantage:** No user interaction needed; uses existing SSO signing keys; enterprise admin controls policies centrally.

**Gap:** SAML not yet supported; cross-provider exchange (e.g., Okta → Azure) requires federation setup; implementation maturity varies.

## Security Models & Attack Surfaces

### Attack Taxonomy

AI agent credential delegation introduces novel attack surfaces that combine traditional identity attacks with LLM-specific vulnerabilities.

#### 1. Prompt Injection → Credential Exfiltration

**OWASP #1 Critical Vulnerability in 2025** — appears in over 73% of production AI deployments ([Obsidian Security](https://www.obsidiansecurity.com/blog/prompt-injection)).

Attack chain:
1. Attacker embeds hidden instructions in content the agent will process (email, document, GitHub issue)
2. Agent interprets hidden instructions as legitimate commands
3. Agent uses its authorized credentials to perform malicious actions
4. User may never realize exfiltration has occurred

**Real-world incident:** At a major financial institution in 2024, attackers embedded hidden instructions in email content that caused an AI assistant to approve fraudulent wire transfers totaling $2.3 million ([Obsidian Security](https://www.obsidiansecurity.com/blog/security-for-ai-agents)).

**MCP-specific variant:** Traditional GitHub MCP integrations use broad personal access tokens. When the AI encounters malicious prompt injections hidden in GitHub issues, it can steal data from any repository the token allows ([Docker Blog](https://www.docker.com/blog/mcp-horror-stories-github-prompt-injection/)).

#### 2. Token Compromise & Credential Theft

AI agents typically operate with **long-lived API tokens and service account credentials**. When these are stolen, attackers gain persistent access to everything the agent can touch ([Obsidian Security](https://www.obsidiansecurity.com/blog/security-for-ai-agents)).

**The longevity problem:** In August 2025, threat actor UNC6395 used stolen OAuth tokens from Drift's Salesforce integration to access customer environments across 700+ organizations. The tokens had been issued months before and hadn't expired or been revoked ([Reco.ai](https://www.reco.ai/blog/ai-and-cloud-security-breaches-2025)).

**LLMjacking:** Theft of credentials for LLM API access is now prevalent. Microsoft filed a civil lawsuit in 2025 against a gang specializing in stealing LLM credentials ([CSO Online](https://www.csoonline.com/article/4111384/top-5-real-world-ai-security-threats-revealed-in-2025.html)).

#### 3. Confused Deputy Attacks

Classic vulnerability resurfaces in agentic AI: a privileged program (the agent) is tricked into misusing its authority ([BeyondTrust](https://www.beyondtrust.com/blog/entry/confused-deputy-problem), [AuthFyre](https://authfyre.com/blog/how-the-confused-deputy-problem-is-resurfacing-in-cybersecurity)).

**How it manifests:**
- AWS STS misconfigurations
- Misused OAuth scopes
- Microservices accepting untrusted parameters executed with elevated privileges
- Incomplete JWT validation (ignoring `aud` or `iss` claims)

**Example:** Without verifying the audience claim, your application accepts any valid token issued by the IdP. An attacker takes a token issued for their own malicious app and uses it to impersonate a user on your app.

#### 4. Tool Poisoning

Attackers inject malicious instructions hidden within tool descriptions or metadata ([Practical DevSecOps](https://www.practical-devsecops.com/mcp-security-vulnerabilities/)):
- Instructions invisible to users but interpreted by AI
- Trusted tool documentation becomes attack vector
- Can trigger unauthorized file reads or data leaks

**Supabase incident (mid-2025):** Cursor agent with privileged service-role access processed support tickets containing user-supplied input as commands. Attackers embedded SQL instructions to read and exfiltrate integration tokens via a public support thread.

#### 5. MCP-Specific Attack Vectors

Four critical attack categories identified for MCP and agent-to-agent (A2A) communication ([Solo.io](https://www.solo.io/blog/deep-dive-mcp-and-a2a-attack-vectors-for-ai-agents)):

| Attack | Description | Example |
|--------|-------------|---------|
| **Naming Attacks** | Malicious servers register deceptively similar names | `finance-tool-mcp.company.com` vs `finance-tools-mcp.company.com` |
| **Context Poisoning** | Hidden instructions in tool descriptions influence AI decisions | Tool description contains "also send a copy to attacker@evil.com" |
| **Shadowing Attacks** | Malicious components override legitimate tool behavior | Injected instructions alter how trusted tools execute |
| **Rug Pulls** | Legitimate-seeming services build trust then weaponize | Service behaves normally for months, then starts exfiltrating |

**Credential-specific MCP risks:**
- Malicious tools request access to `~/.aws/credentials`, browser cookies, banking files
- Tools designed to extract access tokens through seemingly innocent parameters
- OAuth tokens stored by MCP servers become high-value targets — compromising one MCP server grants access to user's entire digital ecosystem

#### 6. Dynamic Client Registration (DCR) Vulnerabilities

Multiple 1-click account takeover vulnerabilities discovered in MCP servers during 2025 ([Descope](https://www.descope.com/blog/post/dcr-hardening-mcp), [Obsidian Security](https://www.obsidiansecurity.com/blog/when-mcp-meets-oauth-common-pitfalls-leading-to-one-click-account-takeover)).

**Core Problem:** MCP servers act as both authorization servers (for MCP clients) AND OAuth clients (to SaaS platforms) using a single static `client_id`. This creates misaligned security boundaries.

**Attack Patterns:**

| Attack | Mechanism | Result |
|--------|-----------|--------|
| **Shared client_id exploitation** | SaaS AS caches consent for shared ID | Attacker gets victim's authorization |
| **Attacker-initiated consent bypass** | Attacker completes consent, captures redirect URL, sends to victim | Victim clicks, attacker gets code |
| **Subdomain cookie injection** | Compromise subdomain, inject cookie | Defeats CSRF protections |

**Real-World Case — Square MCP:**

Square's `mcp.squareup.com` allowed registration without `redirect_uri` restrictions:
1. Attacker registers malicious MCP client
2. Completes consent, captures redirect to `connect.squareup.com`
3. Sends URL to victim who clicks
4. Attacker exchanges code for tokens — **full merchant data access**

> "Any user who had previously authorized the Square MCP server was vulnerable. A single click on a malicious link granted an attacker full access."

**Mitigations:**
- Strict `redirect_uri` allowlisting during DCR
- State-session binding with `__Host-` prefix cookies
- Display client identity and redirect URI on consent screens
- Rate limiting and IP reputation services

**Emerging Alternative — CIMD (SEP-991):**

Client ID Metadata Documents propose domain-based trust — `client_id` becomes an HTTPS URL pointing to metadata, eliminating DCR endpoints as attack vectors. Adoption remains below 4%.

### Mitigations

**Authentication Controls:**
- Short-lived certificates from trusted PKIs (1-2 hour rotation)
- Hardware security modules for key storage
- Workload identity federation binding agent identity to infrastructure
- No passwords or secrets — use token-based auth only

**Authorization Framework:**
- Zero trust with continuous re-verification
- Least-privilege policies with scope narrowing
- Dynamic, context-aware policy evaluation
- Validate `aud` and `iss` claims on every token

**Operational Security:**
- Sandbox MCP in containers to prevent local credential leakage
- Behavioral analytics with baseline profiles
- Anomaly detection on API patterns, data access, network activity
- Target detection time under 5 minutes

> **What remains unsolved:** No standard mechanism exists to prevent prompt injection from triggering credential abuse. The agent cannot reliably distinguish between legitimate user intent and injected malicious instructions when processing untrusted content.

### Behavioral Analytics for Agent Credential Abuse

UEBA (User & Entity Behavior Analytics) is being extended for AI agent monitoring ([Obsidian Security](https://www.obsidiansecurity.com/blog/ai-agent-monitoring-tools), [CrowdStrike](https://www.crowdstrike.com/en-us/platform/next-gen-identity-security/ueba/), [Exabeam](https://www.exabeam.com/explainers/ueba/what-ueba-stands-for-and-a-5-minute-ueba-primer/)).

**Baseline Establishment:**
- ML-based analysis of API call frequency, data access scope, integration interactions
- Contextual analysis considering agent role, permissions, operational environment
- Baselines set per-entity, compared to peers, and org-wide patterns

**Detection Signals:**

| Signal | Indication |
|--------|------------|
| Unusual authentication patterns | Compromised credentials |
| Unauthorized access attempts | Lateral movement |
| Privilege escalation chains | Confused deputy exploitation |
| Cross-region AssumeRole calls | Cloud credential abuse |
| Data access volume spikes | Exfiltration attempts |

**Market Players:**
- **Exabeam**: UEBA for AI agents via Google Gemini Enterprise integration
- **Darktrace SECURE AI**: Behavioral monitoring for enterprise AI systems
- **Obsidian Security**: Real-time agent monitoring with automated access restriction

**Threat Landscape 2025:**
- Cloud account detections surged **500% year-over-year**
- **70% of breaches** now start with stolen credentials
- Response must operate at **machine speed** — automated access restriction when anomaly detected

### Prompt Injection Mitigations — What Works in Production

Research and industry practice reveal a **defense-in-depth** approach is required. No single technique fully solves the problem.

**Microsoft's Three-Layer Defense** ([Microsoft MSRC](https://www.microsoft.com/en-us/msrc/blog/2025/07/how-microsoft-defends-against-indirect-prompt-injection-attacks)):

| Layer | Technique | Purpose |
|-------|-----------|---------|
| Prevention | Hardened system prompts, Spotlighting (delimiter/datamarking) | Distinguish trusted from untrusted input |
| Detection | Prompt Shields (probabilistic classifier) | Flag injection attempts |
| Impact Mitigation | Deterministic blocking, Human-in-the-loop, Least privilege | Limit damage when injection succeeds |

**Proven Techniques** ([tldrsec/prompt-injection-defenses](https://github.com/tldrsec/prompt-injection-defenses)):
- **SmoothLLM**: Reduced attack success to <1%
- **Jatmo finetuning**: <0.5% success rate vs 87% on undefended GPT-3.5-Turbo
- **Dual LLM pattern**: Isolates untrusted content handling in separate model
- **Task Shield**: Verifies instructions contribute to user-specified goals (2.07% attack success on GPT-4o)

**OWASP Recommendations** ([OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)):
1. Input validation including typoglycemia variants ("ignroe" → "ignore")
2. Structured prompts with clear system/user separation
3. Output monitoring for leaked API keys and system prompts
4. Human-in-the-loop for high-risk keywords ("password", "api_key", "bypass")
5. Least privilege access — don't give LLMs unnecessary permissions

**Credential-Specific Mitigations:**
- Never embed secrets in system prompts (assume extraction)
- Retrieve sensitive data dynamically at execution time
- Use token isolation — agent never sees raw credentials
- Deterministic blocking of exfiltration vectors (markdown images, untrusted links)

**Fundamental Limitation:**
> "Robust defense against persistent attacks may require fundamental architectural innovations rather than incremental improvements to existing post-training safety approaches." — OWASP

Prompt injection exploits an architectural property of how LLMs process language — **it can be mitigated but not patched away**.

## Enterprise Requirements

What do enterprise buyers actually need from AI agent credential systems?

### The Identity Propagation Problem

The core challenge: "The portal knows who Jane is, but how does the AI agent?" Users authenticate to front-end applications, but agents operate as separate services outside that user context. Simply passing usernames in API calls is unacceptable for enterprise security ([Agent Architect](https://theagentarchitect.substack.com/p/enterprise-ai-agents-identity-access-management)).

**Token lifecycle conflicts:** Short-lived access tokens (essential for security) expire during long-running agent tasks. If a user's token expires mid-task, the agent loses access and the task fails.

### Must-Have Requirements

Based on enterprise buyer patterns and SOC 2 compliance needs:

**1. Identity & Access Control**
- SSO integration with enterprise IdPs (Okta, Azure AD, custom SAML) — not just username/password ([Swfte AI](https://www.swfte.com/blog/ai-agent-platforms-enterprise-buyers-guide-2025))
- Unique API credentials per agent, bound to least-privilege policies
- Role-based access filtering based on user group membership
- Transparent token refresh enabling agents to work without user re-authentication

**2. Scope & Time Limits**
- Task-scoped credentials with 5-15 minute TTL ([Aembit](https://aembit.io/blog/ai-agent-architectures-identity-security/))
- Transaction caps, recipient whitelists, asset restrictions
- Automatic access revocation when tasks conclude
- Just-in-time (JIT) provisioning — access granted only when needed

**3. Audit & Compliance**
- Immutable, append-only logs of every policy decision ([PolicyLayer](https://www.policylayer.com/blog/soc2-compliance-ai-agents))
- Cryptographic fingerprints on decision records
- Complete audit trail: who created which agents, when, with what permissions
- SOC 2 Type II, HIPAA, GDPR audit-ready from day one

**4. Kill Switch & Revocation**
- Instant disable capability for compromised agents
- Real-time revocation when employee leaves or changes roles
- Quarterly credential rotation with documented history
- Automated detection of privilege creep

**5. Operational Requirements**
- Direct database connections for workflow systems (Salesforce, ServiceNow, SAP)
- Monitoring integration (Datadog, Splunk, PagerDuty)
- Non-custodial architecture — private keys never leave customer infrastructure
- Local transaction signing after policy approval

### The Trust Chain Architecture

Emerging solution pattern combines three security layers ([Agent Architect](https://theagentarchitect.substack.com/p/enterprise-ai-agents-identity-access-management)):

1. **Hard Security**: API gateways validating JWT signatures from trusted IdPs
2. **Soft Security**: Integration processes applying granular authorization rules based on user group membership
3. **Contextual Security**: Agents filtering results based on user permissions during operations

> **Key insight:** "Success depends on robust identity infrastructure, not AI sophistication."

### Compliance Framework Requirements

**SOC 2 Trust Services Criteria** were designed for human-operated systems. AI agents break this assumption by making autonomous decisions at machine speeds ([Teleport](https://goteleport.com/blog/ai-agents-soc-2/), [PolicyLayer](https://www.policylayer.com/blog/soc2-compliance-ai-agents)).

**SOC 2 Credential Requirements:**

| Requirement | Specification |
|-------------|---------------|
| API key scoping | Unique keys per agent, policy-based authorization |
| Key rotation | Quarterly minimum |
| Transaction limits | Per-transaction caps (e.g., $1,000), daily spending limits |
| Intent verification | SHA-256 fingerprinting, two-gate enforcement (LLM intent → deterministic validation) |
| Non-custodial | Private keys never leave customer infrastructure |

**SOC 2 Audit Trail Requirements:**

Each policy decision must log:
- Event ID + precise timestamp
- Organization and agent identifiers
- Complete transaction intent (chain, asset, recipient, amount)
- Applied policy version and active limits
- Current spending counters
- Explicit approval/denial with reason codes
- Request ID and source IP

Logs must be **append-only, immutable**, retained per policy. WORM storage recommended.

**ISO/IEC 42001** adds AI-specific controls:
- Model cards and documentation
- Bias mitigation procedures
- Human oversight requirements
- 38 distinct controls across 9 objectives
- Surveillance audits at 12-month intervals

**Processing Integrity (SOC 2 PI Series):**

> "The AI's decision is irrelevant to processing integrity. What matters is the _executed_ transaction matches the _validated_ intent."

Separation of intent from execution is critical — the agent's reasoning doesn't matter for compliance; the audit trail of what was authorized vs. what executed does.

### Where Buyers Expect This to Live

Market fragmentation — no consensus on where agent credential systems should reside:

| Vendor Type | Example | Approach |
|-------------|---------|----------|
| IdP | Okta, Entra | Add agent identity to existing identity fabric |
| Agent platform | Descope, Scalekit | Embed auth into agent development workflow |
| Standalone | Aembit, Nango | Independent broker across all environments |

Enterprises with existing IdP investments (Okta, Azure AD) prefer extending those. Greenfield agent deployments lean toward purpose-built platforms.

## AI Agent Framework Landscape — Credentials

How do the major agent frameworks handle authentication and credentials today?

### The Problem

Agent authentication differs from user authentication. LangGraph and similar frameworks handle user identity, but the real challenge is when agents need to access external services. The question: **"Can this agent, acting for this user, perform this action on this resource?"** ([Arcade](https://www.arcade.dev/blog/agent-authorization-langgraph-guide))

**Common anti-patterns:**
- **Service accounts**: Create security bypass — users circumvent RBAC by going through agents
- **Full user permissions**: Excessive blast radius — agents get deletion rights users legitimately have but shouldn't delegate

### Framework-by-Framework Status

| Framework | Auth Approach | Credential Management | Maturity |
|-----------|---------------|----------------------|----------|
| **LangGraph** | Custom auth handlers, AES-256-GCM encrypted secrets | Token passed to server, decrypted at runtime | Production-ready with effort |
| **LlamaIndex** | Environment variables, custom tool wrappers | No built-in credential management | Basic |
| **CrewAI** | Environment variables | No native OAuth support | Basic |
| **AutoGen** | Environment variables | Secrets in config files | Basic (merging with Semantic Kernel 2026) |
| **AWS Bedrock AgentCore** | Full OAuth 2.0 (client credentials + auth code), token vault | Zero trust, delegation-based with audit trails | Enterprise-ready |

### LangGraph Platform Auth

LangGraph Platform provides custom authentication and resource-level access control ([LangChain Blog](https://blog.langchain.com/custom-authentication-and-access-control-in-langgraph/)):
- Register auth function that runs on every request
- GitHub OAuth for user authentication
- AES-256-GCM encryption for secrets
- Same encryption key required in web app and agent

**Gap:** LangGraph handles orchestration but lacks a tool authorization layer for external OAuth flows.

### AWS Bedrock AgentCore Identity

Purpose-built identity service for AI agents ([AWS Docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html)):
- Native OAuth 2.0 client credentials (M2M) and authorization code (user-delegated) flows
- **Delegation, not impersonation**: Agents authenticate as themselves while carrying verifiable user context
- Secure token vault with automatic refresh
- Fine-grained access control with comprehensive audit trails
- Revocable agent access independent of user access

### Third-Party Solutions

**Arcade.dev** ([Arcade Blog](https://www.arcade.dev/blog/agent-authorization-langgraph-guide)):
- MCP gateway exposing tools as LangChain-compatible functions
- User-scoped OAuth security with persistent token storage
- Just-in-time authorization: OAuth flows trigger when needed, not upfront
- Least-privileged access: minimum required scopes per action

**Azure + LangGraph + Arcade template** ([GitHub](https://github.com/langchain-samples/langgraph-azure-arcade-oauth-agent)):
- Azure AD/Entra ID integration
- Persistent token storage in Cosmos DB
- MCP gateway for tool discovery

### Best Practices Emerging

From [WorkOS](https://workos.com/blog/securing-ai-agents), [1Password](https://1password.com/solutions/agentic-ai), [Auth0](https://auth0.com/blog/genai-tool-calling-intro/):

1. **Eliminate static secrets**: Use workload identity and dynamic credentials
2. **Asymmetric over symmetric**: JWT-based credentials and X509 certs > API keys
3. **Just-in-time credentials**: Scoped based on RBAC, expire in minutes/hours
4. **Centralized management**: Unified secrets store, audit every request/rotation
5. **LLM isolation**: Tokens retrieved at tool execution, never passed to model

### LLM Provider Tool-Use Authentication

Major LLM providers have divergent approaches to tool authentication:

**OpenAI GPT Actions** ([OpenAI Docs](https://developers.openai.com/api/docs/actions/authentication/)):
- Three options: None, API Key (encrypted storage), OAuth
- OAuth is "most robust" — user token passed in Authorization header
- `x-openai-isConsequential` flag triggers mandatory user confirmation
- Callback URL: `https://chat.openai.com/aip/{GPT_ID}/oauth/callback`
- Allows third-party OAuth tokens with self-managed compliance

**Anthropic Claude** (Feb 2026 policy change):
- OAuth restricted to Claude Code and Claude.ai only
- Third-party tools must use API keys via Claude Console
- Crackdown driven by abuse: autonomous agents running expensive loops on $200/mo subscriptions
- MCP connector available for Claude API

> "A Claude Max subscription at $200/month was never designed to handle an autonomous agent running LLM calls all day — in API terms, that kind of workload can easily cost thousands of dollars."

**Google Gemini** ([Google AI](https://ai.google.dev/gemini-api/docs/oauth), [Credential Delegation](https://jpassing.com/2026/01/27/letting-users-delegate-access-from-gemini-enterprise-to-agent-engine/)):
- Supports API keys and OAuth for Gemini API
- **Gemini Enterprise credential delegation**: user consents once, access token forwarded in `tool_context.session.state`
- Auth handled per-agent (all-or-nothing), unlike ADK's per-tool decorators
- User delegation ensures audit logs contain actual user principal (not just agent)
- Limitation: all OAuth scopes declared upfront, workforce identity federation limited

**Implications:**
- No standardized delegation across providers
- Each has proprietary authentication approach
- Cost control driving policy decisions
- Developers must handle provider-specific integration

### The Developer Experience Gap

For a developer building an agent that needs OAuth today:
1. **Easy path (insecure)**: Hardcode API keys in environment variables
2. **Medium path**: Use Arcade, Nango, or Auth0 for credential brokering
3. **Enterprise path**: AWS AgentCore, Azure AD + custom integration, Okta for AI Agents

Most open-source frameworks assume environment variables. Production-ready credential management requires external tooling.

## The Enterprise Security Gap

Research reveals a stark disconnect between enterprise AI agent deployment velocity and security infrastructure readiness ([Straiker](https://www.straiker.ai/blog/the-agent-security-gap-why-75-of-leaders-wont-let-security-concerns-slow-their-ai-deployment), [Obsidian Security](https://www.obsidiansecurity.com/blog/ai-agent-market-landscape)).

### By The Numbers

| Metric | Value | Source |
|--------|-------|--------|
| Enterprises planning to expand AI agents in 2025 | 96% | IT leaders survey |
| Agents over-permissioned | 90% | Market analysis |
| Privilege excess | 10x more than required | Obsidian |
| Complete visibility into agent permissions | Only 21% | Enterprise survey |
| Cannot enforce purpose limitations | 63% | Compliance audit |
| Data movement vs. human users | 16x more | Agent monitoring |
| Security as primary deployment challenge | 75% cite it | IT leaders survey |

### The Paradox

Despite security concerns, enterprises deploy anyway. Average ROI projections (171%, 192% for U.S.) create competitive pressure that overrides security hesitancy. The result: **organizations racing to deploy agents faster than they're building the security infrastructure to protect them.**

### What's Missing

**Pre-deployment controls exist** (scoped credentials, sandboxing, static policies). **Runtime security is the gap:**
- Real-time behavioral monitoring
- Sub-second threat detection
- Prompt injection prevention at scale
- Tool use validation ensuring authorized scope
- Comprehensive cross-agent audit trails

### Breach Reality

The 2025 Drift breach demonstrated the blast radius: attackers hijacked a chat agent integration to breach **700+ organizations** with 10x greater impact than previous incidents. First documented large-scale AI-executed cyberattack (September 2025) showed AI systems performing 80-90% of attack work autonomously.

## Why Traditional IAM Fails for Agentic AI

ISACA analysis identifies fundamental mismatches between legacy IAM systems and autonomous AI agents ([ISACA](https://www.isaca.org/resources/news-and-trends/industry-news/2025/the-looming-authorization-crisis-why-traditional-iam-fails-agentic-ai)):

> "Organizations are attempting to safeguard dynamic, independent agents with security techniques optimized for human-operated, single-purpose programs."

**Six Critical Failures:**

| Failure Mode | Description |
|--------------|-------------|
| **Coarse-grained permissions** | Static roles cannot adapt to fine-grained, task-specific permissions that change dynamically |
| **Delegation complexity** | Legacy systems cannot represent subagent creation or multi-principal representation |
| **Limited context awareness** | Access decisions ignore runtime conditions and agent intent |
| **Scalability** | Managing hundreds/thousands of transient agents strains token infrastructure |
| **Weak inter-agent trust** | OAuth/SAML hierarchical trust assumptions fail for peer-to-peer agent auth |
| **Revocation chaos** | Compromised agents continue interacting across decentralized systems |

**Emerging Solutions:**
1. **Zero Trust + DIDs**: Cryptographic decentralized identifiers, verifiable credentials, zero-knowledge proofs
2. **ARIA (Agent Relationship-Based Identity)**: Treats delegation relationships as first-class graph objects, extends OAuth 2.0 Rich Authorization Requests, enables "surgically revocable" authority termination

## Open Problems & Gaps

Based on research findings, these remain unsolved or inadequately addressed:

### 1. Prompt Injection → Credential Abuse

No standard mechanism prevents prompt injection from triggering unauthorized credential use. The agent cannot reliably distinguish legitimate user intent from injected instructions when processing untrusted content.

### 2. Downstream Authorization Gap

MCP defines client-to-server auth but not how servers propagate identity downstream. Each MCP server must implement RFC 8693 token exchange independently — no standardized pattern.

### 3. Multi-Agent Delegation Chains

How do nested `act` claims work when Agent A delegates to Agent B which calls Service C? RFC 8693 supports nesting but has a critical gap.

**Delegation Chain Splicing Attack:**

RFC 8693 does not require cross-validation between `subject_token` and `actor_token` at the STS. A compromised intermediary can present tokens from different delegation contexts to create a fraudulent chain that never actually occurred ([IETF OAuth WG](http://www.mail-archive.com/oauth@ietf.org/msg25680.html)).

**Why It Matters for Agentic AI:**
- Audit trail integrity (HIPAA, SOC 2 compliance)
- Policy enforcement ("was there a human in the loop?", "how many delegation hops?")
- Anomaly detection and trust scoring

**Proposed Mitigations:**
1. Make `may_act` claim normative (currently optional)
2. Audience/subject chaining where `aud` at step N matches `sub` at step N+1
3. Per-step signed delegation receipts for verifiable provenance
4. SHA-256 chain hashes for tamper detection (as in Agentic JWT draft)

**Access Control Limitation:**

> "For the purpose of applying access control policy, the consumer of a token MUST only consider the token's top-level claims and the party identified as the current actor by the act claim. Prior actors identified by any nested act claims are informational only."
> — [RFC 8693](https://datatracker.ietf.org/doc/html/rfc8693)

This means resource servers cannot enforce policies based on delegation chain history without custom implementation.

### 4. Token Lifecycle for Long-Running Tasks

Short-lived tokens (5-15 min) conflict with long-running agent tasks (hours/days). Current solutions:
- Background refresh mechanisms
- Task checkpointing with re-auth
- No standardized approach

### 5. Cross-Org Federation

Agents operating across cloud providers and SaaS platforms require secure federation mechanisms. SPIFFE/OIDC help but no agent-specific federation standard exists.

### 6. Kill Switch & Cascade Revocation

No protocol-level standard for instant agent revocation. The fundamental challenge: **JWTs are self-contained** — deleting a token from a database doesn't prevent its use until expiration.

**Current Production Patterns:**

| Approach | Mechanism | Limitation |
|----------|-----------|------------|
| Short-lived tokens | Minutes TTL, no refresh | Long tasks need re-auth |
| Distributed revocation lists | Check blacklist at each hop | Latency, availability concerns |
| Gateway transformation | Issue short-lived downstream assertions | Gateway becomes bottleneck |
| Stateful delegation tracking | Okta FGA, Agent Passport System | Requires custom implementation |

**Agent Passport System** (OSS, Ed25519-based) implements **cascade revocation**: revoking a parent delegation automatically invalidates all dependent work receipts via Merkle proof invalidation ([GitHub](https://github.com/aeoess/agent-passport-system)).

**RFC 7009 OAuth Revocation** allows cascading: "revocation of a particular token may cause revocation of related tokens and the underlying authorization grant" — but doesn't specify how ([RFC 7009](https://datatracker.ietf.org/doc/html/rfc7009)).

**Open Questions:**
- How to handle inflight operations when revocation occurs?
- What's acceptable latency for revocation propagation?
- How to notify all downstream systems in multi-hop chains?

### 7. Intent vs. Authority Mismatch

Just because a user *could* delete all files doesn't mean an agent *should* be able to. Capability-based security models exist but aren't integrated into agent auth flows.

## Implications for Cred

Based on this research, a product in the agent credential delegation space should consider:

### Opportunity Gaps

**1. MCP Downstream Authorization Bridge**
MCP defines client-to-server auth but leaves downstream propagation unspecified. A product that provides standardized RFC 8693 token exchange for MCP servers would fill a critical gap. This is where every MCP server today must implement its own solution.

**2. Developer Experience Gap**
Most OSS frameworks assume environment variables. The path from "hardcoded API key" to "enterprise-grade OAuth" is painful. A solution that provides:
- Drop-in OAuth 2.1 for LangGraph/LlamaIndex/CrewAI
- Credential brokering without code changes
- Gradual migration path from env vars to proper auth

**3. Multi-Agent Delegation Chain**
No standard handles nested `act` claims for Agent A → Agent B → Service C. First mover advantage in defining and implementing multi-hop delegation with preserved audit trails.

**4. Kill Switch / Revocation**
No protocol-level standard. A centralized revocation service that works across agent frameworks and MCP servers would be highly valuable for enterprise buyers (SOC2/compliance requirement).

### Positioning Options

| Position | Compete With | Differentiation Needed |
|----------|-------------|----------------------|
| IdP extension | Okta, Entra | Deep MCP/agent framework integration |
| Agent platform | Descope, Scalekit | Broader framework support, OSS story |
| Standalone broker | Aembit, Nango | Enterprise compliance, audit trails |
| Developer tool | Arcade.dev | Better UX, broader API coverage |

### Technical Considerations

**Build on established standards:**
- OAuth 2.1 + PKCE (required by MCP)
- RFC 8693 token exchange for delegation
- SPIFFE for workload identity (optional, enterprise)
- MCP Protected Resource Metadata for discovery

**Enterprise table stakes:**
- SSO integration (Okta, Azure AD, SAML)
- Immutable audit trails with cryptographic fingerprints
- Task-scoped credentials (5-15 min TTL)
- Non-custodial option (keys in customer infra)

**Security differentiator:**
- Token isolation from LLM (agent never sees raw credentials)
- Least-privilege enforcement at tool execution layer
- Anomaly detection on credential usage patterns

### Risks

1. **Standards convergence:** If NIST or IETF standardizes quickly, early implementations may need rework
2. **Platform play:** Microsoft (Entra Agent ID) and AWS (AgentCore Identity) have resources to dominate enterprise
3. **MCP evolution:** If MCP adds downstream auth natively, the opportunity shrinks
4. **Security incidents:** Any major breach involving agent credentials will reshape the market overnight

### Recommended Next Steps

1. **Monitor:** NIST comment period (April 2026), IETF draft progress, MCP roadmap
2. **Prototype:** RFC 8693 bridge for MCP, drop-in for LangGraph
3. **Validate:** Talk to enterprises about actual RFP requirements, production deployment blockers
4. **Differentiate:** Focus on developer experience or enterprise compliance — both markets exist but require different GTM

## Sources

### Primary Sources Cited

**Standards & Specifications:**
- [RFC 8693 — OAuth 2.0 Token Exchange](https://datatracker.ietf.org/doc/html/rfc8693)
- [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Authorization Tutorial](https://modelcontextprotocol.io/docs/tutorials/security/authorization)
- [IETF draft-oauth-ai-agents-on-behalf-of-user-01](https://www.ietf.org/archive/id/draft-oauth-ai-agents-on-behalf-of-user-01.html)
- [IETF draft-klrc-aiagent-auth-00](https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/)
- [IETF draft-goswami-agentic-jwt-00](https://datatracker.ietf.org/doc/html/draft-goswami-agentic-jwt-00)
- [IETF OAuth WG — Delegation Chain Splicing Security Discussion](http://www.mail-archive.com/oauth@ietf.org/msg25680.html)

**Academic:**
- [Authenticated Delegation for AI Agents (arXiv)](https://arxiv.org/html/2501.09674v1)
- [OIDC-A 1.0 Proposal (arXiv)](https://arxiv.org/abs/2509.25974)

**Industry Analysis:**
- [Christian Posta — API Keys Are Bad for AI Agents](https://blog.christianposta.com/api-keys-are-a-bad-idea-for-enterprise-llm-agent-and-mcp-access/)
- [Stack Overflow Blog — Auth in MCP](https://stackoverflow.blog/2026/01/21/is-that-allowed-authentication-and-authorization-in-model-context-protocol/)
- [Obsidian Security — AI Agent Security](https://www.obsidiansecurity.com/blog/security-for-ai-agents)
- [Arcade — Agent Auth Problem](https://www.arcade.dev/blog/agent-authorization-langgraph-guide)
- [Stacklok — Token Delegation for MCP Multi-User AI Systems](https://dev.to/stacklok/token-delegation-and-mcp-server-orchestration-for-multi-user-ai-systems-3gbi)
- [Spherical Cow Consulting — Delegation in a Multi-Actor World](https://sphericalcowconsulting.com/2025/06/27/delegation-part-two/)

**Vendor Documentation:**
- [Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-id)
- [Microsoft Entra Agent OAuth Protocols](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-oauth-protocols)
- [Okta for AI Agents](https://www.okta.com/solutions/secure-ai/)
- [Okta — Agent Delegation Chain Security](https://www.okta.com/blog/ai/agent-security-delegation-chain/)
- [Auth0 for GenAI](https://auth0.com/ai)
- [AWS Bedrock AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html)
- [Descope Agentic Identity Hub](https://www.descope.com/press-release/agentic-identity-hub)

**Analysis & Research:**
- [ISACA — The Looming Authorization Crisis: Why Traditional IAM Fails Agentic AI](https://www.isaca.org/resources/news-and-trends/industry-news/2025/the-looming-authorization-crisis-why-traditional-iam-fails-agentic-ai)
- [GitGuardian — OAuth for MCP: Emerging Enterprise Patterns](https://blog.gitguardian.com/oauth-for-mcp-emerging-enterprise-patterns-for-agent-authorization/)
- [Agent Passport System (GitHub)](https://github.com/aeoess/agent-passport-system)
- [Straiker — The Agent Security Gap](https://www.straiker.ai/blog/the-agent-security-gap-why-75-of-leaders-wont-let-security-concerns-slow-their-ai-deployment)
- [Obsidian Security — 2025 AI Agent Market Landscape](https://www.obsidiansecurity.com/blog/ai-agent-market-landscape)
- [Teleport — AI Agents Impact on SOC 2](https://goteleport.com/blog/ai-agents-soc-2/)
- [PolicyLayer — SOC 2 Compliance for AI Agents](https://www.policylayer.com/blog/soc2-compliance-ai-agents)
- [Lasso Security — ISO/IEC 42001](https://www.lasso.security/blog/iso-iec-42001)
- [Ultrathink — MCP Gateway Authentication](https://ultrathinksolutions.com/the-signal/mcp-gateway-authentication/)
- [Red Hat — Advanced MCP Gateway Auth](https://developers.redhat.com/articles/2025/12/12/advanced-authentication-authorization-mcp-gateway)
- [Obsidian Security — Real-Time AI Agent Monitoring](https://www.obsidiansecurity.com/blog/ai-agent-monitoring-tools)
- [CrowdStrike — UEBA for Identity Protection](https://www.crowdstrike.com/en-us/platform/next-gen-identity-security/ueba/)
- [Exabeam — UEBA Primer](https://www.exabeam.com/explainers/ueba/what-ueba-stands-for-and-a-5-minute-ueba-primer/)
- [Okta — AI Agent Token Exchange](https://developer.okta.com/docs/guides/ai-agent-token-exchange/authserver/main/)
- [Okta — Cross-App Access for Enterprise AI](https://developer.okta.com/blog/2025/06/23/enterprise-ai)
- [Keycloak — Token Exchange](https://www.keycloak.org/securing-apps/token-exchange)
- [Descope — DCR Hardening for MCP](https://www.descope.com/blog/post/dcr-hardening-mcp)
- [Obsidian — MCP OAuth Pitfalls: 1-Click Account Takeover](https://www.obsidiansecurity.com/blog/when-mcp-meets-oauth-common-pitfalls-leading-to-one-click-account-takeover)
- [WorkOS — DCR in MCP](https://workos.com/blog/dynamic-client-registration-dcr-mcp-oauth)
- [OpenAI — GPT Actions Authentication](https://developers.openai.com/api/docs/actions/authentication/)
- [Dave Swift — Claude OAuth Update](https://daveswift.com/claude-oauth-update/)
- [Claude MCP Connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
- [WorkOS — Descope vs WorkOS for Agentic Identity](https://workos.com/blog/descope-vs-workos-agentic-identity-enterprise-authentication)
- [Nango — Best AI Agent Authentication Platforms](https://nango.dev/blog/best-ai-agent-authentication)
- [Aembit Pricing](https://aembit.io/pricing/)
- [Google Gemini OAuth Quickstart](https://ai.google.dev/gemini-api/docs/oauth)
- [Gemini Enterprise Credential Delegation](https://jpassing.com/2026/01/27/letting-users-delegate-access-from-gemini-enterprise-to-agent-engine/)

**Standards Bodies:**
- [NIST AI Agent Standards Initiative](https://www.nist.gov/caisi/ai-agent-standards-initiative)
- [OpenID Foundation — Identity Management for Agentic AI](https://openid.net/wp-content/uploads/2025/10/Identity-Management-for-Agentic-AI.pdf)
