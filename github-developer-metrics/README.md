# GitHub Developer Metrics

DORA/Accelerate-aligned PR flow reports for Command-Cloud CDS repositories.

## Quick start

```bash
# Default: rolling 13 weeks → ~/.cursor/output/github-developer-metrics/
python3 ~/.claude/skills/github-developer-metrics/scripts/developer_pr_metrics.py
```

Open the report:

```bash
open ~/.cursor/output/github-developer-metrics/latest.md
```

## Monthly cadence

Run on the first working day of each month (defaults to trailing 13 weeks):

```bash
python3 ~/.claude/skills/github-developer-metrics/scripts/developer_pr_metrics.py \
  --report-name "report-$(date +%Y-%m)"
```

Compare month-over-month using the JSON exports:

```bash
ls ~/.cursor/output/github-developer-metrics/report-*.json
```

## Custom date range

```bash
python3 ~/.claude/skills/github-developer-metrics/scripts/developer_pr_metrics.py \
  --since 2026-01-01 \
  --until 2026-07-09 \
  --report-name report-2026-h1
```

## CLI flags

| Flag | Purpose |
|------|---------|
| `--since` / `--until` | Date range (YYYY-MM-DD) |
| `--output-dir` | Report destination (default: `~/.cursor/output/github-developer-metrics/`) |
| `--roster` | Alternate roster JSON path |
| `--format md\|json\|both` | Output format |
| `--report-name` | Base filename without extension |
| `--enrich-all` | Enrich every merged PR (slow). Default: roster authors only |

## Performance

Default enrichment covers **roster authors only** (~150–250 PRs for a long period, ~1 min for 13 weeks). Use `--enrich-all` only when you need org-wide batch size and review stats (can take 30+ minutes for half-year ranges).

## Updating the team roster

Edit `references/developer-roster.json`:

- `developers` — display name → GitHub login
- `repos` — repositories to include
- `exclude_logins` — bots to omit from throughput
- `stale_open_days` / `stale_update_days` — stale PR thresholds

## How to interpret (without misusing as rankings)

| Report section | Good use | Avoid |
|----------------|----------|-------|
| Weekly throughput | Team delivery cadence trend | Individual leaderboard |
| Lead time p50/p85 | Flow health (first commit → merge) | Blaming individuals for outliers |
| PR cycle time | Review/process wait (created → merge) | Treating it as full coding lead time |
| Batch size | Identify large PRs slowing review | Penalizing necessary large changes |
| Stale inventory | Process cleanup | Individual blame |
| Review coverage | Collaboration health | Mandatory 100% targets without context |

**Not measured:** change failure rate, MTTR (need incident/deploy data). Lead time stops at **merge** (SAFe train), not production.

## Output files

| File | Purpose |
|------|---------|
| `report-YYYY-MM-DD.md` | Full human-readable report |
| `report-YYYY-MM-DD.json` | Same data for diffing / automation |
| `latest.md` / `latest.json` | Copy of most recent run |

## Requirements

- Python 3.10+
- GitHub CLI (`gh`) authenticated with `repo` and `read:org`

## Invoke in Cursor

```
/github-developer-metrics
```

Or ask: "Run developer metrics for the last 13 weeks and summarize the signals."
