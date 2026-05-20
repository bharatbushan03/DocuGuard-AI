# DocuGuard AI Security Model

This document outlines the security architecture and measures implemented in DocuGuard AI to protect enterprise data and ensure system integrity.

## 1. Authentication & Authorization

### JWT Authentication
- DocuGuard AI uses JSON Web Tokens (JWT) for stateless authentication.
- Tokens are signed with `HS256` and have a default expiration of 24 hours.
- Users must provide their credentials (email/password) to receive a token via the `/auth/login` endpoint.

### Role-Based Access Control (RBAC)
- **Roles:** `admin`, `hr`, `legal`, `employee`, `user`.
- **Enforcement:** Middleware (`require_role`) protects sensitive API endpoints.
- **Document Access:** 
    - `admin` can access all documents.
    - Other roles can only access documents they uploaded or those marked as `public`.

## 2. Data Protection

### File Upload Security
- **Filename Sanitization:** All uploaded files are renamed to a random UUID to prevent path traversal and filename collisions.
- **Storage:** Files are stored in a dedicated `uploads/` directory, which should be protected by server-level permissions.
- **Validation:** File size is capped at 10MB, and MIME types are restricted to PDF, DOCX, TXT, and MD.

### Retrieval-Augmented Generation (RAG) Security
- **Metadata Filtering:** Every query to the vector database (Qdrant) includes a strict filter based on the user's ID and role. This ensures users never retrieve "context" from documents they aren't authorized to see.
- **Prompt Injection Protection:** User questions are clearly delimited within LLM prompts. Explicit system instructions command the model to ignore any instructions embedded within the user's question or the document context.

### Database Security
- **SQL Injection:** All database interactions use the SQLAlchemy ORM, which automatically parameterizes queries to prevent SQL injection.
- **Encryption:** Passwords are hashed using `bcrypt` with a unique salt before storage.

## 3. Network & Infrastructure

### CORS Configuration
- Cross-Origin Resource Sharing (CORS) is restricted to the specific frontend URL (default: `http://localhost:3000`).

### Environment Variables
- Sensitive configurations (OpenAI API keys, Database URLs, JWT Secret) are managed through environment variables.
- Default insecure values are provided for local development but **must** be overridden in production.

## 4. Known Limitations & Future Work

- **Virus Scanning:** Current implementation does not scan uploaded files for malware. It is recommended to add a virus scanning service (e.g., ClamAV) in a production environment.
- **Audit Logging:** While basic query logging is implemented, a comprehensive tamper-proof audit log for all administrative actions is planned for future releases.
- **Rate Limiting:** API rate limiting is not currently implemented and should be added to prevent DoS attacks.
