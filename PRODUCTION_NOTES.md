# Architecture & Production Notes

## Current Setup

* **Local Environment:** A single docker compose yml file runs both the Django backend and Next.js frontend services for quick setup.
* **Background Processing:** Used Python's built-in ThreadPoolExecutor to handle work item analysis asynchronously. This keeps the backend lightweight and avoids complex external message broker dependencies for local environment.
* **AI Engine:** Implemented an extensible Factory pattern using MockAIservice for fast, deterministic unit testing alongside a local Ollama fallback for offline testing.
* **API:** Swagger API to create work item. /api/swagger/

## Backend Production Improvements

If scaling this system to a production environment, I would implement the following upgrades:

* **Inbound Ingestion Security:** Add HMAC signature validation or API Key authentication to verify incoming payload origin and ensure message authenticity.
* **Robust Background Queues:** Replace ThreadPoolExecutor  with **Celery + Redis** to offload analysis tasks properly.
* **Real-Time UI Updates:** Implement django-eventstream (Server-Sent Events) and Redis Pub/Sub to push real-time background analysis progress directly to the frontend dashboard .
* **Authentication & Access Control:** Add JWT authentication and role-based access for operators and admins reviewing work items.
* **Production Database:** Migrate to managed **PostgreSQL** with connection pooling to cleanly handle high concurrency, row-level locking, and higher data volumes.
* **Dynamic AI Provider Configuration:** Expand backend/frontend settings configurations to allow hot-swapping or configuring active AI providers (e.g  Gemini, OpenAI, Ollama) on the fly without requiring code deployments.
* **Middleware:** Add request IDs, HTTPS settings, trusted hosts, rate limiting, and strict CORS/CSRF rules for the frontend.
* **Request Logging:** Log each requests path, status, response time, and user. Never log passwords, tokens, cookies, or other sensitive data.
* **Application Logging:** Configure Django logging and send the logs to a central place so errors can be monitored and investigated.

## Frontend Production Improvements

* **Production Runtime:** Build the Next.js application with pnpm run build  and run it with pnpm run start instead of pnpm run dev.
* **Frontend Container:** Use a multi-stage Docker build with a minimal runtime image, no source bind mounts, and a non-root user.
* **Reverse Proxy and TLS:** Put the frontend and backend behind a managed reverse proxy with HTTPS, secure headers, request limits, and access logging.
* **Configuration:** Provide the backend URL and other runtime settings through deployment environment variables .
* **Observability:** Add frontend error tracking, structured logs, health checks, and monitoring for failed API requests and slow page loads.
* **Release Safety:** Run linting, type checks, and a production build in CI before deployment, then use rolling or blue-green releases with a rollback path.
