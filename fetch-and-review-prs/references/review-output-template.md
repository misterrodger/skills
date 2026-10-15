# Cluster review output

Write one file per Jira/feature cluster under `pr-reviews/YYYY-MM-DD/<KEY>.md` (or `no-ticket__<repo>__pr-<n>.md`).

Start from `/Users/jrodger/Github/pr-reviews/templates/cluster-review.md`.

Required sections:

1. PRs in cluster (table)
2. Readiness
3. Requirements / AC coverage
4. Context used (paths + freshness)
5. Critical
6. Advised
7. Skill notes (dev-coding-practices, typescript-type-safety, test-code-quality, pr-review, command-alkon-best-practices)
8. Security assessment
9. Suggested actions

Every Critical/Advised item: workspace-relative file link when reviewing from a local repo checkout (same rules as pr-review `REFERENCE.md`).
