---
name: feature-workflow
description: Default workflow for feature development. Use this skill when starting any new feature — it orchestrates all other skills through planning, building, and release.
---

# Feature Workflow

## Philosophy

Plan first. Build in chunks. Test and secure as you go. Harden before release.

**Hotfixes/small patches:** Phases can be abbreviated — ask for approval before skipping steps.

---

## 1. DISCOVER

Before writing code:
- Clarify requirements — ask questions
- Identify edge cases and unknowns
- Break feature into chunks (one behavior or logical unit each)
- Flag anything that needs design decisions or diagrams

---

## 2. BUILD (per chunk)

### Code
Apply these skills while coding:
- **dev-coding-practices** — FP-lite, fail fast, naming, architecture
- **ui-code-quality** — if UI work: components, a11y, state, Storybook

### Test & Secure
Shortly after coding each chunk:
- **test-code-quality** — unit tests for logic, Storybook for components
- **security** — validate inputs, check for vulnerabilities, auth/authz

*Repeat for each chunk until feature is functionally complete.*

---

## 3. FINALIZE (whole feature)

Before release, apply these skills across the entire feature:

- **performance** — profile, optimize bottlenecks, check bundle/query costs
- **observability** — logging, metrics, tracing, dashboards
- **documentation** — README, comments, API docs, PR description
- **release-readiness** — final defensive coding, feature flags, quality scans, rollback plan

---

## 4. RELEASE

- PR with clear description (what/why/how to test)
- Self-review or request review
- Ship

---

## 5. POST-RELEASE

Remind to:
- **Monitor** — watch dashboards, logs, alerts for anomalies
- **Rollback plan ready** — feature flag off, revert deploy if needed
- Confirm metrics are tracking as expected

---

## Skill Reference

| Phase | Skills |
|-------|--------|
| Discover | — |
| Build (code) | dev-coding-practices, ui-code-quality |
| Build (test/secure) | test-code-quality, security |
| Finalize | performance, observability, documentation, release-readiness |
| Post-release | (monitoring, rollback) |