"""GitHub CLI wrapper for fetching pull request data."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def gh_api(path: str, *, retries: int = 4) -> Any:
    """Call `gh api` and return parsed JSON with rate-limit backoff."""
    delay = 2.0
    last_error: Exception | None = None
    for attempt in range(retries):
        result = subprocess.run(
            ["gh", "api", path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)

        stderr = result.stderr or result.stdout or ""
        last_error = RuntimeError(f"gh api {path} failed: {stderr.strip()}")
        if "rate limit" in stderr.lower() or "403" in stderr or "429" in stderr:
            time.sleep(delay)
            delay *= 2
            continue
        raise last_error
    raise last_error or RuntimeError(f"gh api {path} failed after retries")


def check_gh_auth() -> None:
    result = subprocess.run(
        ["gh", "auth", "status", "-h", "github.com"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "GitHub CLI is not authenticated. Run: gh auth login"
        )


@dataclass
class PullRequest:
    repo: str
    number: int
    author_login: str
    title: str
    url: str
    state: str
    draft: bool
    created_at: datetime | None
    updated_at: datetime | None
    closed_at: datetime | None
    merged_at: datetime | None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    head_ref: str = ""
    first_commit_at: datetime | None = None
    reviews: list[dict[str, Any]] = field(default_factory=list)

    @property
    def lines_changed(self) -> int:
        return self.additions + self.deletions

    @property
    def is_merged(self) -> bool:
        return self.merged_at is not None

    @property
    def is_research(self) -> bool:
        title_upper = self.title.upper()
        return "[DO NOT MERGE]" in title_upper or "DO NOT MERGE" in title_upper

    @property
    def is_bot(self) -> bool:
        login = self.author_login.lower()
        return "[bot]" in login or login.endswith("-bot")


def _normalize_pr(repo: str, raw: dict[str, Any], state: str) -> PullRequest:
    user = raw.get("user") or {}
    return PullRequest(
        repo=repo,
        number=raw["number"],
        author_login=user.get("login") or "",
        title=raw.get("title") or "",
        url=raw.get("html_url") or "",
        state=state,
        draft=bool(raw.get("draft")),
        created_at=parse_dt(raw.get("created_at")),
        updated_at=parse_dt(raw.get("updated_at")),
        closed_at=parse_dt(raw.get("closed_at")),
        merged_at=parse_dt(raw.get("merged_at")),
        head_ref=(raw.get("head") or {}).get("ref") or "",
    )


def fetch_prs_for_repo(
    org: str,
    repo: str,
    *,
    state: str,
    since: datetime,
    on_progress: Callable[[str], None] | None = None,
) -> list[PullRequest]:
    """Paginate pulls for a repo. For closed, stop when closed_at < since."""
    prs: list[PullRequest] = []
    page = 1
    while True:
        if on_progress:
            on_progress(f"  {repo} ({state}) page {page}")
        path = (
            f"repos/{org}/{repo}/pulls"
            f"?state={state}&sort=updated&direction=desc&per_page=100&page={page}"
        )
        batch = gh_api(path)
        if not batch:
            break

        stop = False
        for raw in batch:
            pr = _normalize_pr(repo, raw, state)
            if state == "closed" and pr.closed_at and pr.closed_at < since:
                stop = True
                break
            prs.append(pr)

        if stop or len(batch) < 100:
            break
        page += 1
        if page > 200:
            break
    return prs


def fetch_all_prs(
    org: str,
    repos: list[str],
    since: datetime,
    on_progress: Callable[[str], None] | None = None,
) -> tuple[list[PullRequest], list[PullRequest]]:
    closed: list[PullRequest] = []
    open_prs: list[PullRequest] = []
    for repo in repos:
        if on_progress:
            on_progress(f"Fetching closed PRs: {repo}")
        closed.extend(fetch_prs_for_repo(org, repo, state="closed", since=since, on_progress=on_progress))
        if on_progress:
            on_progress(f"Fetching open PRs: {repo}")
        open_prs.extend(fetch_prs_for_repo(org, repo, state="open", since=since, on_progress=on_progress))
    return closed, open_prs


def _fetch_pr_detail(org: str, pr: PullRequest) -> PullRequest:
    path = f"repos/{org}/{pr.repo}/pulls/{pr.number}"
    detail = gh_api(path)
    pr.additions = int(detail.get("additions") or 0)
    pr.deletions = int(detail.get("deletions") or 0)
    pr.changed_files = int(detail.get("changed_files") or 0)
    return pr


def _fetch_pr_reviews(org: str, pr: PullRequest) -> PullRequest:
    path = f"repos/{org}/{pr.repo}/pulls/{pr.number}/reviews"
    reviews = gh_api(path)
    pr.reviews = reviews if isinstance(reviews, list) else []
    return pr


def _commit_author_date(raw: dict[str, Any]) -> datetime | None:
    commit = raw.get("commit") or {}
    author = commit.get("author") or {}
    return parse_dt(author.get("date"))


def _is_merge_commit(raw: dict[str, Any]) -> bool:
    parents = raw.get("parents") or []
    return len(parents) > 1


def earliest_first_commit_at(commits: list[dict[str, Any]]) -> datetime | None:
    """Earliest author date among non-merge commits; else earliest of any commit."""
    non_merge_dates = [
        dt for c in commits
        if not _is_merge_commit(c) and (dt := _commit_author_date(c)) is not None
    ]
    if non_merge_dates:
        return min(non_merge_dates)
    any_dates = [dt for c in commits if (dt := _commit_author_date(c)) is not None]
    return min(any_dates) if any_dates else None


def _fetch_pr_commits(org: str, pr: PullRequest) -> PullRequest:
    commits: list[dict[str, Any]] = []
    page = 1
    while True:
        path = (
            f"repos/{org}/{pr.repo}/pulls/{pr.number}/commits"
            f"?per_page=100&page={page}"
        )
        batch = gh_api(path)
        if not isinstance(batch, list) or not batch:
            break
        commits.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 50:
            break
    pr.first_commit_at = earliest_first_commit_at(commits)
    return pr


def enrich_prs(
    org: str,
    prs: list[PullRequest],
    *,
    concurrency: int = 8,
    on_progress: Callable[[str], None] | None = None,
) -> list[PullRequest]:
    """Fetch size fields, reviews, and first-commit timestamps for merged PRs."""
    if not prs:
        return prs

    total = len(prs)
    if on_progress:
        on_progress(f"Enriching {total} merged PRs (concurrency={concurrency})...")

    completed = 0

    def enrich_one(pr: PullRequest) -> PullRequest:
        nonlocal completed
        enriched = _fetch_pr_detail(org, pr)
        enriched = _fetch_pr_reviews(org, enriched)
        enriched = _fetch_pr_commits(org, enriched)
        completed += 1
        if on_progress and completed % 25 == 0:
            on_progress(f"  Enriched {completed}/{total}")
        return enriched

    results: list[PullRequest] = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(enrich_one, pr): pr for pr in prs}
        for future in as_completed(futures):
            results.append(future.result())

    if on_progress:
        on_progress(f"  Enriched {total}/{total}")
    return results


def log_progress(message: str) -> None:
    print(message, file=sys.stderr)
