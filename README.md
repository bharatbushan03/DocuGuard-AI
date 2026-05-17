# DocuGuard AI Enterprise Assistant

## Tech Stack
- **Frontend**: Next.js (TypeScript, Tailwind CSS)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (via SQLAlchemy)
- **Vector DB**: Qdrant
- **Deployment**: Docker Compose

## Quick Start

1. Copy `.env.example` to `.env` in the root directory.
2. Ensure you have Docker and Docker Compose installed.
3. Run `docker-compose up --build` to start all services.

### Services Overview
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Qdrant**: localhost:6333

### Development
- The backend is set to reload on code changes.
- Ensure to run Alembic migrations in the backend for DB setup:
  `cd backend && alembic upgrade head`
