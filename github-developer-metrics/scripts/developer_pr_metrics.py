#!/usr/bin/env python3
"""CLI entrypoint for GitHub developer PR metrics reports."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from gh_client import (  # noqa: E402
    check_gh_auth,
    enrich_prs,
    fetch_all_prs,
    log_progress,
)
from metrics import (  # noqa: E402
    RosterConfig,
    build_json_export,
    build_report_data,
)
from report_md import build_markdown_report  # noqa: E402


DEFAULT_OUTPUT_DIR = Path.home() / ".cursor" / "output" / "github-developer-metrics"
DEFAULT_ROSTER = SKILL_ROOT / "references" / "developer-roster.json"


def parse_date(value: str) -> datetime:
    dt = datetime.strptime(value, "%Y-%m-%d")
    return dt.replace(tzinfo=timezone.utc)


def load_roster(path: Path) -> RosterConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    required = ["org", "repos", "developers"]
    for key in required:
        if key not in raw:
            raise ValueError(f"Roster missing required key: {key}")
    return RosterConfig(
        org=raw["org"],
        repos=raw["repos"],
        developers=raw["developers"],
        exclude_logins=raw.get("exclude_logins", []),
        stale_open_days=int(raw.get("stale_open_days", 21)),
        stale_update_days=int(raw.get("stale_update_days", 14)),
    )


def default_since(until: datetime) -> datetime:
    return until - timedelta(weeks=13)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate DORA/Accelerate-aligned developer PR metrics reports via gh API.",
    )
    parser.add_argument(
        "--since",
        help="Period start (YYYY-MM-DD). Default: 13 weeks before --until.",
    )
    parser.add_argument(
        "--until",
        help="Period end (YYYY-MM-DD). Default: today (UTC).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--roster",
        type=Path,
        default=DEFAULT_ROSTER,
        help="Path to developer-roster.json",
    )
    parser.add_argument(
        "--enrich-concurrency",
        type=int,
        default=8,
        help="Parallel PR enrichment workers (default: 8)",
    )
    parser.add_argument(
        "--format",
        choices=["md", "json", "both"],
        default="both",
        help="Output format (default: both)",
    )
    parser.add_argument(
        "--report-name",
        help="Base filename without extension (default: report-YYYY-MM-DD)",
    )
    parser.add_argument(
        "--enrich-all",
        action="store_true",
        help="Enrich all merged PRs in period (slow). Default: roster authors only.",
    )
    args = parser.parse_args()

    if sys.version_info < (3, 10):
        print("Python 3.10+ required.", file=sys.stderr)
        return 1

    check_gh_auth()
    roster = load_roster(args.roster)

    until = parse_date(args.until) if args.until else datetime.now(timezone.utc)
    since = parse_date(args.since) if args.since else default_since(until)

    if since >= until:
        print("--since must be before --until", file=sys.stderr)
        return 1

    log_progress(f"Period: {since.date()} → {until.date()}")
    log_progress(f"Repos: {', '.join(roster.repos)}")

    closed_prs, open_prs = fetch_all_prs(
        roster.org,
        roster.repos,
        since,
        on_progress=log_progress,
    )
    log_progress(f"Fetched {len(closed_prs)} closed and {len(open_prs)} open PRs (raw)")

    merged_candidates = [
        p for p in closed_prs
        if p.merged_at and since <= p.merged_at <= until + timedelta(days=1)
    ]
    if not args.enrich_all:
        merged_candidates = [
            p for p in merged_candidates
            if p.author_login in roster.dev_logins
        ]
        log_progress(
            f"Enriching {len(merged_candidates)} roster-author merged PRs "
            "(use --enrich-all for every author)"
        )
    enriched = enrich_prs(
        roster.org,
        merged_candidates,
        concurrency=args.enrich_concurrency,
        on_progress=log_progress,
    )

    report_data = build_report_data(
        roster,
        closed_prs,
        open_prs,
        enriched,
        since,
        until,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    base_name = args.report_name or f"report-{until.date().isoformat()}"
    md_path = args.output_dir / f"{base_name}.md"
    json_path = args.output_dir / f"{base_name}.json"
    latest_path = args.output_dir / "latest.md"
    latest_json_path = args.output_dir / "latest.json"

    if args.format in ("md", "both"):
        md_content = build_markdown_report(report_data, SKILL_ROOT)
        md_path.write_text(md_content, encoding="utf-8")
        shutil.copy2(md_path, latest_path)
        log_progress(f"Wrote {md_path}")

    if args.format in ("json", "both"):
        export = build_json_export(report_data)
        json_path.write_text(json.dumps(export, indent=2, default=str), encoding="utf-8")
        shutil.copy2(json_path, latest_json_path)
        log_progress(f"Wrote {json_path}")

    print(f"Report written to {args.output_dir}")
    if args.format in ("md", "both"):
        print(f"  Markdown: {md_path}")
        print(f"  Latest:   {latest_path}")
    if args.format in ("json", "both"):
        print(f"  JSON:     {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
