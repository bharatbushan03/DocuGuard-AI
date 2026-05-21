# DocuGuard AI — Portfolio Kit

Copy-ready materials for GitHub, LinkedIn, resumes, and interviews.  
**Live repo:** https://github.com/bharatbushan03/DocuGuard-AI

---

## 1. GitHub Repository Description

**Short (GitHub About — max ~350 chars):**

```
Enterprise RAG assistant: grounded Q&A over PDF/DOCX with Qdrant + OpenAI, FastAPI & Next.js. Features RBAC, citation verification, confidence/risk scoring, prompt-injection defense, admin analytics, Docker, and 63+ tests.
```

**Topics / tags:** `rag` `llm` `fastapi` `nextjs` `qdrant` `openai` `nlp` `enterprise-ai` `vector-database` `prompt-injection` `docker` `python` `typescript`

**Extended description (for README pin or project page):**

DocuGuard AI is a production-style enterprise knowledge assistant that combines retrieval-augmented generation with compliance guardrails. It ingests policy documents, enforces role-based vector search, generates cited answers with confidence and risk signals, and includes security hardening plus an offline evaluation harness—demonstrating full-stack LLM application engineering beyond a basic chatbot demo.

---

## 2. LinkedIn Project Post

```
🚀 Project highlight: DocuGuard AI — Enterprise RAG Assistant

I built DocuGuard AI to show how LLM applications should work in regulated, document-heavy environments—not as open-ended chatbots, but as grounded, auditable systems.

What it does:
• Answers HR/legal/policy questions using only uploaded corpora (RAG)
• Retrieves context from Qdrant with role-based metadata filters
• Returns cited answers with confidence scores and human-review flags
• Detects high-risk topics and prompt-injection attempts

Tech stack:
Python · FastAPI · Next.js · PostgreSQL · Qdrant · OpenAI · Docker

What I’m proud of technically:
✅ End-to-end ingestion (PDF/DOCX/TXT) → chunk → embed → vector index
✅ Secure RAG orchestration (ACL before LLM, untrusted document wrapping)
✅ Citation verification + offline evaluation (Jaccard, citation/risk/refusal metrics)
✅ 63+ automated tests including prompt-injection scenarios
✅ Full Docker Compose deployment with health checks

This project reflects skills I bring to enterprise AI teams: NLP/RAG pipeline design, vector DB integration, LLM safety, API/product engineering, and measurable quality—not just prompt engineering.

🔗 GitHub: https://github.com/bharatbushan03/DocuGuard-AI
📄 Security model & architecture documented in-repo.

#MachineLearning #NLP #RAG #LLM #FastAPI #NextJS #GenerativeAI #Portfolio #SoftwareEngineering #AIEngineering
```

---

## 3. Resume Bullet Points (5)

```
• Architected DocuGuard AI, an enterprise RAG platform (FastAPI, Next.js, PostgreSQL, Qdrant, OpenAI) delivering cited, access-controlled Q&A over PDF/DOCX corpora with Dockerized deployment and 63+ automated tests.

• Built production NLP ingestion and indexing: multi-format text extraction, semantic chunking, batch embeddings (text-embedding-3-small), and metadata-rich vector upserts with background job orchestration.

• Designed secure retrieval-augmented generation with Qdrant ACL filters, JSON-structured LLM outputs, citation verification, confidence scoring, and risk-based human-review escalation for high-stakes queries.

• Implemented enterprise AI security controls—JWT/RBAC, magic-byte upload validation, prompt-injection detection/sanitization for user and document inputs, and redacted audit logging.

• Created offline RAG evaluation harness measuring answer similarity, citation accuracy, risk classification, and refusal behavior; published reproducible metrics via JSON/CSV reports on a labeled dataset.
```

---

## 4. Two-Minute Demo Script

**Setup (before recording):** `docker compose up -d` → migrations → `python seed.py` → login as `admin@docuguard.com`

| Time | Action | Say this |
|------|--------|----------|
| **0:00–0:15** | Show repo README + architecture diagram | "DocuGuard AI is an enterprise RAG assistant. Documents go in, authorized users get grounded answers with citations—not hallucinated policies." |
| **0:15–0:35** | Login → Dashboard → Documents | "Users upload PDFs or text files. The backend validates file types, chunks content, embeds it into Qdrant, and tracks indexing status." |
| **0:35–1:05** | Chat: *"What is the remote work policy?"* | "Here’s the RAG loop: embed the question, retrieve top chunks with role filters, prompt the LLM with untrusted context markers, then verify citations and score confidence." |
| **1:05–1:25** | Expand citations / source previews | "Every claim ties to a document chunk. We only expose previews in the API to reduce data leakage." |
| **1:25–1:45** | Ask: *"How do I fire an employee?"* | "Risk classification flags sensitive HR/legal topics and recommends human review—enterprise AI needs guardrails, not just answers." |
| **1:45–2:00** | Quick injection attempt + Admin panel | "Prompt-injection phrases are detected and neutralized. Admins see query analytics and high-risk logs. Full stack is tested and documented on GitHub." |

**Closer (last 5 seconds):** "DocuGuard shows I can ship RAG systems that are useful, measurable, and safe enough for real teams."

---

## 5. System Architecture Explanation

### Narrative (interview-ready)

DocuGuard AI follows a **classic three-tier RAG architecture** extended for enterprise constraints.

**Presentation tier (Next.js):** React pages for authentication, document upload, chat, and admin analytics. The browser holds JWT cookies and calls REST APIs; admin role is verified server-side via `/api/auth/me`, not client-only flags.

**Application tier (FastAPI):** Stateless API services coordinate auth, ingestion, chat, and observability. Business logic lives in service modules—not route handlers—so RAG, security, and parsing can be tested independently.

**Data tier:** PostgreSQL stores authoritative metadata (users, documents, sessions, audit logs). Qdrant stores dense embeddings plus payload fields (`uploaded_by`, `access_level`) used as **mandatory retrieval filters**. Uploaded binaries sit on a dedicated volume.

**External AI tier:** OpenAI provides embeddings and chat completion. The app never trusts model output blindly: structured JSON, citation verification, and confidence/risk modules run after generation.

### Request path for a chat query

1. JWT validated → user identity and role resolved.  
2. User text sanitized; injection patterns logged.  
3. Chat session ownership verified (**before** retrieval).  
4. Query embedded → Qdrant similarity search with RBAC filter.  
5. Chunks sanitized and wrapped as untrusted reference data.  
6. LLM produces JSON answer with citations.  
7. Post-processors adjust answer, compute scores, persist audit log.  
8. Client receives answer + metadata (no full chunk bodies).

### Why this split matters

- **PostgreSQL** = source of truth for permissions and compliance audit.  
- **Qdrant** = fast semantic recall, but only as a *cache* of text already authorized in SQL.  
- **FastAPI** = low-latency orchestration and explicit security checkpoints in the pipeline order.

See [README.md — Architecture](README.md#5-architecture) for Mermaid diagrams.

---

## 6. Technical Challenges Solved

| Challenge | Approach | Skills demonstrated |
|-----------|----------|---------------------|
| **Grounded answers vs. hallucination** | Strict context-only prompts, citation verifier, refusal language for low retrieval | NLP, RAG, evaluation |
| **Cross-user document leakage** | SQL ACL on list/detail + Qdrant `should` filters on `uploaded_by` / `public` | Vector DB, security, enterprise AI |
| **Indirect prompt injection via uploads** | Untrusted context wrapping, chunk sanitization, pattern detection | LLM safety, NLP |
| **Direct jailbreak queries** | Regex category detection, system rules, safe continuation with human-review flag | LLM agents, security |
| **MIME spoofing on uploads** | Magic-byte validation independent of client `Content-Type` | Security, FastAPI |
| **Privilege escalation at signup** | Server-assigned roles only; no client-supplied `admin` | Enterprise AI, FastAPI |
| **Chat session IDOR** | Session ownership check before embed/retrieve/LLM | Security, API design |
| **Sensitive data in API/logs** | Chunk previews + redacted storage in `QueryLog` | Enterprise AI, compliance |
| **Subjective “does RAG work?”** | Labeled dataset + `evaluate.py` with citation/risk/refusal metrics | Evaluation |
| **Reproducible deployment** | Docker Compose, health checks, named volumes, env templates | DevOps, FastAPI, Next.js |
| **Structured LLM outputs** | `response_format: json_object` + downstream parsers | LLM agents |
| **High-stakes HR/legal queries** | Risk classifier elevates severity and human review | Enterprise AI, NLP |

---

## 7. Future Improvements

Prioritized roadmap for portfolio → production evolution:

**Near term**
- [ ] Hybrid retrieval (BM25 + dense) for better recall on policy keywords  
- [ ] Streaming chat responses (SSE) for UX  
- [ ] Document delete with Qdrant point cleanup  
- [ ] API rate limiting and upload quotas  

**Security & compliance**
- [ ] ClamAV / cloud malware scanning on ingest  
- [ ] JWT refresh + revocation list  
- [ ] SSO (OIDC) for enterprise IdP  
- [ ] Tamper-evident audit log export  

**Quality & MLOps**
- [ ] CI gate on `evaluate.py` pass rate regression  
- [ ] LLM-as-judge metrics alongside Jaccard  
- [ ] Chunking experiments (semantic splits vs. fixed windows)  
- [ ] Embedding model A/B tests  

**Scale & product**
- [ ] Multi-tenant workspaces  
- [ ] Async job queue (Celery/Redis) for ingestion at scale  
- [ ] Admin RBAC for query-log PII policies  
- [ ] Analytics dashboard (time-series query volume)  

---

## 8. Interview Talking Points

### Elevator pitch (30 seconds)

> "DocuGuard AI is an enterprise RAG system I built end-to-end. It ingests policy documents, indexes them in Qdrant, and answers employee questions with citations—while enforcing role-based access, detecting prompt injection, and flagging high-risk answers for human review. It’s Dockerized, tested, and evaluated on a labeled dataset—not just a notebook demo."

### Deep-dive prompts & how to answer

**"Walk me through your RAG pipeline."**  
Cover: ingest → chunk → embed → store with metadata → query embed → filtered retrieval → prompt assembly → JSON generation → citation verify → confidence/risk → audit log. Emphasize **ACL before LLM**.

**"How do vector DB filters relate to Postgres security?"**  
Explain dual enforcement: SQL for listing documents, Qdrant payload filters for retrieval. Admit Qdrant is a performance layer; SQL remains authoritative. Mention localhost-only exposure in Docker.

**"How do you handle prompt injection?"**  
Direct: sanitize user query, detect categories, system prompt rules. Indirect: treat chunks as `UNTRUSTED_REFERENCE_DATA`, strip delimiter attacks, continue safely with `requires_human_review`. Point to `test_prompt_injection.py`.

**"How do you evaluate quality without production traffic?"**  
Describe `evaluation_dataset.json`, metrics (Jaccard, citation accuracy, risk, refusal), and CSV/JSON reports. Discuss limits: Jaccard ≠ semantic equivalence; future LLM-judge.

**"Why FastAPI + Next.js?"**  
FastAPI for typed APIs, OpenAPI docs, async-friendly orchestration, pytest. Next.js for polished UX, App Router, easy deploy. Separation keeps ML logic testable in Python.

**"What would break at scale?"**  
Background tasks in-process, single Qdrant collection, no queue for ingestion, embedding batch limits. Propose Celery, sharding, caching, horizontal API replicas.

**"Biggest tradeoff you made?"**  
Example: pattern-based injection detection vs. latency/cost of classifier model—chose interpretable rules + tests for portfolio clarity; would add ML detector in production.

**"What distinguishes this from ChatGPT with files?"**  
RBAC-aligned retrieval, citation verification, audit logs, risk escalation, injection defenses, offline eval harness, full code ownership.

### Skills matrix (map to your project)

| Skill area | Evidence in DocuGuard |
|------------|----------------------|
| **NLP** | PDF/DOCX extraction, chunking, embedding pipeline |
| **RAG** | Retrieve → augment → generate with context-only rules |
| **LLM agents** | Multi-step orchestration: retrieve, generate, verify, classify, score |
| **Vector databases** | Qdrant collection design, metadata filters, upsert/search |
| **FastAPI** | REST API, JWT deps, background tasks, OpenAPI |
| **Next.js** | Auth flow, chat UI, admin dashboard |
| **Evaluation** | `evaluate.py`, labeled dataset, composite pass metrics |
| **Security** | RBAC, injection module, upload validation, SECURITY.md |
| **Enterprise AI** | Human review, audit logs, redaction, compliance-oriented UX |

### Questions to ask them (shows maturity)

- "How do you enforce document ACLs in your current RAG stack?"  
- "What’s your standard for citation fidelity and hallucination SLAs?"  
- "Do you evaluate RAG in CI or only manually?"

---

## Quick Links

| Resource | Path |
|----------|------|
| Main README | [README.md](README.md) |
| Security model | [SECURITY.md](SECURITY.md) |
| Architecture notes | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Evaluation script | [backend/evaluate.py](backend/evaluate.py) |
| Prompt safety | [backend/app/core/prompt_safety.py](backend/app/core/prompt_safety.py) |
