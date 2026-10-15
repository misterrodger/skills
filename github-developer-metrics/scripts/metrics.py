"""Metric aggregation for developer PR reports."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from gh_client import PullRequest


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    sorted_vals = sorted(values)
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (pct / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def iso_week_key(dt: datetime) -> str:
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def days_between(start: datetime | None, end: datetime | None) -> float | None:
    if not start or not end:
        return None
    return (end - start).total_seconds() / 86400


def is_excluded_login(login: str, exclude_logins: list[str]) -> bool:
    lower = login.lower()
    if "[bot]" in lower or lower.endswith("-bot"):
        return True
    return login in exclude_logins


SUPERSEDED_PATTERNS = re.compile(
    r"sync|superseded|rebase|develop.?to|dev.?to.?pre|merge.?develop",
    re.IGNORECASE,
)
RESEARCH_PATTERNS = re.compile(r"\[DO NOT MERGE\]|research|spike", re.IGNORECASE)
HOTFIX_PATTERNS = re.compile(r"hotfix|urgent.?fix|prod.?fix", re.IGNORECASE)


def categorize_closure(pr: PullRequest) -> str:
    if pr.is_research or RESEARCH_PATTERNS.search(pr.title):
        return "research"
    title_branch = f"{pr.title} {pr.head_ref}"
    if SUPERSEDED_PATTERNS.search(title_branch):
        return "superseded_sync"
    return "other"


def is_research_pr(pr: PullRequest) -> bool:
    return pr.is_research or bool(RESEARCH_PATTERNS.search(pr.title))


def is_hotfix_pr(pr: PullRequest) -> bool:
    return bool(HOTFIX_PATTERNS.search(f"{pr.title} {pr.head_ref}"))


@dataclass
class RosterConfig:
    org: str
    repos: list[str]
    developers: dict[str, str]
    exclude_logins: list[str]
    stale_open_days: int
    stale_update_days: int

    @property
    def dev_logins(self) -> set[str]:
        return set(self.developers.values())

    @property
    def login_to_name(self) -> dict[str, str]:
        return {login: name for name, login in self.developers.items()}


@dataclass
class ReportData:
    since: datetime
    until: datetime
    roster: RosterConfig
    closed_prs: list[PullRequest] = field(default_factory=list)
    open_prs: list[PullRequest] = field(default_factory=list)
    enriched_merged: list[PullRequest] = field(default_factory=list)
    prior_merged_count: int = 0
    prior_weeks: float = 0.0


def filter_in_period(pr: PullRequest, since: datetime, until: datetime, *, use_closed: bool = True) -> bool:
    anchor = pr.closed_at if use_closed else pr.created_at
    if not anchor:
        return False
    return since <= anchor <= until + timedelta(days=1)


def build_report_data(
    roster: RosterConfig,
    closed_prs: list[PullRequest],
    open_prs: list[PullRequest],
    enriched_merged: list[PullRequest],
    since: datetime,
    until: datetime,
) -> ReportData:
    period_closed = [
        p for p in closed_prs
        if filter_in_period(p, since, until) and not is_excluded_login(p.author_login, roster.exclude_logins)
    ]
    period_open = [
        p for p in open_prs
        if not is_excluded_login(p.author_login, roster.exclude_logins)
    ]
    period_merged = [
        p for p in enriched_merged
        if p.merged_at and since <= p.merged_at <= until + timedelta(days=1)
        and not is_excluded_login(p.author_login, roster.exclude_logins)
    ]

    period_days = (until - since).days or 1
    prior_until = since - timedelta(seconds=1)
    prior_since = since - timedelta(days=period_days)
    prior_merged = [
        p for p in closed_prs
        if p.merged_at
        and prior_since <= p.merged_at < since
        and not is_excluded_login(p.author_login, roster.exclude_logins)
        and p.author_login in roster.dev_logins
    ]

    return ReportData(
        since=since,
        until=until,
        roster=roster,
        closed_prs=period_closed,
        open_prs=period_open,
        enriched_merged=period_merged,
        prior_merged_count=len(prior_merged),
        prior_weeks=max(1.0, period_days / 7),
    )


def calendar_weeks(since: datetime, until: datetime) -> float:
    return max(1.0, (until - since).days / 7)


def active_weeks(first_pr: datetime | None, until: datetime) -> float:
    if not first_pr:
        return 1.0
    return max(1.0, (until - first_pr).days / 7)


def first_pr_in_period(prs: list[PullRequest], login: str) -> datetime | None:
    dates = [p.created_at for p in prs if p.author_login == login and p.created_at]
    return min(dates) if dates else None


def merged_for_lead_time(pr: PullRequest) -> bool:
    return pr.is_merged and not is_research_pr(pr)


def lead_time_days(pr: PullRequest) -> float | None:
    """DORA proxy: first commit (fallback PR created) → merged."""
    start = pr.first_commit_at or pr.created_at
    return days_between(start, pr.merged_at)


def pr_cycle_time_days(pr: PullRequest) -> float | None:
    """PR open duration: created → merged."""
    return days_between(pr.created_at, pr.merged_at)


def time_to_first_review_days(pr: PullRequest) -> float | None:
    author = pr.author_login
    review_times: list[datetime] = []
    for review in pr.reviews:
        reviewer = (review.get("user") or {}).get("login") or ""
        submitted = review.get("submitted_at")
        if reviewer and reviewer != author and submitted:
            dt = datetime.fromisoformat(submitted.replace("Z", "+00:00"))
            review_times.append(dt)
    if not review_times or not pr.created_at:
        return None
    first = min(review_times)
    return days_between(pr.created_at, first)


def has_non_author_review(pr: PullRequest) -> bool:
    author = pr.author_login
    for review in pr.reviews:
        reviewer = (review.get("user") or {}).get("login") or ""
        if reviewer and reviewer != author:
            return True
    return False


def compute_weekly_merged(data: ReportData) -> dict[str, dict[str, int]]:
    """week -> {login or '_team': count} and per-repo."""
    weekly: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for pr in data.enriched_merged:
        if not pr.merged_at:
            continue
        wk = iso_week_key(pr.merged_at)
        weekly[wk]["_team"] += 1
        weekly[wk][pr.author_login] += 1
        weekly[wk][f"_repo:{pr.repo}"] += 1
    return dict(weekly)


def all_weeks_in_range(since: datetime, until: datetime) -> list[str]:
    """ISO weeks in [since, until] whose Friday has been reached (full weeks only)."""
    weeks: list[str] = []
    current = since
    seen: set[str] = set()
    while current <= until:
        wk = iso_week_key(current)
        if wk not in seen:
            weeks.append(wk)
            seen.add(wk)
        current += timedelta(days=7)
    wk_end = iso_week_key(until)
    if wk_end not in seen:
        weeks.append(wk_end)
    return [wk for wk in sorted(set(weeks)) if week_is_complete(wk, until)]


def week_friday(week_key: str) -> datetime:
    year_str, week_str = week_key.split("-W")
    monday = datetime.fromisocalendar(int(year_str), int(week_str), 1).replace(tzinfo=timezone.utc)
    return monday + timedelta(days=4)


def week_is_complete(week_key: str, until: datetime) -> bool:
    """True when until is on/after that ISO week's Friday."""
    return until.date() >= week_friday(week_key).date()


def rolling_avg(values: list[float], window: int = 4) -> list[float | None]:
    result: list[float | None] = []
    for i in range(len(values)):
        if i < window - 1:
            result.append(None)
        else:
            window_vals = values[i - window + 1 : i + 1]
            result.append(sum(window_vals) / window)
    return result


def compute_stale_prs(data: ReportData, now: datetime | None = None) -> list[dict[str, Any]]:
    now = now or datetime.now(timezone.utc)
    stale: list[dict[str, Any]] = []
    for pr in data.open_prs:
        if not pr.created_at:
            continue
        days_open = (now - pr.created_at).days
        days_since_update = (now - pr.updated_at).days if pr.updated_at else days_open
        if days_open >= data.roster.stale_open_days and days_since_update >= data.roster.stale_update_days:
            stale.append({
                "tracked": pr.author_login in data.roster.dev_logins,
                "repo": pr.repo,
                "number": pr.number,
                "author": pr.author_login,
                "author_name": data.roster.login_to_name.get(pr.author_login, pr.author_login),
                "created": pr.created_at.isoformat(),
                "days_open": days_open,
                "days_since_update": days_since_update,
                "draft": pr.draft,
                "research": is_research_pr(pr),
                "title": pr.title,
                "url": pr.url,
            })
    stale.sort(key=lambda x: (-x["days_open"], x["repo"], x["number"]))
    return stale


def developer_throughput(data: ReportData) -> list[dict[str, Any]]:
    weeks_cal = calendar_weeks(data.since, data.until)
    rows: list[dict[str, Any]] = []

    for name, login in sorted(data.roster.developers.items()):
        closed = [p for p in data.closed_prs if p.author_login == login]
        merged = [p for p in closed if p.is_merged]
        open_wip = len([p for p in data.open_prs if p.author_login == login])
        first = first_pr_in_period(data.closed_prs + data.open_prs, login)
        active = active_weeks(first, data.until)
        merge_rate = len(merged) / len(closed) if closed else None

        rows.append({
            "developer": name,
            "login": login,
            "merged": len(merged),
            "closed": len(closed),
            "merged_per_week_calendar": len(merged) / weeks_cal,
            "merged_per_week_active": len(merged) / active,
            "open_wip": open_wip,
            "merge_rate": merge_rate,
            "first_pr": first.isoformat() if first else None,
            "active_weeks": round(active, 1),
        })
    return rows


def developer_identities(data: ReportData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, login in sorted(data.roster.developers.items()):
        first = first_pr_in_period(data.closed_prs + data.open_prs, login)
        active = active_weeks(first, data.until)
        rows.append({
            "display_name": name,
            "github_login": login,
            "first_pr_in_period": first.date().isoformat() if first else "—",
            "active_weeks": round(active, 1),
        })
    return rows


def lead_time_by_developer(data: ReportData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, login in sorted(data.roster.developers.items()):
        prs = [
            p for p in data.enriched_merged
            if p.author_login == login and merged_for_lead_time(p)
        ]
        days = [d for p in prs if (d := lead_time_days(p)) is not None]
        rows.append({
            "developer": name,
            "n": len(days),
            "p50": percentile(days, 50),
            "p75": percentile(days, 75),
            "p85": percentile(days, 85),
            "p95": percentile(days, 95),
            "max": max(days) if days else None,
        })
    return rows


def pr_cycle_time_by_developer(data: ReportData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, login in sorted(data.roster.developers.items()):
        prs = [
            p for p in data.enriched_merged
            if p.author_login == login and merged_for_lead_time(p)
        ]
        days = [d for p in prs if (d := pr_cycle_time_days(p)) is not None]
        rows.append({
            "developer": name,
            "n": len(days),
            "p50": percentile(days, 50),
            "p75": percentile(days, 75),
            "p85": percentile(days, 85),
            "p95": percentile(days, 95),
            "max": max(days) if days else None,
        })
    return rows


def lead_time_monthly_team(data: ReportData) -> list[dict[str, Any]]:
    by_month: dict[str, list[float]] = defaultdict(list)
    for pr in data.enriched_merged:
        if not merged_for_lead_time(pr) or not pr.merged_at:
            continue
        d = lead_time_days(pr)
        if d is not None:
            by_month[month_key(pr.merged_at)].append(d)

    rows: list[dict[str, Any]] = []
    for month in sorted(by_month.keys()):
        days = by_month[month]
        rows.append({
            "month": month,
            "n": len(days),
            "p50": percentile(days, 50),
            "p75": percentile(days, 75),
            "p85": percentile(days, 85),
            "p95": percentile(days, 95),
        })
    return rows


def pr_cycle_time_monthly_team(data: ReportData) -> list[dict[str, Any]]:
    by_month: dict[str, list[float]] = defaultdict(list)
    for pr in data.enriched_merged:
        if not merged_for_lead_time(pr) or not pr.merged_at:
            continue
        d = pr_cycle_time_days(pr)
        if d is not None:
            by_month[month_key(pr.merged_at)].append(d)

    rows: list[dict[str, Any]] = []
    for month in sorted(by_month.keys()):
        days = by_month[month]
        rows.append({
            "month": month,
            "n": len(days),
            "p50": percentile(days, 50),
            "p75": percentile(days, 75),
            "p85": percentile(days, 85),
            "p95": percentile(days, 95),
        })
    return rows


def pr_cycle_time_weekly_team(data: ReportData) -> list[dict[str, Any]]:
    by_week: dict[str, list[float]] = defaultdict(list)
    for pr in data.enriched_merged:
        if not merged_for_lead_time(pr) or not pr.merged_at:
            continue
        d = pr_cycle_time_days(pr)
        if d is not None:
            by_week[iso_week_key(pr.merged_at)].append(d)

    rows: list[dict[str, Any]] = []
    for week in all_weeks_in_range(data.since, data.until):
        days = by_week.get(week, [])
        rows.append({
            "week": week,
            "n": len(days),
            "p50": percentile(days, 50),
            "p75": percentile(days, 75),
            "p85": percentile(days, 85),
            "p95": percentile(days, 95),
        })
    return rows


def lead_time_weekly_team(data: ReportData) -> list[dict[str, Any]]:
    by_week: dict[str, list[float]] = defaultdict(list)
    for pr in data.enriched_merged:
        if not merged_for_lead_time(pr) or not pr.merged_at:
            continue
        d = lead_time_days(pr)
        if d is not None:
            by_week[iso_week_key(pr.merged_at)].append(d)

    rows: list[dict[str, Any]] = []
    for week in all_weeks_in_range(data.since, data.until):
        days = by_week.get(week, [])
        rows.append({
            "week": week,
            "n": len(days),
            "p50": percentile(days, 50),
            "p75": percentile(days, 75),
            "p85": percentile(days, 85),
            "p95": percentile(days, 95),
        })
    return rows


def research_appendix(data: ReportData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    all_prs = data.enriched_merged + [
        p for p in data.closed_prs if not p.is_merged
    ] + data.open_prs
    seen: set[tuple[str, int]] = set()
    for pr in all_prs:
        key = (pr.repo, pr.number)
        if key in seen:
            continue
        if is_research_pr(pr) or (pr.draft and pr.state == "open"):
            seen.add(key)
            days = None
            if pr.created_at:
                end = pr.merged_at or pr.closed_at or data.until
                days = days_between(pr.created_at, end)
            rows.append({
                "repo": pr.repo,
                "number": pr.number,
                "author": pr.author_login,
                "author_name": data.roster.login_to_name.get(pr.author_login, pr.author_login),
                "state": pr.state,
                "draft": pr.draft,
                "days_open": round(days, 1) if days is not None else None,
                "title": pr.title,
                "url": pr.url,
            })
    rows.sort(key=lambda x: (x["repo"], x["number"]))
    return rows


def batch_size_team(data: ReportData) -> dict[str, float | None]:
    lines = [float(p.lines_changed) for p in data.enriched_merged if merged_for_lead_time(p)]
    files = [float(p.changed_files) for p in data.enriched_merged if merged_for_lead_time(p)]
    return {
        "lines_p50": percentile(lines, 50),
        "lines_p85": percentile(lines, 85),
        "files_p50": percentile(files, 50),
        "files_p85": percentile(files, 85),
    }


def batch_size_by_developer(data: ReportData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, login in sorted(data.roster.developers.items()):
        prs = [
            p for p in data.enriched_merged
            if p.author_login == login and merged_for_lead_time(p)
        ]
        lines = [float(p.lines_changed) for p in prs]
        files = [float(p.changed_files) for p in prs]
        rows.append({
            "developer": name,
            "n": len(prs),
            "lines_p50": percentile(lines, 50),
            "lines_p85": percentile(lines, 85),
            "files_p50": percentile(files, 50),
            "files_p85": percentile(files, 85),
        })
    return rows


def large_batch_inventory(data: ReportData) -> list[dict[str, Any]]:
    team_lines = [
        float(p.lines_changed) for p in data.enriched_merged if merged_for_lead_time(p)
    ]
    threshold = percentile(team_lines, 85) or 0
    rows: list[dict[str, Any]] = []
    for pr in data.enriched_merged:
        if not merged_for_lead_time(pr):
            continue
        if pr.lines_changed >= threshold:
            rows.append({
                "repo": pr.repo,
                "number": pr.number,
                "author": pr.author_login,
                "author_name": data.roster.login_to_name.get(pr.author_login, pr.author_login),
                "lines": pr.lines_changed,
                "files": pr.changed_files,
                "title": pr.title,
                "url": pr.url,
            })
    rows.sort(key=lambda x: (-x["lines"], x["repo"]))
    return rows


def review_flow_team(data: ReportData) -> dict[str, Any]:
    merged = [p for p in data.enriched_merged if merged_for_lead_time(p)]
    if not merged:
        return {"reviewed_pct": None, "ttfr_p50": None, "ttfr_p85": None, "n": 0}
    reviewed = sum(1 for p in merged if has_non_author_review(p))
    ttfr = [d for p in merged if (d := time_to_first_review_days(p)) is not None]
    return {
        "n": len(merged),
        "reviewed_pct": 100.0 * reviewed / len(merged),
        "ttfr_p50": percentile(ttfr, 50),
        "ttfr_p85": percentile(ttfr, 85),
    }


def review_flow_by_author(data: ReportData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, login in sorted(data.roster.developers.items()):
        merged = [
            p for p in data.enriched_merged
            if p.author_login == login and merged_for_lead_time(p)
        ]
        if not merged:
            rows.append({
                "developer": name,
                "merged": 0,
                "reviewed_pct": None,
                "ttfr_p50": None,
                "ttfr_p85": None,
            })
            continue
        reviewed = sum(1 for p in merged if has_non_author_review(p))
        ttfr = [d for p in merged if (d := time_to_first_review_days(p)) is not None]
        rows.append({
            "developer": name,
            "merged": len(merged),
            "reviewed_pct": 100.0 * reviewed / len(merged),
            "ttfr_p50": percentile(ttfr, 50),
            "ttfr_p85": percentile(ttfr, 85),
        })
    return rows


def review_flow_by_reviewer(data: ReportData) -> list[dict[str, Any]]:
    counts: dict[str, int] = defaultdict(int)
    repos: dict[str, set[str]] = defaultdict(set)
    for pr in data.enriched_merged:
        if not merged_for_lead_time(pr):
            continue
        for review in pr.reviews:
            reviewer = (review.get("user") or {}).get("login") or ""
            if reviewer and reviewer in data.roster.dev_logins:
                counts[reviewer] += 1
                repos[reviewer].add(pr.repo)

    rows: list[dict[str, Any]] = []
    for name, login in sorted(data.roster.developers.items()):
        rows.append({
            "developer": name,
            "reviews_given": counts.get(login, 0),
            "repos_reviewed": len(repos.get(login, set())),
        })
    rows.sort(key=lambda x: -x["reviews_given"])
    return rows


def closure_outcomes(data: ReportData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, login in sorted(data.roster.developers.items()):
        closed = [p for p in data.closed_prs if p.author_login == login]
        merged = [p for p in closed if p.is_merged]
        not_merged = [p for p in closed if not p.is_merged]
        superseded = sum(1 for p in not_merged if categorize_closure(p) == "superseded_sync")
        research = sum(1 for p in not_merged if categorize_closure(p) == "research")
        other = len(not_merged) - superseded - research
        rows.append({
            "developer": name,
            "merged": len(merged),
            "closed_not_merged": len(not_merged),
            "superseded_sync": superseded,
            "research": research,
            "other": other,
        })
    return rows


def repo_distribution_matrix(data: ReportData) -> tuple[list[str], list[dict[str, Any]]]:
    repos = data.roster.repos
    rows: list[dict[str, Any]] = []
    for name, login in sorted(data.roster.developers.items()):
        row: dict[str, Any] = {"developer": name}
        for repo in repos:
            short = repo.replace("cds-", "")
            count = sum(
                1 for p in data.enriched_merged
                if p.author_login == login and p.repo == repo
            )
            row[short] = count
        row["total"] = sum(row[r.replace("cds-", "")] for r in repos)
        rows.append(row)
    short_repos = [r.replace("cds-", "") for r in repos]
    return short_repos, rows


def executive_summary(data: ReportData) -> dict[str, Any]:
    weeks = calendar_weeks(data.since, data.until)
    team_merged = len([
        p for p in data.enriched_merged
        if p.author_login in data.roster.dev_logins
    ])
    all_merged = len(data.enriched_merged)
    lead_days = [
        d for p in data.enriched_merged
        if merged_for_lead_time(p) and (d := lead_time_days(p)) is not None
    ]
    cycle_days = [
        d for p in data.enriched_merged
        if merged_for_lead_time(p) and (d := pr_cycle_time_days(p)) is not None
    ]
    open_wip = len([
        p for p in data.open_prs
        if p.author_login in data.roster.dev_logins
    ])
    stale = compute_stale_prs(data)
    stale_roster = sum(1 for s in stale if s["tracked"])

    current_rate = team_merged / weeks
    prior_rate = data.prior_merged_count / data.prior_weeks if data.prior_weeks else None
    rate_change = None
    if prior_rate and prior_rate > 0:
        rate_change = 100.0 * (current_rate - prior_rate) / prior_rate

    return {
        "period_start": data.since.date().isoformat(),
        "period_end": data.until.date().isoformat(),
        "weeks": round(weeks, 1),
        "repo_count": len(data.roster.repos),
        "roster_count": len(data.roster.developers),
        "team_merged": team_merged,
        "all_merged": all_merged,
        "team_merged_per_week": current_rate,
        "prior_merged_per_week": prior_rate,
        "throughput_change_pct": rate_change,
        "lead_time_p50": percentile(lead_days, 50),
        "lead_time_p85": percentile(lead_days, 85),
        "pr_cycle_p50": percentile(cycle_days, 50),
        "pr_cycle_p85": percentile(cycle_days, 85),
        "open_wip": open_wip,
        "stale_total": len(stale),
        "stale_roster": stale_roster,
    }


def generate_signals(data: ReportData, summary: dict[str, Any]) -> list[str]:
    signals: list[str] = []

    if summary.get("throughput_change_pct") is not None:
        pct = summary["throughput_change_pct"]
        direction = "increased" if pct > 0 else "decreased"
        signals.append(
            f"Team merged throughput {direction} {abs(pct):.0f}% vs prior "
            f"{summary['weeks']:.0f}-week window "
            f"({summary['team_merged_per_week']:.1f}/wk now vs "
            f"{summary['prior_merged_per_week']:.1f}/wk prior)."
        )

    monthly = lead_time_monthly_team(data)
    if len(monthly) >= 2:
        p85_vals = [(m["month"], m["p85"]) for m in monthly if m["p85"] is not None]
        if len(p85_vals) >= 2 and p85_vals[-1][1] and p85_vals[-2][1]:
            if p85_vals[-1][1] > p85_vals[-2][1] * 1.25:
                signals.append(
                    f"Lead time p85 rose in {p85_vals[-1][0]} "
                    f"({p85_vals[-1][1]:.1f}d vs {p85_vals[-2][1]:.1f}d prior month) — "
                    "see batch size and review flow tables."
                )

    stale = compute_stale_prs(data)
    roster_stale = [s for s in stale if s["tracked"]]
    if roster_stale:
        research_stale = sum(1 for s in roster_stale if s["research"])
        signals.append(
            f"{len(roster_stale)} stale open PR(s) from roster developers "
            f"({research_stale} flagged as research/[DO NOT MERGE]) — "
            "candidate for close-or-revive review."
        )

    review = review_flow_team(data)
    if review.get("reviewed_pct") is not None and review["reviewed_pct"] < 80:
        signals.append(
            f"Review coverage is {review['reviewed_pct']:.0f}% "
            f"(merged PRs with ≥1 non-author review) — below 80% target."
        )

    by_repo: dict[str, int] = defaultdict(int)
    for pr in data.enriched_merged:
        by_repo[pr.repo] += 1
    for repo, count in sorted(by_repo.items(), key=lambda x: -x[1]):
        reviewed = sum(
            1 for p in data.enriched_merged
            if p.repo == repo and merged_for_lead_time(p) and has_non_author_review(p)
        )
        total = sum(1 for p in data.enriched_merged if p.repo == repo and merged_for_lead_time(p))
        if total >= 5:
            pct = 100.0 * reviewed / total
            if pct < 80:
                signals.append(f"Review coverage on `{repo}` is {pct:.0f}% ({reviewed}/{total} merged PRs).")

    hotfixes = [p for p in data.enriched_merged if is_hotfix_pr(p)]
    if hotfixes:
        signals.append(
            f"{len(hotfixes)} hotfix-like merged PR(s) in period — "
            "responsiveness signal, not a quality penalty."
        )

    if not signals:
        signals.append("No automated alerts this period — review tables for detail.")

    return signals


def build_json_export(data: ReportData) -> dict[str, Any]:
    summary = executive_summary(data)
    weekly = compute_weekly_merged(data)
    weeks = all_weeks_in_range(data.since, data.until)
    team_counts = [weekly.get(wk, {}).get("_team", 0) for wk in weeks]
    rolling = rolling_avg([float(c) for c in team_counts], 4)

    weekly_rows = []
    for i, wk in enumerate(weeks):
        row = weekly.get(wk, {})
        weekly_rows.append({
            "week": wk,
            "merged_team": row.get("_team", 0),
            "rolling_4wk_avg": rolling[i],
            **{repo: row.get(f"_repo:{repo}", 0) for repo in data.roster.repos},
        })

    short_repos, matrix = repo_distribution_matrix(data)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executive_summary": summary,
        "developer_identities": developer_identities(data),
        "weekly_throughput": weekly_rows,
        "developer_throughput": developer_throughput(data),
        "lead_time_monthly_team": lead_time_monthly_team(data),
        "lead_time_weekly_team": lead_time_weekly_team(data),
        "lead_time_by_developer": lead_time_by_developer(data),
        "pr_cycle_time_monthly_team": pr_cycle_time_monthly_team(data),
        "pr_cycle_time_weekly_team": pr_cycle_time_weekly_team(data),
        "pr_cycle_time_by_developer": pr_cycle_time_by_developer(data),
        "research_appendix": research_appendix(data),
        "batch_size_team": batch_size_team(data),
        "batch_size_by_developer": batch_size_by_developer(data),
        "large_batch_inventory": large_batch_inventory(data),
        "review_flow_team": review_flow_team(data),
        "review_flow_by_author": review_flow_by_author(data),
        "review_flow_by_reviewer": review_flow_by_reviewer(data),
        "stale_prs": compute_stale_prs(data),
        "closure_outcomes": closure_outcomes(data),
        "repo_distribution": {"repos": short_repos, "rows": matrix},
        "signals": generate_signals(data, summary),
    }
