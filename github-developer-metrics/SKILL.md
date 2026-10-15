---
name: github-developer-metrics
description: Compute team PR throughput and cycle-time metrics for Command-Cloud repos via gh API—closed/merged PRs per developer, weekly trends, stale open PRs, DORA/Accelerate-aligned flow signals. Use when the user asks for developer metrics, PR velocity, cycle time, monthly team throughput reports, or stale PR audits.
---

# GitHub Developer Metrics

Read-only reporting skill. Uses `gh api` and Python — **never edits repositories**.

## When to Use

- "Developer metrics", "PR velocity", "cycle time", "team throughput"
- Monthly or quarterly engineering flow reports for Command-Cloud CDS repos
- Stale / abandoned open PR audit
- DORA-style deployment frequency and lead time **proxies** from PR data

## Prerequisites

- **GitHub CLI** authenticated: `gh auth status -h github.com` (scopes: `repo`, `read:org`)
- **Python 3.10+** on PATH
- Network access to github.com

## Default behaviour

| Setting | Default |
|---------|---------|
| Period | Rolling **13 weeks** ending today |
| Output | `~/.cursor/output/github-developer-metrics/` |
| Roster | `references/developer-roster.json` in this skill |
| Formats | Markdown + JSON (`latest.md` / `latest.json` copies) |

## Instructions

### 0. Ask mode

If you are in **Ask mode**, tell the user to switch to **Agent mode** to run the script. You may still explain how to interpret an existing report at `~/.cursor/output/github-developer-metrics/latest.md`.

### 1. Validate

```bash
gh auth status -h github.com
python3 --version
```

### 2. Run (default — rolling 13 weeks)

```bash
python3 ~/.claude/skills/github-developer-metrics/scripts/developer_pr_metrics.py
```

### 3. Run (custom period)

```bash
python3 ~/.claude/skills/github-developer-metrics/scripts/developer_pr_metrics.py \
  --since 2026-01-01 \
  --until 2026-07-09 \
  --report-name report-2026-h1
```

### 4. Present results

1. Open `~/.cursor/output/github-developer-metrics/latest.md`
2. Summarize **3–5 signals** from section 11 ("Signals to watch") and the executive summary
3. Call out stale PR inventory (section 8) if the user asked about abandoned PRs
4. **Do not** frame individual tables as performance rankings — use team trends and capacity context language

## CLI flags

| Flag | Purpose |
|------|---------|
| `--since YYYY-MM-DD` | Period start (default: 13 weeks before `--until`) |
| `--until YYYY-MM-DD` | Period end (default: today UTC) |
| `--output-dir PATH` | Report destination |
| `--roster PATH` | Alternate roster JSON |
| `--enrich-concurrency N` | Parallel PR detail fetches (default 8) |
| `--format md\|json\|both` | Output format |
| `--report-name NAME` | Base filename without extension |
| `--enrich-all` | Enrich every merged PR in period (slow; default is roster authors only) |

## Roster maintenance

Edit [`references/developer-roster.json`](references/developer-roster.json) to add/remove developers or repos without changing code.

## Report sections

1. Executive summary (team DORA proxies)
2. Developer identity reference
3. Weekly team throughput + rolling average
4. Per-developer throughput (contribution context)
5. Lead time percentiles (first commit → merge; weekly + monthly; research PRs in appendix)
6. PR cycle time (created → merge; weekly + monthly)
7. Batch size distribution
8. Review & collaboration flow
9. Stale open PR inventory (full table)
10. Closure outcomes (non-punitive)
11. Repository distribution matrix
12. Auto-generated signals to watch

See [`references/metrics-methodology.md`](references/metrics-methodology.md) for DORA mapping and interpretation rules.

## Read-only scope

- **Do not** edit repos, close PRs, or post comments unless the user explicitly asks in a separate task
- **Do not** treat hotfixes or closed-without-merge PRs as quality failures

## Estimated runtime

~3–5 minutes for a 13-week window across 9 repos (PR enrichment includes size, reviews, and first-commit timestamps). Longer windows (e.g. from 1 March) take longer.
