# DocuGuard AI — Security Model

This document describes how DocuGuard AI protects enterprise documents, user data, and AI interactions. It reflects the **implemented** controls in this repository.

## Threat model (summary)

| Threat | Mitigation |
|--------|------------|
| Privilege escalation at registration | Roles are server-assigned (`user` only); clients cannot set `role` |
| Unauthorized document access | ORM filters + per-document checks + Qdrant metadata filters |
| Cross-user chat session access | Session ownership verified before read/write |
| Prompt injection (direct) | Delimiters, sanitization, system rules, JSON-only output |
| Prompt injection (indirect, via uploads) | Context treated as untrusted data; chunk sanitization |
| Sensitive chunk leakage to clients | API returns metadata + short previews only |
| JWT forgery / weak secrets | HS256 + production validation of `SECRET_KEY` |
| File upload malware / spoofing | Magic-byte validation, size limits, UUID storage paths |
| Open Qdrant/Postgres on LAN | Docker binds DB/vector ports to `127.0.0.1` only |
| SQL injection | SQLAlchemy ORM (parameterized queries) |
| Over-broad CORS | Explicit origins, limited methods/headers |

## 1. Authentication & JWT

- **Mechanism:** OAuth2 password flow → JWT (`HS256`), subject = user ID.
- **Token lifetime:** Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 24h).
- **Login response** includes `role` from the database (not client-supplied).
- **Production:** Set `APP_ENV=production` and a `SECRET_KEY` of at least 32 random characters. Startup validation rejects known insecure defaults.

```bash
# Required in production
APP_ENV=production
SECRET_KEY=<openssl rand -hex 32>
OPENAI_API_KEY=sk-...
```

**Limitations:** No refresh tokens, revocation list, or MFA (planned hardening).

## 2. Role-based access control (RBAC)

| Role | Upload documents | View all documents | Admin dashboard |
|------|------------------|--------------------|-----------------|
| `admin` | Yes | Yes | Yes |
| `hr`, `legal`, `employee` | Yes | Own + `public` only | No |
| `user` | No | Own + `public` only | No |

- Enforced via `require_role()` on routes.
- **Registration** always creates `user` role (`backend/app/crud/crud_user.py`).
- Elevated roles must be assigned by an administrator (DB/seed), not via the public API.

## 3. Document access control

**PostgreSQL (listing & detail):**

- Admins: all documents.
- Others: `uploaded_by == user.id` OR `access_level == "public"`.

**Qdrant (RAG retrieval):**

- Admins: unfiltered search.
- Others: filter `should` match `access_level=public` OR `uploaded_by=user_id`.

**Access levels:** `private` (default), `public`. Levels like `internal` / `confidential` are reserved for future policy engines.

## 4. File upload security

| Control | Implementation |
|---------|----------------|
| Max size | 10 MB |
| Allowed types | PDF, DOCX, TXT, MD |
| Type verification | Magic-byte / UTF-8 validation (`app/core/file_validation.py`) — not client `Content-Type` alone |
| Storage path | UUID filename under `uploads/` |
| PDF limits | Max 500 pages |
| Virus scan | **Not implemented** — add ClamAV or cloud scanning in production |

## 5. Prompt injection & RAG safety

Implementation: `backend/app/core/prompt_safety.py`, orchestrated in `chat_service.py`.

**Pipeline order (security-critical):**

1. Sanitize + detect user query  
2. Validate chat session ownership (**before** retrieval or LLM)  
3. Embed query → retrieve chunks (Qdrant RBAC filter)  
4. Sanitize + detect each document chunk  
5. Build system/user prompts with warnings  
6. Call LLM  

**Detected attack categories (neutralized with `[filtered]`, request continues safely):**

| Category | Example |
|----------|---------|
| `ignore_instructions` | "Ignore previous instructions" |
| `reveal_system_prompt` | "Reveal system prompt" |
| `confidential_exfiltration` | "Return all confidential documents" |
| `bypass_access_control` | "Bypass access control" |
| `no_citations` | "Do not cite sources" |
| `role_override` | "You are now admin" |
| `delimiter_escape` | Fake `--- END CONTEXT ---` markers |

**Direct injection (user question):** Length cap, pattern detection, delimiter stripping, explicit system rules.

**Indirect injection (document content):** Retrieved text wrapped in `UNTRUSTED_REFERENCE_DATA` with a warning block; chunks sanitized before prompts; model told never to obey embedded commands.

**On detection:** `injection_detected=true`, `injection_categories` in API response, `requires_human_review` elevated; malicious phrases replaced—not executed.

**Defense in depth:** Citation verification, risk classification, confidence scoring, human-review flags.

**Tests:** `backend/tests/test_prompt_injection.py`

## 6. Sensitive data in responses & logs

| Surface | Policy |
|---------|--------|
| Chat API `retrieved_chunks` | Metadata + `content_preview` (≤120 chars), no full chunk bodies |
| Query logs (DB) | Chunk metadata only (no full content) |
| Admin log APIs | Redacted chunk payloads, capped at 200 rows |
| Application logs | User IDs and error types; no passwords, tokens, or full document text |

## 7. Chat session isolation

- Each `session_id` must belong to `current_user.id`.
- Invalid or foreign sessions return **403 Forbidden**.

## 8. CORS

- Origins from `BACKEND_CORS_ORIGINS` (JSON array or comma-separated).
- Methods: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`.
- Headers: `Authorization`, `Content-Type`, `Accept`.
- Credentials enabled for cookie-based frontend auth.

## 9. Environment variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | JWT signing |
| `OPENAI_API_KEY` | Embeddings & chat |
| `POSTGRES_*` | Database |
| `QDRANT_URL` | Vector store (internal Docker network) |
| `BACKEND_CORS_ORIGINS` | Allowed browser origins |
| `APP_ENV` | `development` \| `production` (enables secret validation) |
| `ALLOW_PUBLIC_REGISTRATION` | Disable open signup when `false` |

Never commit `.env` files. Use `.env.docker` as a template only.

## 10. Infrastructure (Docker)

- **Postgres** and **Qdrant** published on `127.0.0.1` only — not exposed on all interfaces.
- **Qdrant** has no application-level API key; network isolation is required.
- Uploads use the `docuguard_uploads_data` volume.

## 11. SQL injection

All application queries use SQLAlchemy ORM. No dynamic SQL concatenation in route handlers.

## 12. Dependencies

- Backend: pinned ranges in `backend/requirements.txt`.
- Frontend: pinned in `package.json` / lockfile.
- Run `pip audit` and `npm audit` before production releases.

## 13. Reporting vulnerabilities

If you discover a security issue, report it privately to the repository maintainers. Do not open public issues for undisclosed vulnerabilities.

## 14. Known gaps & roadmap

- [ ] API rate limiting
- [ ] Malware scanning on upload
- [ ] JWT refresh + revocation
- [ ] MFA for admin accounts
- [ ] Qdrant API key / mTLS
- [ ] Tamper-evident audit logging
- [ ] Automated dependency scanning in CI
# Maintenance commit 3
