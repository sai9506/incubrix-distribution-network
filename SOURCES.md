
# SOURCES.md

## 1. Project Development Resources

The following technologies and libraries are used in the IncuBrix Distribution Network.

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| SQLAlchemy | Database ORM |
| MySQL | Persistent data storage |
| Pydantic | Request validation |
| HTTPX | HTTP communication with destinations |
| PyJWT | Ghost Admin API token generation |
| python-dotenv | Environment configuration |
| Docker | Local mock server deployment |
| Pytest | Automated testing |

## 2. Platform Integration References

The project implements connector interfaces for the following destinations:

- Discourse API – https://docs.discourse.org/
- Lemmy API – https://join-lemmy.org/api/
- Dev.to API – https://developers.forem.com/api
- Ghost Admin API – https://docs.ghost.org/admin-api/
- HMAC-SHA256 – Python cryptographic library documentation:
  https://docs.python.org/3/library/hmac.html

These references identify the platform APIs and security mechanisms relevant to the connector implementations.

## 3. Python Documentation

- Python: https://docs.python.org/3/
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- HTTPX: https://www.python-httpx.org/
- Pytest: https://docs.pytest.org/
- Docker: https://docs.docker.com/

## 4. Local Testing Resources

The project includes a locally hosted mock destination server.

It provides mock endpoints for:

- Discourse
- Lemmy
- Dev.to
- Ghost
- HMAC-signed webhook

The mock server is used to test request handling and connector behavior without publishing to real external accounts.

## 5. Data and Media Sources

The current implementation uses developer-created test content and local mock responses.

No external community content dataset or real user-generated media dataset is required by the current implementation.

## 6. Licensing and Attribution

Third-party libraries and services remain subject to their respective licenses and terms of use.

No claim is made that the local mock server represents official platform infrastructure or certification.
