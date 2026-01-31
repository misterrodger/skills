---
name: security
description: Security best practices for web applications. Use when writing, reviewing, or refactoring code that handles auth, data, APIs, or user input.
---

# Security

## Philosophy

Least privilege. Strict defaults. Trust nothing. Validate everything.

*If I spot auth architecture concerns or security issues beyond code-level fixes, I'll flag and ask before diving in.*

## General Principles

- Secrets out of source code
- Allowlist over blocklist
- Reduce attack surface — eliminate insecure options
- Latest stable versions of runtime and dependencies
- Never run apps with root privileges

## Input Validation

Validate ALL inputs with a tested lib (Zod, Pydantic). Inputs include:
- Client calls, API responses
- Data store responses (DB, cache, search)
- Browser storage (cookies, local/session storage)
- URL params
- Filesystem I/O

Validation layers:
- **Syntactic** — type, format, length
- **Semantic** — logical values, reasonable ranges, start < end
- **Allowlist** — constrain to known valid values where possible

## Data Layer

- Never trust user input — always parameterise/sanitise
- Use ORM / query builder / parameterised queries — no string concatenation
- Confirm no SQL/NoSQL injection vectors
- No unvalidated external input can alter a query

## Frontend

- Use framework tools — no direct DOM manipulation
- Avoid dangerous built-ins: `eval`, `Function()`, `document.write`, `innerHTML`
- No dynamic HTML/JSON building outside framework
- Use framework data binding — no mixed templating or dynamic template generation

## Server-Side

- Every external endpoint is accessible without a browser — duplicate validation client/server
- Whitelist allowed domains, resources, protocols for fetching
- Use lib for HTTP header security (helmet, etc.)
- Set sensible limits on request body size per content type
- Check for default/hard-coded credentials

## Rate Limiting

- Rate limit auth endpoints, APIs, expensive operations
- Fail closed on limit breach

## Error Handling

- Never leak stack traces, internal paths, or DB errors to clients
- Generic messages externally, detailed logs internally

## CORS

- Explicit allowlist of origins
- No wildcard (`*`) in production

## File Uploads

- Validate file type by magic bytes, not just extension
- Limit size
- Store outside webroot
- Scan for malware if possible

## Cryptography

- Don't hand-roll — use established libs
- Hashing: bcrypt, argon2
- Encryption: libsodium
- Random: `crypto.randomUUID`, `crypto.getRandomValues`

## Auth & Sessions

- Don't self-roll auth — use established packages (OAuth, Google Auth, etc.)
- Single auth mechanism everywhere
- Use JWTs with short expiry — validate signature and claims server-side
- Timeout session IDs/tokens — invalidate on logout and at set intervals
- Encrypt passwords in storage and transit
- Use `Secure`, `HttpOnly`, `SameSite` flags on cookies
- Use CSRF tokens / synchroniser pattern — framework should provide
- Authenticate comms between components, APIs, middleware, data layers

## Access Control

Choose the right model:
| Model | Use case |
|-------|----------|
| Attribute-based | User/resource/action attrs (id, location, dept, device, timestamp) |
| Role-based | Student, user, admin — different read/write/network/file access |
| Mandatory | Military-style clearance levels — no read-up, no write-down |
| Discretionary | File-system style — explicit allow/deny per entity |

Enforce at trust points: gateways, servers, serverless functions, DBs.

## Sensitive Data

- Obfuscate PII
- Hide private data (search history, etc.)
- Only return what you need from objects/data sources

## Communications

- TLS (latest) — SSL is dead
- HTTPS everywhere
- Mark cookies as Secure

## Architecture

- **Single mechanisms** — one approach each for auth, authz, logging, exception handling
- **Centralised error handling** — no duplicated try/catch
- **Centralised logging** — common format, synced time, single storage
- **Authenticate between layers** — components, APIs, middleware, data

## Code Review Checklist

- [ ] No secrets in code
- [ ] Inputs validated (all sources incl. filesystem)
- [ ] Parameterised queries
- [ ] No dangerous built-ins (`eval`, `innerHTML`, etc.)
- [ ] Auth/authz enforced at trust points
- [ ] JWTs validated server-side, short expiry
- [ ] Cookies secured (`Secure`, `HttpOnly`, `SameSite`, CSP)
- [ ] Rate limiting on auth and expensive endpoints
- [ ] CORS allowlist — no wildcards
- [ ] File uploads validated (magic bytes, size, storage)
- [ ] Errors don't leak internals
- [ ] HTTPS enforced
- [ ] Logging in place for attack vectors