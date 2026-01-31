---
name: observability
description: Logging, exception handling, tracing, monitoring, and metrics. Use when implementing or reviewing observability concerns in any application.
---

# Observability

## Philosophy

Centralise everything. Log what matters. Never log secrets. Fail securely.

*If I spot observability architecture concerns (tracing infrastructure, log aggregation strategy, alerting design), I'll flag and ask before diving in.*

## Architecture

- Single mechanism for logging, exception handling, tracing
- No logging/exception handling sprinkled throughout — centralise it
- Minimal instrumentation in business logic — prefer decorators, wrappers, or aspect-oriented approach
- Consistent format across all components
- Synced time across all services
- Use established tools: Kibana, Grafana, Datadog, etc.

## Exception Handling

- Validate inputs/outputs
- Fail securely under expected AND unexpected circumstances
- Use standard HTTP response codes
- Generalise user-facing codes and messages — detailed logs internally

## What to Log

**Always log:**
- Input/output validation failures
- Auth success AND failure (logins, failed logins)
- Authorization (access control) failures
- Server-side validation failures
- Session management failures
- App exceptions and system events (especially API, DB)
- App/system startups and shutdowns
- Higher-risk operations (large transactions, admin actions)
- Legal and consent opt-ins
- Circuit breaker state changes (open/closed/half-open)

**Never log:**

See also: **security** skill for sensitive data handling.

- Source code
- Session IDs, access tokens, JWTs
- DB connection strings, encryption keys, passwords, secrets
- PII, bank accounts, cardholder data
- Data above the logger's auth level
- Business secrets
- Data illegal to collect in jurisdiction
- Data user hasn't consented to

## Structured Logging

- Use structured formats (JSON) over plain text
- Enables querying, filtering, aggregation
- Consistent schema across services

## Log Levels

Use consistently:
| Level | When |
|-------|------|
| ERROR | Action needed — something broke |
| WARN | Investigate — potential issue |
| INFO | Business events — normal operations |
| DEBUG | Dev only — off in prod |

## Log Content

Each log entry should include:
- Timestamp (consistent across components)
- App ID, service name, code location
- Trace ID / correlation ID
- Source address, user ID (if available)
- Event type, severity, security relevance
- Geolocation, page/form/window (where relevant)

## Log Security

- Sanitise user input before logging
- Validate log content — prevent injection/forging attacks
- No dangerous characters in log output

## Where to Log

| Environment | Approach |
|-------------|----------|
| Dev | Filesystem OK — delete regularly |
| Production | SIEM (Security Info & Event Management) — centralised, secure |
| Alternative | Dedicated DB with restrictive permissions |

Forward logs from distributed systems to central storage.

## Retention & Cost

- Define retention policy per environment
- Comply with legal requirements
- Auto-purge old logs
- High-cardinality labels cost money at scale — log what you'll actually use

## Tracing

- Generate correlation ID at entry point, propagate through all layers
- Use trace IDs across service boundaries
- Correlate logs, metrics, traces for debugging
- Instrument at trust points: API calls, DB queries, external services

## Sampling

- For high-volume systems, sample traces/logs intelligently
- 100% capture on errors
- Sample success paths

## Metrics

**Performance/telemetry:**
- Response times, latency percentiles
- Throughput, request rates
- Error rates by type/endpoint
- Resource usage (CPU, memory, connections)

**Business metrics:**
- User actions, conversions, funnel steps
- Feature usage
- Domain-specific KPIs

Instrument early. Decide what matters, measure it, alert on it.

## Health Checks

- Expose `/health` and `/ready` endpoints
- Health = alive
- Ready = can serve traffic
- Separate concerns

## Circuit Breakers

- Log state changes (open/closed/half-open)
- Alert on repeated failures to downstream services

## Monitoring & Alerts

- Set sensible thresholds — avoid alert fatigue
- Alert on anomalies, not just thresholds
- Runbooks for common alerts
- Dashboard for real-time visibility