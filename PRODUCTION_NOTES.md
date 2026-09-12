# Architecture 


* **Background Processing:** Used Python's built-in `ThreadPoolExecutor`.
  * *Why:* It processes tasks in background without requiring candidates  to run heavy third-party message brokers like Celery or Redis.
* **AI:** Implemented a Provider/Factory pattern with a `MockAIService` and local `Ollama`.
  * *Why:* Tests run instantly without network overhead or API cost, while keeping the system ready for real LLM integration.
