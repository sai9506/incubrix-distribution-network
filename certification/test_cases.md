# IncuBrix Distribution Network – Certification Test Pack

## 1. Purpose

This test pack verifies the core functionality of the IncuBrix Distribution Network, including connector registration, content validation, publishing, security, and reliability.

All connector integration tests described below use a local mock destination server. They do not represent successful publishing to live third-party platforms.

## 2. Test Environment

| Component | Configuration |
|---|---|
| Operating System | Windows |
| Language | Python 3.13 |
| Backend | FastAPI |
| Database | MySQL 8.4 |
| Container | Docker |
| Testing Framework | Pytest |
| Mock Server | Local FastAPI server |

## 3. Connector Certification Tests

| Test ID | Connector | Test Scenario | Expected Result |
|---|---|---|---|
| CON-01 | Manual | Register manual connector | Connector available |
| CON-02 | Webhook | Send valid HMAC signature | Request accepted |
| CON-03 | Webhook | Send invalid HMAC signature | Request rejected |
| CON-04 | Discourse | Publish test content to mock endpoint | Successful mock response |
| CON-05 | Lemmy | Publish test content to mock endpoint | Successful mock response |
| CON-06 | Dev.to | Publish draft to mock endpoint | Successful mock response |
| CON-07 | Ghost | Create draft through mock endpoint | Successful mock response |

## 4. Posting Rules Tests

| Test ID | Scenario | Expected Result |
|---|---|---|
| RULE-01 | Content within daily posting limit | Allowed |
| RULE-02 | Daily posting limit exceeded | Blocked |
| RULE-03 | Self-promotion without disclosure | Blocked |
| RULE-04 | Self-promotion with disclosure | Allowed |
| RULE-05 | Content exceeding maximum link limit | Blocked |
| RULE-06 | AI-generated content without disclosure | Blocked |
| RULE-07 | AI-generated content with disclosure | Allowed |

## 5. API Tests

| Test ID | Endpoint | Expected Result |
|---|---|---|
| API-01 | GET / | Application running |
| API-02 | GET /health | Healthy response |
| API-03 | GET /ready | Database connected |
| API-04 | GET /api/v1/connectors | Supported connectors listed |
| API-05 | POST /api/v1/publish | Publishing request processed |
| API-06 | POST /api/v1/publish/async | Background job submitted |
| API-07 | GET /api/v1/jobs/{job_id} | Job status returned |

## 6. Reliability and Idempotency Tests

| Test ID | Scenario | Expected Result |
|---|---|---|
| REL-01 | Submit request with an idempotency key | Request processed |
| REL-02 | Repeat request with the same key and payload | Duplicate publishing prevented |
| REL-03 | Reuse idempotency key with different payload | Conflict rejected |
| REL-04 | Temporary network failure | Retry attempted |
| REL-05 | Non-retryable publishing failure | Failure recorded |

## 7. Security Tests

| Test ID | Scenario | Expected Result |
|---|---|---|
| SEC-01 | Valid webhook signature | Accepted |
| SEC-02 | Invalid webhook signature | Rejected |
| SEC-03 | Missing webhook signature | Rejected |
| SEC-04 | Missing connector configuration | Connector validation fails |
| SEC-05 | Environment secrets | Secrets kept outside source code |

## 8. Batch Processing Tests

| Test ID | Scenario | Expected Result |
|---|---|---|
| BAT-01 | Valid batch input | Items processed |
| BAT-02 | AI disclosure missing | Item blocked |
| BAT-03 | Unsupported platform | Item fails |
| BAT-04 | Batch completion | JSON manifest generated |

## 9. Test Execution Summary

The automated Pytest suite was executed successfully.

- Total tests passed: 33
- Failed tests: 0
- Warnings: 1
- Execution time: 0.99 seconds

All automated tests passed.

## 10. Known Limitations

1. Connector integrations were tested against local mock endpoints, not live third-party services.
2. Live platform authentication and publishing permissions have not been verified.
3. The mock destination server stores test posts in memory.
4. Production deployment and real-world community certification remain future work.

## 11. Conclusion

The certification test pack documents the core functional, API, connector, security, and reliability scenarios for the IncuBrix Distribution Network. Automated tests and local mock integration tests provide initial validation of the implementation.
