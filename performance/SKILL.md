---
name: performance
description: Performance optimization for frontend, backend, database, and network. Use when writing, reviewing, or optimizing code for speed and efficiency.
---

# Performance

## Philosophy

Measure first. Optimize bottlenecks, not hunches. Readable code until proven slow.

## When to Optimize

- Don't optimize prematurely — prove it's slow first
- Profile before guessing
- Set performance budgets, measure against them
- If code review suggests deeper work (profiling, RUM, memory analysis, infra scaling, framework-specific tuning) — ask before diving in

## Frontend

**Bundle & Loading:**
- Code split by route — lazy load non-critical paths
- Tree shake unused code
- Keep bundle size in check — monitor growth
- Defer non-critical JS (`defer`, dynamic imports)
- Preload critical assets, prefetch likely next pages

**Rendering:**
- Minimize DOM size and depth
- Avoid layout thrashing — batch DOM reads/writes
- Use CSS for animations over JS where possible
- Virtualize long lists — don't render 1000 items

**Images & Assets:**
- Right format: WebP/AVIF for photos, SVG for icons
- Responsive images (`srcset`)
- Lazy load below-the-fold images
- Compress aggressively

**Caching:**
- Cache static assets with long TTL + hash in filename
- Use service workers for offline/repeat visits where appropriate

*If I spot opportunities for framework-specific optimizations (React.memo, useMemo, etc.), I'll flag and ask.*

## Backend

**General:**
- Async/non-blocking for I/O-bound work
- Parallelize independent operations
- Fail fast — don't do expensive work if early validation fails
- Pagination for large datasets — never unbounded queries

**Query Optimization:**
- Prevent N+1 — batch or eager load
- Select only needed fields — no `SELECT *`
- Push filtering to the database, not application code
- Use query plans to find slow queries

**Connection Management:**
- Use connection pooling
- Set sensible timeouts
- Release connections promptly

**Memory:**
- Watch for leaks: unclosed connections, unbounded caches, event listener buildup
- Stream large payloads — don't load entire files into memory

**Caching:**
- Cache expensive computations and repeated queries
- Cache at the right layer: in-memory, Redis, CDN
- Consider cache-aside vs write-through based on access patterns
- Plan cache invalidation — hardest problem in CS

*If I spot potential memory leaks, scaling concerns, or infra-level bottlenecks, I'll flag and ask.*

## Database

**Indexing:**
- Index columns used in WHERE, JOIN, ORDER BY
- Composite indexes for multi-column queries — order matters
- Don't over-index — writes pay the cost
- Review query plans regularly

**Schema & Queries:**
- Normalize first, denormalize for proven read performance needs
- Avoid expensive operations in hot paths: full table scans, LIKE '%x%', functions on indexed columns
- Use EXPLAIN/ANALYZE to understand query behavior

**Pagination:**
- Cursor-based for large/real-time datasets
- Offset-based OK for small, static datasets
- Never fetch unbounded results

*If I spot schema design issues or migration concerns affecting performance, I'll flag and ask.*

## Network

**Reduce Round Trips:**
- Batch API calls where possible
- GraphQL or BFF pattern to avoid chatty requests
- HTTP/2 for multiplexing

**Compression:**
- Gzip/Brotli for text assets
- Compress API responses

**CDN:**
- Static assets on CDN — close to users
- Consider edge caching for dynamic content where appropriate

**Headers:**
- Cache-Control, ETag for caching
- Keep-Alive for connection reuse

## Caching Strategy

| Layer | Use case |
|-------|----------|
| Browser | Static assets, user-specific data |
| CDN | Static assets, public content |
| Application (in-memory) | Hot data, computed values |
| Distributed (Redis, etc.) | Shared state, sessions, rate limiting |

**Invalidation:**
- TTL-based for simplicity
- Event-based for consistency
- Versioned keys to avoid stale reads

## Measurement

**What to track:**
- Response times (p50, p95, p99)
- Time to first byte (TTFB)
- Largest contentful paint (LCP)
- Database query times
- Cache hit rates

**Tools:**
- Browser devtools (Network, Performance, Lighthouse)
- Backend profilers (language-specific)
- APM tools (Datadog, New Relic, etc.)
- Database query analyzers

**Budgets:**
- Set budgets for bundle size, load time, API response time
- Fail CI on budget breach

*If deeper measurement (RUM, continuous profiling, load testing) would help, I'll flag and ask.*