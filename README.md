
# LLM Sandbox

A lightweight **FastAPI chat backend** that integrates with a remote LLM provider and uses **Redis for session-based conversation storage and rate limiting**.

The project demonstrates a modular backend architecture with separate layers for API routes, business logic, persistence, configuration, and LLM integration.

## Architecture

The request flow is:

1. Client sends a prompt with an optional `X-Session-ID`.
2. The API creates or resolves the session.
3. Conversation history is retrieved from Redis.
4. The prompt and history are sent to the configured LLM.
5. The response and user message are stored in Redis.
6. The API returns the session ID and generated response.

```text
app/
├── main.py
├── api/routes/chat.py
├── core/config.py
├── core/rate_limit.py
├── dependencies.py
├── repositories/redis_repository.py
├── services/chat_service.py
├── schemas/chat.py
└── clients/llm_client.py
```

## Features

* Session-isolated conversation history
* Automatic UUID-based session creation
* Redis-backed persistence
* Configurable conversation history limits
* TTL-based cleanup of inactive sessions
* Per-session rate limiting
* Pydantic request validation
* Session deletion endpoint
* Replaceable LLM provider abstraction
* Clean startup and shutdown lifecycle management
* Docker-based deployment

## Safeguards

Requests are validated and limited to prevent excessive resource usage:

* Prompt: **10,000 characters**
* System prompt: **5,000 characters**
* Temperature: **0.0–2.0**
* Rate limit: **10 requests/session/minute**

Requests exceeding the rate limit return **HTTP 429**.

## Configuration

The application is configured through environment variables, including the LLM API key, model, Redis connection, session TTL, history limit, and rate limit.

## Running

```bash
docker compose up --build
```

API: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

### Endpoints

```text
POST   /chat
DELETE /chat/session/{session_id}
GET    /health
```

> **Security:** `X-Session-ID` provides session isolation but is not authentication. Production deployments should use an authentication layer or API gateway.
