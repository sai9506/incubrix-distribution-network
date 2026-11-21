# IncuBrix – Long-Tail Destination Distribution Network

## 1. Project Overview

The IncuBrix Distribution Network is a Python-based service designed to distribute content across multiple publishing destinations.

It provides a unified API for managing publishing requests, validating posting rules, connecting to different platforms, and tracking publishing jobs.

The system supports six connector types:

- Discourse
- Lemmy
- Dev.to
- Ghost
- HMAC-Signed Webhook
- Assisted Manual Publishing

Local mock destination endpoints are used to test publishing workflows without posting content to real external platforms.

## 2. Key Features

- Multi-platform connector architecture
- Centralized publishing API
- Configurable destination credentials
- Posting frequency limits
- Self-promotion disclosure validation
- AI-generated content disclosure validation
- Link count validation
- Synchronous publishing
- Asynchronous background jobs
- Idempotency protection
- Automatic retry handling
- Structured API errors
- HMAC-SHA256 webhook signature verification
- Batch publishing runner
- JSON output manifest
- Local mock destination server
- S3-compatible object storage integration
- File upload and listing endpoints
- Health and readiness endpoints
- OpenAPI documentation
- Structured JSON application logging

## 3. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python 3.13 |
| API Framework | FastAPI |
| Database | MySQL 8.4 |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| HTTP Client | HTTPX |
| Authentication | PyJWT |
| Webhook Signature | HMAC-SHA256 |
| Object Storage | S3-compatible storage (Silo) |
| Storage SDK | MinIO Python SDK |
| Containerization | Docker |
| Testing | Pytest |
| Background Processing | FastAPI BackgroundTasks |
| API Specification | OpenAPI 3.1 |

## 4. Architecture

The application follows a modular architecture.

1. API Layer – receives publishing requests and exposes REST endpoints.
2. Rules Engine – validates content and posting restrictions.
3. Publishing Service – coordinates publishing operations.
4. Connector Registry – selects the appropriate destination connector.
5. Connector Layer – communicates with publishing platforms.
6. Database Layer – stores publishing logs and job information.
7. Background Processing – handles asynchronous jobs and retries.
8. Batch Runner – processes multiple publishing requests and generates a manifest.
9. Object Storage Layer – manages uploaded files through an S3-compatible storage service.

## 5. Supported Connectors

| Connector | Purpose |
|---|---|
| Discourse | Community discussion publishing |
| Lemmy | Federated community publishing |
| Dev.to | Developer article publishing |
| Ghost | Blog publishing |
| Webhook | Custom HMAC-signed integration |
| Manual | Assisted publishing workflow |

Local mock endpoints are used for integration testing. These tests do not represent publishing to live external accounts.

## 6. API Endpoints

Base path: `/api/v1`

### Publishing endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/connectors` | List registered connectors |
| POST | `/api/v1/publish` | Publish synchronously |
| POST | `/api/v1/publish/async` | Submit background publishing job |
| GET | `/api/v1/jobs/{job_id}` | Retrieve job status |

### Storage endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/storage/upload` | Upload a file to object storage |
| GET | `/api/v1/storage/files` | List stored files |

### Health endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Health check |
| GET | `/ready` | Database readiness check |

Interactive API documentation:

`http://127.0.0.1:8000/docs`

OpenAPI specification:

`openapi.yaml`

## 7. Project Setup

### Requirements

- Python 3.13
- MySQL 8.4
- Docker Desktop
- Git

### Step 1: Clone the repository

```powershell
git clone <YOUR_REPOSITORY_URL>
cd IncuBrix-Distribution
```

### Step 2: Create a virtual environment

```powershell
python -m venv venv
```

### Step 3: Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 5: Configure environment

Create a `.env` file in the project root.

Configure the following environment variables using your own local credentials:

**Database configuration**

- `DATABASE_URL`

**Webhook configuration**

- `WEBHOOK_URL`
- `WEBHOOK_SECRET`

**Discourse configuration**

- `DISCOURSE_URL`
- `DISCOURSE_API_KEY`
- `DISCOURSE_USERNAME`

**Lemmy configuration**

- `LEMMY_URL`
- `LEMMY_AUTH_TOKEN`
- `LEMMY_COMMUNITY_ID`

**Dev.to configuration**

- `DEVTO_API_KEY`
- `DEVTO_URL`

**Ghost configuration**

- `GHOST_URL`
- `GHOST_ADMIN_API_KEY`

**Object storage configuration**

- `MINIO_ENDPOINT`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`
- `MINIO_BUCKET`
- `MINIO_SECURE`

Use local test credentials where required. Never commit real credentials or secrets to version control.

### Step 6: Initialize the database

```powershell
python -m app.database.init_db
```

### Step 7: Start local services

```powershell
docker compose up --build -d
```

This starts the local mock destination server and S3-compatible storage service.

Local service addresses:

- Mock destination server: `http://localhost:9000`
- Storage console: `http://localhost:9001`
- Storage API endpoint: `http://localhost:9002`

### Step 8: Start the application

```powershell
uvicorn app.main:app --reload
```

API documentation:

`http://127.0.0.1:8000/docs`

Health check:

`http://127.0.0.1:8000/health`

Readiness check:

`http://127.0.0.1:8000/ready`

## 8. Batch Processing

Batch requests are provided through:

`batch_input.json`

Run:

```powershell
python scripts/batch_runner.py
```

The runner processes the requests and generates:

`output/batch_manifest.json`

The manifest contains:

- Total requests
- Successful requests
- Blocked requests
- Failed requests
- Individual publishing results

Publishing defaults to preview mode unless explicitly configured otherwise.

## 9. Object Storage

The application integrates with an S3-compatible storage service.

The storage module supports:

- Bucket creation and verification
- File uploads
- File downloads
- Listing stored objects

The storage API provides:

- `POST /api/v1/storage/upload`
- `GET /api/v1/storage/files`

Storage credentials and endpoint configuration are supplied through environment variables.

## 10. Security and Reliability

- Secrets are read from environment configuration.
- Webhook requests are verified using HMAC-SHA256.
- Invalid webhook signatures are rejected.
- Idempotency keys prevent duplicate request processing.
- Request hashes detect reuse of an idempotency key with different content.
- Retry logic handles selected temporary publishing failures.
- Database errors return structured responses.
- Local mock publishing is used for safe testing.
- Object storage access uses configured credentials.

## 11. Testing

Run the complete test suite:

```powershell
pytest -q
```

**Latest observed test result: 37 passed, 1 warning.**

The test suite covers:

- Connector registration and configuration
- Publishing functionality
- Posting rule validation
- Synchronous and asynchronous publishing
- Background job processing and retry handling
- Idempotency and duplicate request handling
- API error responses
- Storage API functionality

The test run reported one Starlette deprecation warning related to the test environment.

## 12. Current Limitations

- Platform integrations have been tested against local mock endpoints, not live external accounts.
- The mock destination server stores requests in memory.
- Background jobs currently use FastAPI BackgroundTasks rather than a persistent external queue.
- Local testing credentials are not production credentials.
- Production deployment and live destination certification have not been demonstrated.
- Object storage has been tested locally; production storage deployment has not been demonstrated.

## 13. Future Improvements

- Persistent background job queue
- Production deployment
- Persistent mock destination storage
- Live platform certification
- Enhanced destination analytics
- Improved batch scheduling and monitoring
- Production observability and metrics

## 14. Project Status

The project includes the core connector architecture, posting rules, API endpoints, database logging, background processing, idempotency handling, retry logic, webhook signature verification, batch processing, and object storage integration.

The automated test suite currently reports 37 passing tests.

Platform integrations have been exercised against local mock endpoints. Live external publishing and production deployment remain future enhancements.