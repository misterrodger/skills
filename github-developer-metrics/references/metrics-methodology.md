# Metrics Methodology

This report uses GitHub pull request data as a **flow and throughput** lens. It is inspired by DORA and *Accelerate* research but does **not** replace deployment or incident telemetry.

## DORA mapping

| DORA metric | In this report? | Definition |
|-------------|-----------------|------------|
| Deployment frequency | Partial proxy | Count of **merged PRs per week** (team and per repo). Merge ≠ production deploy; for a SAFe release train this tracks delivery into the integration branch, not train-to-prod. |
| Lead time for changes | Yes (proxy) | **First commit → merged** on merged PRs. Uses the earliest **author date** among non-merge commits on the PR (falls back to PR `created_at` if commits are unavailable). Reported as p50 / p75 / p85 / p95 (days), not averages. Stops at merge — not production — by design for SAFe. |
| Change failure rate | **Not measured** | Requires incident or deployment failure data. Do not infer from closed-without-merge PRs. |
| Mean time to restore (MTTR) | **Not measured** | Requires incident resolution timestamps. |

## Secondary flow metrics

| Signal | Definition | How to interpret |
|--------|------------|------------------|
| PR cycle time | Created → merged | Review/process wait after the PR is opened. Complements lead time; does not include pre-PR coding. Reported weekly and monthly (p50–p95). |
| Batch size | Lines changed and files changed on merged PRs | Smaller batches generally indicate healthier flow. Informational — not a ranking score. |
| WIP | Open PR count per developer / team | High WIP can indicate bottlenecks or context-switching cost. |
| Stale inventory | Open ≥ N days with no update ≥ M days | Process health signal. Candidate for close-or-revive, not individual blame. |
| Review coverage | % merged PRs with ≥1 review from a non-author | Collaboration and knowledge-sharing signal. |
| Time to first review | Created → first non-author review | Flow efficiency; long waits may indicate review bottlenecks. |

## Weekly completeness

Weekly throughput, lead time, and PR cycle time tables include an ISO week only when the report end date is **on or after that week’s Friday**. Partial trailing weeks are omitted so the latest row is a full week.

## Lead time caveats

- **Author date** is used so rebases do not reset the clock via committer date.
- **Merge commits** (e.g. syncing `develop` into the branch) are skipped when picking the first commit so an early sync does not start lead time incorrectly.
- Commits made **before** the PR is opened are included — that is the main alignment with DORA “commit → done.”

## Exclusions and segmentation

- **Bots** — logins in `exclude_logins` and any login containing `[bot]` are excluded from throughput and lead-time tables.
- **Research PRs** — titles containing `[DO NOT MERGE]` or long-lived drafts are listed in a separate appendix and excluded from primary lead-time metrics.
- **Hotfixes** — PRs matching hotfix heuristics (title/branch) are never treated as negative quality signals.

## Closure outcomes (non-punitive)

Closed PRs that were not merged are categorized as:

- **Superseded/sync** — title or branch suggests sync, rebase, or superseded work.
- **Research** — `[DO NOT MERGE]` or explicit research/spike in title.
- **Other** — remaining closed-without-merge cases.

These are **not** labeled as failures or change failure rate.

## Individual developer tables

Per-developer tables are **contribution and capacity context**, not performance rankings. Use **active weeks** (weeks since first PR in period) when comparing developers who joined mid-period.

## Data source

All data is fetched read-only via `gh api` from the configured org/repos. No repository files are modified.
