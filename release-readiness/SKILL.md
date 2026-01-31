---
name: release-readiness
description: Final checks before release — defensive coding, metrics, feature flags, quality scans. Use when completing a feature or preparing for production release.
---

# Release Readiness

## Philosophy

Last line of defense. Validate everything upstream first. Then harden minimally.

## Final Defensive Coding

- Only now add exception handling or defensive code — after exhausting upstream fixes
- Keep it minimal — don't over-engineer

## Business Metrics

- Confirm whether business metrics are appropriate for this feature
- User actions, conversions, feature usage, domain KPIs

## Release Strategy

- Ask: feature flag for gradual rollout?
- Ask: A/B experiment needed?
- Document rollback plan: feature flag off, revert deploy, data considerations

## Dashboards

- Remind to create/update dashboards
- Print summary of available data to connect:
  - Logs, traces, metrics endpoints
  - Business events
  - Health checks

## Environment Parity

- Confirm staging matches prod: env vars, feature flags, data shape

## Database Migrations

- Confirm migrations are reversible
- Test rollback
- Check for locking issues on large tables

## Load Testing

- For high-traffic features, run load tests
- Confirm rate limits and scaling behave as expected

## Runbook

- Update on-call runbook if feature introduces new failure modes

## Quality Tools — IDE

Confirm running in IDE or run manually:

| Tool | Purpose |
|------|---------|
| Error Lens | Inline error display |
| WebHint | Browser best practices |
| ESLint | JS/TS linting |
| typescript-eslint | TS-specific rules |
| Stylelint | CSS linting |
| eslint-plugin-react-hooks | Hooks rules |
| eslint-plugin-jest | Jest rules |
| axe Linter | A11y linting |
| SonarLint | Code quality |
| Code Spell Checker | Typos |
| SQLFluff | SQL linting |
| Prettier | Formatting |

## Quality Scans — Pipeline

Run or confirm in pipeline:

| Scan | Command |
|------|---------|
| Type check | `tsc --noEmit` |
| Unused deps | `depcheck` |
| Dep vulnerabilities | `npm audit` / `pip-audit` |
| Code quality | SonarQube |
| Copy-paste detection | `npx jscpd <path>` |
| License compliance | `license-checker` / `pip-licenses` |

Flag copyleft licenses in proprietary code.

## Bundle Analysis

- Check bundle size: `webpack-bundle-analyzer`, `source-map-explorer`
- Flag unexpected growth

## Manual Checks

Remind to run:

- **Smoke test in staging** — before prod
- **Lighthouse** — performance, a11y, SEO, best practices
- **WAVE** — a11y audit
- **Performance profiling** — browser devtools, backend profiling as needed