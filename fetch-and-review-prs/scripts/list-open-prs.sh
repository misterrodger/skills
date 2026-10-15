#!/usr/bin/env bash
# Non-interactive twin of ~/.zshrc gh_prs_review_pretty
# Usage: list-open-prs.sh AUTHOR [AUTHOR ...]
# Prints TSV: repo<TAB>#number<TAB>author<TAB>title<TAB>url<TAB>updatedAt<TAB>createdAt
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: list-open-prs.sh AUTHOR [AUTHOR ...]" >&2
  exit 1
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

for user in "$@"; do
  gh search prs --author "$user" --state=open --limit 100 \
    --json repository,number,title,author,url,updatedAt,createdAt \
    --jq '.[] | [
      .repository.nameWithOwner,
      ("#" + (.number|tostring)),
      .author.login,
      .title,
      .url,
      .updatedAt,
      .createdAt
    ] | @tsv' || true
done | sort -u > "$tmp"

if [[ ! -s "$tmp" ]]; then
  echo "No matching PRs found." >&2
  exit 0
fi

cat "$tmp"
