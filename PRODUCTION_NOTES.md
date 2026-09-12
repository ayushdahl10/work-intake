*

# Architecture & Production Notes

## Current Setup

* **Local Environment:** A single docker compose yml file runs both the Django backend and Next.js frontend services for quick setup.
* **Background Processing:** Used Python's built-in ThreadPoolExecutor to handle work item analysis asynchronously. This keeps the backend lightweight and avoids complex external message broker dependencies for local environment.
* **AI Engine:** Implemented an extensible Factory pattern using MockAIservice for fast, deterministic unit testing alongside a local Ollama fallback for offline testing.
* **API:** Swagger API to create work item. /api/swagger/

## Production Improvements

If scaling this system to a production environment, I would implement the following upgrades:

* **Inbound Ingestion Security:** Add HMAC signature validation or API Key authentication to verify incoming payload origin and ensure message authenticity.
* **Robust Background Queues:** Replace ThreadPoolExecutor  with **Celery + Redis** to offload analysis tasks properly.
* **Real-Time UI Updates:** Implement django-eventstream (Server-Sent Events) and Redis Pub/Sub to push real-time background analysis progress directly to the frontend dashboard .
* **Authentication & Access Control:** Add JWT authentication and role-based access for operators and admins reviewing work items.
* **Production Database:** Migrate to managed **PostgreSQL** with connection pooling to cleanly handle high concurrency, row-level locking, and higher data volumes.
* **Dynamic AI Provider Configuration:** Expand backend/frontend settings configurations to allow hot-swapping or configuring active AI providers (e.g  Gemini, OpenAI, Ollama) on the fly without requiring code deployments.
