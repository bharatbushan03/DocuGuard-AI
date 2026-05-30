# DocuGuard AI: Enterprise Knowledge & Compliance Assistant
## Architecture & Implementation Plan

### 1. Folder Structure
```
DocuGuard-AI/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # API router and endpoints
│   │   ├── core/             # Configuration, security, and DB setup
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic (RAG, ingestion, risk)
│   │   │   ├── ingestion/    # PyMuPDF, python-docx parsers
│   │   │   ├── llm/          # OpenAI API integrations
│   │   │   └── vector_db/    # Qdrant integrations
│   │   └── utils/            # Helper functions
│   ├── tests/                # Pytest unit and integration tests
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Backend container definition
├── frontend/                 # Next.js Application
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # Reusable UI components (React/Tailwind)
│   │   ├── hooks/            # Custom React hooks (e.g., useChat, useUpload)
│   │   ├── lib/              # Utility functions, API client
│   │   └── types/            # TypeScript interfaces
│   ├── package.json          # Node dependencies
│   ├── tailwind.config.ts    # Tailwind CSS config
│   └── Dockerfile            # Frontend container definition
├── docker-compose.yml        # Multi-container orchestration
└── README.md                 # Project documentation
```

### 2. Backend Modules
- **API Layer (`app/api`)**: Handles HTTP requests, input validation, and route definitions.
- **Ingestion Module (`app/services/ingestion`)**: Handles file uploads, extracts text using PyMuPDF (PDFs) and python-docx (DOCX), processes TXT/Markdown, and chunks the text using semantic or character-based splitting.
- **Vector DB Service (`app/services/vector_db`)**: Manages communication with Qdrant, including creating collections, upserting chunks with metadata, and performing similarity searches.
- **LLM/RAG Service (`app/services/llm`)**: Integrates with the OpenAI-compatible API to generate embeddings for chunks, build prompts with retrieved context, and structure the final response with citations and confidence scores.
- **Risk Classification Service (`app/services/risk`)**: Analyzes document contents during ingestion to classify risk (e.g., PII detection, confidential data flags).
- **Database Layer (`app/models` & `app/core`)**: PostgreSQL integration via SQLAlchemy and Alembic for migrations, storing document metadata, user info, and chat history.

### 3. Frontend Pages
- **`/` (Dashboard)**: Overview of uploaded documents, system status, and recent queries.
- **`/documents`**: Document management interface to upload, view processing status, and delete files.
- **`/chat`**: The main chat interface where users ask questions, view AI responses, and see citations/confidence scores.
- **`/settings`**: User preferences, API key configuration (if applicable), and system settings.

### 4. Database Schema (PostgreSQL)
- **Users**: `id`, `email`, `password_hash`, `role`, `created_at`
- **Documents**: `id`, `filename`, `file_type`, `upload_status` (Pending, Processing, Completed, Failed), `risk_level` (Low, Medium, High), `uploaded_by` (User ID), `created_at`
- **ChatSessions**: `id`, `user_id`, `title`, `created_at`
- **Messages**: `id`, `session_id`, `role` (user/assistant), `content`, `citations` (JSON), `confidence_score` (Float), `created_at`

### 5. API Endpoints
- `POST /api/v1/documents/upload`: Upload files for processing.
- `GET /api/v1/documents/`: List all documents with their status and risk level.
- `DELETE /api/v1/documents/{id}`: Delete a document and its associated vector embeddings.
- `POST /api/v1/chat/completions`: Send a query, returns RAG response, citations, confidence score, and risk alerts.
- `GET /api/v1/chat/history`: Fetch chat sessions and messages.

### 6. RAG Pipeline
1. **Query Formulation**: User submits a question.
2. **Embedding**: The query is embedded using the OpenAI-compatible embedding model.
3. **Retrieval**: Qdrant performs a similarity search to find the top-k relevant document chunks.
4. **Context Assembly**: Retrieved chunks are assembled into a prompt context, alongside their metadata (source document, page number, chunk ID).
5. **Generation**: The LLM generates an answer based *only* on the provided context, instructed to cite sources using chunk IDs.
6. **Post-processing**: The response is parsed to extract citations, calculate an overall confidence score based on chunk relevance and prompt instructions, and format the output.

### 7. Document Ingestion Flow
1. **Upload**: User uploads a file via the frontend.
2. **Storage**: DB record created with "Processing" status.
3. **Parsing**: PyMuPDF or python-docx extracts text and structural metadata (pages, headings).
4. **Chunking**: Text is split into overlapping chunks (e.g., 500 tokens with 50 token overlap).
5. **Risk Classification**: Chunks are analyzed for sensitive data to determine the document's risk level.
6. **Embedding**: Chunks are converted to vector embeddings.
7. **Indexing**: Embeddings and metadata are upserted into Qdrant.
8. **Completion**: DB record updated to "Completed".

### 8. Risk Classification Logic
- Runs asynchronously during document ingestion.
- Uses pattern matching (Regex for SSNs, credit cards) and/or a smaller specialized LLM prompt to detect PII, financial data, or confidential keywords.
- Assigns a score to chunks. The document's overall risk level (Low, Medium, High) is aggregated from its chunks.
- High-risk documents may trigger access controls or warning flags in the UI.

### 9. Citation System
- Every indexed chunk in Qdrant contains metadata: `document_id`, `filename`, `page_number`, and a unique `chunk_id`.
- The LLM is prompted: "Answer the question using the provided context. When stating a fact, cite the source using the format [chunk_id]."
- The backend parses the LLM output, maps `[chunk_id]` back to the actual document and page, and returns a structured list of references alongside the text.
- The frontend renders these as clickable tooltips or footnotes linking to the original document.

### 11. Security Layer Details
- **Input Sanitization**: All user queries are stripped of HTML tags and control characters.
- **Rate Limiting**: (Planned) Implement Redis-based rate limiting per API key.
- **Audit Logging**: Every RAG transaction is logged with its risk score.

### 10. Development Milestones
- **Phase 1: Foundation (Week 1)**
  - Setup Docker Compose with PostgreSQL and Qdrant.
  - Initialize FastAPI backend and Next.js frontend projects.
  - Implement database schema and basic CRUD endpoints.
- **Phase 2: Ingestion & Vector DB (Week 2)**
  - Implement PyMuPDF and python-docx parsers.
  - Build text chunking and embedding logic.
  - Integrate Qdrant for storing and retrieving vectors.
- **Phase 3: RAG & Chat API (Week 3)**
  - Develop the RAG pipeline (Retrieval + LLM generation).
  - Implement citation parsing and confidence scoring.
  - Build the Risk Classification logic.
- **Phase 4: Frontend Integration (Week 4)**
  - Build the Chat interface and Document management dashboard.
  - Connect frontend to FastAPI endpoints.
  - Polish UI/UX with Tailwind CSS and handle loading states/errors.
- **Phase 5: Refinement & Deployment (Week 5)**
  - Testing (Unit tests for parsing/RAG, integration tests).
  - Finalize Dockerfiles for production deployment.
  - Documentation and handover.
