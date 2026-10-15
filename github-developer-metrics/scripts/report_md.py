"""Markdown report builder for developer PR metrics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from metrics import (
    ReportData,
    all_weeks_in_range,
    batch_size_by_developer,
    batch_size_team,
    build_json_export,
    closure_outcomes,
    compute_stale_prs,
    compute_weekly_merged,
    developer_identities,
    developer_throughput,
    executive_summary,
    generate_signals,
    large_batch_inventory,
    lead_time_by_developer,
    lead_time_monthly_team,
    lead_time_weekly_team,
    pr_cycle_time_by_developer,
    pr_cycle_time_monthly_team,
    pr_cycle_time_weekly_team,
    repo_distribution_matrix,
    research_appendix,
    review_flow_by_author,
    review_flow_by_reviewer,
    review_flow_team,
    rolling_avg,
)


def _fmt_num(value: float | int | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    if isinstance(value, int):
        return str(value)
    return f"{value:.{decimals}f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.1f}%"


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "_No data._\n"

    str_rows = [[str(c) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells: list[str]) -> str:
        return "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells)) + " |"

    lines = [
        fmt_row(headers),
        "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |",
    ]
    for row in str_rows:
        lines.append(fmt_row(row))
    return "\n".join(lines) + "\n"


def load_methodology(skill_root: Path) -> str:
    path = skill_root / "references" / "metrics-methodology.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "_Methodology reference not found._\n"


def build_markdown_report(data: ReportData, skill_root: Path) -> str:
    summary = executive_summary(data)
    export = build_json_export(data)
    methodology = load_methodology(skill_root)

    parts: list[str] = [
        "# GitHub Developer Metrics Report\n",
        f"**Generated:** {export['generated_at']}  ",
        f"**Period:** {summary['period_start']} → {summary['period_end']} "
        f"({summary['weeks']} weeks)  ",
        f"**Org:** {data.roster.org}  ",
        f"**Repos:** {', '.join(f'`{r}`' for r in data.roster.repos)}\n",
        "---\n",
        "## Methodology & limitations\n",
        methodology,
        "\n---\n",
        "## 1. Executive summary\n",
        _section_executive(summary),
        "\n---\n",
        "## 2. Developer identity reference\n",
        _section_identities(developer_identities(data)),
        "\n---\n",
        "## 3. Deployment frequency proxy — team throughput\n",
        _section_weekly_throughput(data),
        "\n---\n",
        "## 4. Throughput by developer (contribution context)\n",
        _section_developer_throughput(developer_throughput(data)),
        "\n---\n",
        "## 5. Lead time for changes proxy\n",
        _section_lead_time(data),
        "\n---\n",
        "## 6. PR cycle time (created → merge)\n",
        _section_pr_cycle_time(data),
        "\n---\n",
        "## 7. Batch size (Accelerate flow)\n",
        _section_batch_size(data),
        "\n---\n",
        "## 8. Review & collaboration flow\n",
        _section_review_flow(data),
        "\n---\n",
        "## 9. Process health — stale open PR inventory\n",
        _section_stale(compute_stale_prs(data)),
        "\n---\n",
        "## 10. Closure outcomes (non-punitive)\n",
        _section_closure(closure_outcomes(data)),
        "\n---\n",
        "## 11. Repository distribution matrix\n",
        _section_repo_matrix(data),
        "\n---\n",
        "## 12. Signals to watch\n",
        _section_signals(generate_signals(data, summary)),
    ]
    return "\n".join(parts)


def _section_executive(summary: dict[str, Any]) -> str:
    lines = [
        "| Signal | Value |",
        "| --- | --- |",
        f"| Team merged PRs (roster) | {summary['team_merged']} |",
        f"| All merged PRs (incl. non-roster) | {summary['all_merged']} |",
        f"| Team merged / week | {_fmt_num(summary['team_merged_per_week'], 2)} |",
        f"| Prior period merged / week | {_fmt_num(summary['prior_merged_per_week'], 2)} |",
        f"| Throughput change vs prior period | {_fmt_pct(summary['throughput_change_pct']) if summary.get('throughput_change_pct') is not None else '—'} |",
        f"| Lead time p50 (days, first commit → merge) | {_fmt_num(summary['lead_time_p50'])} |",
        f"| Lead time p85 (days, first commit → merge) | {_fmt_num(summary['lead_time_p85'])} |",
        f"| PR cycle time p50 (days, created → merge) | {_fmt_num(summary['pr_cycle_p50'])} |",
        f"| PR cycle time p85 (days, created → merge) | {_fmt_num(summary['pr_cycle_p85'])} |",
        f"| Open WIP (roster) | {summary['open_wip']} |",
        f"| Stale open PRs (all authors) | {summary['stale_total']} |",
        f"| Stale open PRs (roster) | {summary['stale_roster']} |",
        f"| Change failure rate | **Not measured** |",
        f"| MTTR | **Not measured** |",
        "",
        "_Merge ≠ deploy (SAFe release train). Lead time is first commit → merge; "
        "PR cycle time is created → merge. CFR/MTTR need incident/deploy telemetry._",
    ]
    return "\n".join(lines) + "\n"


def _section_identities(rows: list[dict[str, Any]]) -> str:
    return md_table(
        ["Display name", "GitHub login", "First PR in period", "Active weeks"],
        [
            [r["display_name"], r["github_login"], r["first_pr_in_period"], r["active_weeks"]]
            for r in rows
        ],
    )


def _section_weekly_throughput(data: ReportData) -> str:
    weekly = compute_weekly_merged(data)
    weeks = all_weeks_in_range(data.since, data.until)
    team_counts = [weekly.get(wk, {}).get("_team", 0) for wk in weeks]
    rolling = rolling_avg([float(c) for c in team_counts], 4)

    headers = ["Week", "Merged (team)", *data.roster.repos, "4-wk rolling avg"]
    rows: list[list[Any]] = []
    for i, wk in enumerate(weeks):
        row_data = weekly.get(wk, {})
        rows.append([
            wk,
            row_data.get("_team", 0),
            *[row_data.get(f"_repo:{repo}", 0) for repo in data.roster.repos],
            _fmt_num(rolling[i], 2) if rolling[i] is not None else "—",
        ])

    table_a = (
        "_Weekly rows include only **complete ISO weeks** "
        "(report end date is on/after that week’s Friday)._\n\n"
        "### Table A — Weekly merged PRs\n\n" + md_table(headers, rows)
    )

    prior_note = (
        f"\n### Table B — Prior period comparison\n\n"
        f"Prior window: same length immediately before `{data.since.date().isoformat()}`.  \n"
        f"Prior period merged (roster): **{data.prior_merged_count}** "
        f"({_fmt_num(data.prior_merged_count / data.prior_weeks, 2)}/week).\n"
    )
    return table_a + prior_note


def _section_developer_throughput(rows: list[dict[str, Any]]) -> str:
    intro = (
        "_Per-developer throughput for capacity and contribution context — not a performance ranking. "
        "Use **active weeks** for developers who joined mid-period._\n\n"
    )
    return intro + md_table(
        [
            "Developer",
            "Merged",
            "Closed",
            "Merged/wk (calendar)",
            "Merged/wk (active weeks)",
            "Open WIP",
            "Merge rate",
        ],
        [
            [
                r["developer"],
                r["merged"],
                r["closed"],
                _fmt_num(r["merged_per_week_calendar"], 2),
                _fmt_num(r["merged_per_week_active"], 2),
                r["open_wip"],
                _fmt_pct(100 * r["merge_rate"]) if r["merge_rate"] is not None else "—",
            ]
            for r in rows
        ],
    )


def _percentile_trend_table(rows: list[dict[str, Any]], period_key: str) -> str:
    return md_table(
        [period_key.capitalize(), "n", "p50", "p75", "p85", "p95"],
        [
            [
                r[period_key], r["n"],
                _fmt_num(r["p50"]), _fmt_num(r["p75"]),
                _fmt_num(r["p85"]), _fmt_num(r["p95"]),
            ]
            for r in rows
        ],
    )


def _developer_percentile_table(rows: list[dict[str, Any]]) -> str:
    return md_table(
        ["Developer", "n", "p50", "p75", "p85", "p95", "max"],
        [
            [
                r["developer"], r["n"],
                _fmt_num(r["p50"]), _fmt_num(r["p75"]),
                _fmt_num(r["p85"]), _fmt_num(r["p95"]), _fmt_num(r["max"]),
            ]
            for r in rows
        ],
    )


def _section_lead_time(data: ReportData) -> str:
    weekly = lead_time_weekly_team(data)
    monthly = lead_time_monthly_team(data)
    by_dev = lead_time_by_developer(data)
    appendix = research_appendix(data)

    parts = [
        "_**Lead time** = earliest non-merge commit author date → merge "
        "(falls back to PR created if commits unavailable). Research PRs excluded. "
        "Weekly rows use complete ISO weeks only (through Friday)._\n",
        "### Team — weekly lead time (days)\n",
        _percentile_trend_table(weekly, "week"),
        "### Team — monthly lead time (days)\n",
        _percentile_trend_table(monthly, "month"),
        "### By developer — merged PRs (research excluded)\n",
        _developer_percentile_table(by_dev),
        "### Appendix — research / long-lived draft PRs\n",
        md_table(
            ["Repo", "#", "Author", "State", "Draft", "Days open", "Title", "URL"],
            [
                [
                    r["repo"],
                    r["number"],
                    r["author_name"],
                    r["state"],
                    r["draft"],
                    _fmt_num(r["days_open"]),
                    r["title"],
                    r["url"],
                ]
                for r in appendix
            ],
        ),
    ]
    return "\n".join(parts)


def _section_pr_cycle_time(data: ReportData) -> str:
    weekly = pr_cycle_time_weekly_team(data)
    monthly = pr_cycle_time_monthly_team(data)
    by_dev = pr_cycle_time_by_developer(data)

    parts = [
        "_**PR cycle time** = PR created → merge (review/process wait after open). "
        "Complements lead time; excludes pre-PR coding. Research PRs excluded. "
        "Weekly rows use complete ISO weeks only (through Friday)._\n",
        "### Team — weekly PR cycle time (days)\n",
        _percentile_trend_table(weekly, "week"),
        "### Team — monthly PR cycle time (days)\n",
        _percentile_trend_table(monthly, "month"),
        "### By developer — merged PRs (research excluded)\n",
        _developer_percentile_table(by_dev),
    ]
    return "\n".join(parts)


def _section_batch_size(data: ReportData) -> str:
    team = batch_size_team(data)
    by_dev = batch_size_by_developer(data)
    large = large_batch_inventory(data)

    parts = [
        "### Team batch size (merged PRs, research excluded)\n",
        md_table(
            ["Metric", "p50", "p85"],
            [
                ["Lines changed", _fmt_num(team["lines_p50"], 0), _fmt_num(team["lines_p85"], 0)],
                ["Files changed", _fmt_num(team["files_p50"], 0), _fmt_num(team["files_p85"], 0)],
            ],
        ),
        "### By developer\n",
        md_table(
            ["Developer", "n", "Lines p50", "Lines p85", "Files p50", "Files p85"],
            [
                [r["developer"], r["n"], _fmt_num(r["lines_p50"], 0), _fmt_num(r["lines_p85"], 0),
                 _fmt_num(r["files_p50"], 0), _fmt_num(r["files_p85"], 0)]
                for r in by_dev
            ],
        ),
        "### Large batch inventory (≥ team lines p85)\n",
        md_table(
            ["Repo", "#", "Author", "Lines", "Files", "Title", "URL"],
            [
                [r["repo"], r["number"], r["author_name"], r["lines"], r["files"], r["title"], r["url"]]
                for r in large
            ],
        ),
    ]
    return "\n".join(parts)


def _section_review_flow(data: ReportData) -> str:
    team = review_flow_team(data)
    by_author = review_flow_by_author(data)
    by_reviewer = review_flow_by_reviewer(data)

    parts = [
        "### Team review flow\n",
        md_table(
            ["Merged PRs (n)", "Review coverage", "Time to first review p50 (days)", "TTFR p85 (days)"],
            [[
                team["n"],
                _fmt_pct(team["reviewed_pct"]),
                _fmt_num(team["ttfr_p50"]),
                _fmt_num(team["ttfr_p85"]),
            ]],
        ),
        "### By developer (as PR author)\n",
        md_table(
            ["Developer", "Merged", "Review coverage", "TTFR p50", "TTFR p85"],
            [
                [r["developer"], r["merged"], _fmt_pct(r["reviewed_pct"]),
                 _fmt_num(r["ttfr_p50"]), _fmt_num(r["ttfr_p85"])]
                for r in by_author
            ],
        ),
        "### By developer (as reviewer — collaboration signal)\n",
        md_table(
            ["Developer", "Reviews given", "Repos reviewed"],
            [[r["developer"], r["reviews_given"], r["repos_reviewed"]] for r in by_reviewer],
        ),
    ]
    return "\n".join(parts)


def _section_stale(rows: list[dict[str, Any]]) -> str:
    roster_count = sum(1 for r in rows if r["tracked"])
    research_count = sum(1 for r in rows if r["research"])
    intro = (
        f"**Summary:** {len(rows)} stale PR(s) total — "
        f"{roster_count} from roster, {len(rows) - roster_count} from other authors, "
        f"{research_count} flagged research/[DO NOT MERGE].\n\n"
    )
    return intro + md_table(
        ["Tracked?", "Repo", "#", "Author", "Created", "Days open", "Days stale", "Draft", "Research?", "Title", "URL"],
        [
            [
                "Yes" if r["tracked"] else "No",
                r["repo"],
                r["number"],
                r["author_name"],
                r["created"][:10],
                r["days_open"],
                r["days_since_update"],
                r["draft"],
                "Yes" if r["research"] else "No",
                r["title"],
                r["url"],
            ]
            for r in rows
        ],
    )


def _section_closure(rows: list[dict[str, Any]]) -> str:
    footnote = (
        "\n_Footnote: **Superseded/sync** = sync/rebase/superseded branch patterns. "
        "**Research** = `[DO NOT MERGE]` or spike/research in title. "
        "**Other** = remaining closed-without-merge. None of these are labeled as failure rate._\n"
    )
    return md_table(
        ["Developer", "Merged", "Closed not merged", "Superseded/sync", "Research", "Other"],
        [
            [r["developer"], r["merged"], r["closed_not_merged"],
             r["superseded_sync"], r["research"], r["other"]]
            for r in rows
        ],
    ) + footnote


def _section_repo_matrix(data: ReportData) -> str:
    short_repos, rows = repo_distribution_matrix(data)
    headers = ["Developer", *short_repos, "Total"]
    return md_table(
        headers,
        [[r["developer"], *[r[s] for s in short_repos], r["total"]] for r in rows],
    )


def _section_signals(signals: list[str]) -> str:
    return "\n".join(f"- {s}" for s in signals) + "\n"
