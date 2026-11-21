# IncuBrix – Long-Tail Destination Distribution Network

## 1. Executive Summary

The IncuBrix Long-Tail Destination Distribution Network is a Python-based application designed to distribute content across multiple publishing destinations through a unified API.

The system uses a modular connector architecture, a centralized publishing service, configurable posting rules, database logging, asynchronous job processing, object storage, and batch execution.

The implementation includes six connector types: Discourse, Lemmy, Dev.to, Ghost, HMAC-signed Webhook, and Assisted Manual Publishing.

Local mock destination endpoints are used to test publishing workflows without posting content to real external platforms.

## 2. Problem Statement

Content creators and organizations may need to distribute content across multiple online destinations. Managing different platform integrations separately can increase development effort and make publishing workflows difficult to maintain.

The proposed solution provides a common interface for submitting content, validating publishing requirements, selecting destinations, and tracking publishing results.

## 3. Project Objectives

- Develop a unified content distribution API.
- Support multiple destination connectors.
- Implement configurable posting rules.
- Prevent duplicate publishing requests using idempotency keys.
- Support synchronous and asynchronous publishing.
- Handle temporary failures using retry logic.
- Provide batch publishing capabilities.
- Generate output manifests for batch execution.
- Protect webhook integrations using HMAC-SHA256 verification.
- Support file uploads and object storage.
- Provide local testing without publishing to real communities.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API framework |
| MySQL | Persistent database |
| SQLAlchemy | Database ORM |
| Pydantic | Request validation |
| HTTPX | HTTP requests |
| PyJWT | Ghost authentication token generation |
| Docker | Local mock server and storage service |
| S3-compatible object storage | File storage |
| MinIO Python SDK | Object storage integration |
| Pytest | Automated testing |
| PowerShell | Local development and verification |

## 5. System Architecture

The application is divided into the following components.

### 5.1 API Layer

The FastAPI application exposes endpoints for connector discovery, synchronous publishing, asynchronous publishing, job-status retrieval, and file storage operations.

### 5.2 Connector Registry

The registry stores the available connector instances and selects a connector based on the requested platform.

### 5.3 Posting Rules Engine

The rules engine validates content before publishing.

Implemented checks include:

- Maximum three successful posts per platform per day.
- Self-promotion disclosure requirement.
- Maximum five links in the content body.
- AI-generated content disclosure requirement.

### 5.4 Publishing Service

The publishing service coordinates rule validation, connector selection, configuration validation, preview mode, and publishing execution.

### 5.5 Database Layer

MySQL and SQLAlchemy are used to store:

- Destination configuration records.
- Publishing logs.
- Publishing jobs.
- Idempotency keys and request hashes.
- Publishing results and job status.

### 5.6 Background Processing

FastAPI BackgroundTasks is used to process asynchronous publishing requests.

The current implementation includes retry handling for selected temporary network and HTTP failures.

### 5.7 Batch Runner

The batch runner reads requests from `batch_input.json`, processes each item, and generates a JSON output manifest.

### 5.8 Object Storage

An S3-compatible object storage service is integrated for storing uploaded files.

The application provides an upload endpoint and a file-listing endpoint. Uploaded files are stored in the configured storage bucket.

## 6. Connector Implementation

The system includes six connector types.

| Connector | Implementation |
|---|---|
| Discourse | Sends publishing requests to the posts endpoint |
| Lemmy | Sends post requests to the Lemmy API endpoint |
| Dev.to | Sends article creation requests |
| Ghost | Generates an Admin API JWT and submits a draft |
| Webhook | Sends JSON with an HMAC-SHA256 signature |
| Manual | Prepares content for manual publishing |

The platform connectors have been exercised against a local mock destination server. Live external account publishing has not yet been demonstrated.

## 7. API Endpoints

The API uses the `/api/v1/` prefix.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/connectors` | List available connectors |
| POST | `/api/v1/publish` | Submit synchronous publishing request |
| POST | `/api/v1/publish/async` | Submit background publishing job |
| GET | `/api/v1/jobs/{job_id}` | Retrieve job status |
| POST | `/api/v1/storage/upload` | Upload a file to object storage |
| GET | `/api/v1/storage/files` | List stored files |
| GET | `/health` | Application health check |
| GET | `/ready` | Database readiness check |

Interactive API documentation is available through FastAPI Swagger UI at `/docs`.

## 8. Reliability and Security

### 8.1 Idempotency

The application accepts an `Idempotency-Key` header. Request hashes are used to identify repeated requests and detect reuse of a key with different content.

Repeated requests with the same key and content return the existing publishing result or job instead of creating another publishing operation.

### 8.2 Retry Handling

The background processor retries selected temporary network failures and retryable HTTP status codes, with an exponential delay.

### 8.3 Webhook Verification

The webhook connector generates an HMAC-SHA256 signature using a shared secret.

The mock destination server independently verifies the signature and rejects invalid signatures.

The secret is supplied through environment configuration rather than being hardcoded in the mock server source.

### 8.4 Safe Testing

Publishing requests default to preview mode. Local mock endpoints are used for integration testing, avoiding unintended publication to real communities.

### 8.5 Object Storage

Storage credentials and connection settings are supplied through environment configuration. The application uses the configured S3-compatible storage endpoint for file operations.

## 9. Implementation and Test Evidence

The following checks have been performed during development.

| Feature | Observed result |
|---|---|
| MySQL connection | Successful |
| Database readiness endpoint | Ready |
| Discourse mock connector | Successful |
| Lemmy mock connector | Successful |
| Ghost mock connector | Successful |
| Dev.to mock connector | Successful |
| Webhook mock connector | Successful |
| Valid webhook signature | HTTP 200 |
| Invalid webhook signature | HTTP 401 |
| Connector discovery endpoint | All six connectors returned |
| Batch runner | Three requests processed |
| Batch preview results | Two successful previews |
| Posting rule validation | One AI disclosure request blocked |
| Object storage integration | Test passed |
| Automated test suite | 37 tests passed |

### Batch Runner Result

The test input contained three requests:

- First request: preview successful.
- Second request: preview successful.
- Third request: blocked because the required AI disclosure was missing.

Observed batch summary:

| Metric | Result |
|---|---:|
| Total requests | 3 |
| Successful previews | 2 |
| Blocked requests | 1 |
| Failed requests | 0 |

The output manifest was generated at:

`output/batch_manifest.json`

### Automated Tests

The project uses Pytest for automated testing.

**Final observed result: 37 passed, 1 warning.**

The automated test suite covers:

- Connector registration and configuration.
- Publishing functionality.
- Content validation and posting rules.
- Synchronous and asynchronous publishing.
- Background job processing and retry handling.
- Idempotency and duplicate request handling.
- API error responses.
- Object storage API functionality.

The test run reported one Starlette deprecation warning related to the test environment.

## 10. Limitations

- Destination integrations have been tested using local mock endpoints, not live platform accounts.
- The mock server stores published test records in memory; restarting the container clears them.
- Background processing currently uses FastAPI BackgroundTasks rather than a persistent message queue.
- Production deployment and live destination certification have not been demonstrated.
- The batch runner currently uses a local service call and does not provide a persistent distributed batch scheduler.
- Object storage integration has been tested locally; production storage deployment has not been demonstrated.

## 11. Future Enhancements

- Integrate a persistent background queue.
- Add persistent storage for mock destination records.
- Improve batch scheduling and monitoring.
- Add more comprehensive integration and failure-recovery tests.
- Complete live platform integration testing with authorized accounts.
- Improve observability through structured logs and metrics.
- Add production deployment and operational monitoring.

## 12. Conclusion

The IncuBrix Distribution Network establishes a modular foundation for multi-destination content distribution.

The implementation brings together connector registration, posting-rule validation, synchronous and asynchronous publishing, idempotency, retry handling, webhook signature verification, database persistence, object storage, and batch processing.

Local mock integration tests provide a safe way to exercise the connector workflows. The automated test suite currently reports 37 passing tests. Further work is required for live platform validation, production deployment, and persistent background processing.