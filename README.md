# DocuGuard AI Enterprise Assistant

## Tech Stack
- **Frontend**: Next.js (TypeScript, Tailwind CSS)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (via SQLAlchemy)
- **Vector DB**: Qdrant
- **Deployment**: Docker Compose

## Quick Start with Docker

1.  **Configure Environment Variables**:
    Copy `.env.docker` to `.env`:
    ```bash
    cp .env.docker .env
    ```
    Edit `.env` and provide your `OPENAI_API_KEY`.

2.  **Build and Start**:
    ```bash
    docker-compose up --build
    ```

3.  **Setup Database (Migrations)**:
    Once the services are running, apply the database schema:
    ```bash
    docker-compose exec backend alembic upgrade head
    ```

4.  **Seed Initial Data (Optional)**:
    To populate the system with test users and sample logs:
    ```bash
    docker-compose exec backend python seed.py
    ```

### Services Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Development

-   **Backend Hot Reload**: The backend container is configured to sync local changes (excluding `uploads/`) for rapid development.
-   **Persistent Data**: Database records and vector embeddings are persisted in Docker volumes (`postgres_data`, `qdrant_data`).
-   **Logs**: View logs for all services with `docker-compose logs -f`.
