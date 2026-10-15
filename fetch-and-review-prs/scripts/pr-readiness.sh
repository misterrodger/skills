#!/usr/bin/env bash
# Collect CI, review threads, file signals, and nudge labels for one PR.
# Usage: pr-readiness.sh OWNER/REPO PR_NUMBER
# Prints one JSON object to stdout.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: pr-readiness.sh OWNER/REPO PR_NUMBER" >&2
  exit 1
fi

repo="$1"
pr="$2"

if ! command -v jq >/dev/null; then
  echo '{"error":"jq required"}' >&2
  exit 1
fi

team_json="$(cd "$(dirname "$0")/../references" && pwd)/team.json"

pr_json="$(gh pr view "$pr" --repo "$repo" --json number,title,url,author,isDraft,createdAt,updatedAt,headRefOid,baseRefName,mergeable,mergeStateStatus,reviewDecision,reviews,latestReviews,additions,deletions,changedFiles,files,commits 2>/dev/null || true)"
if [[ -z "$pr_json" ]]; then
  jq -n --arg repo "$repo" --argjson pr "$pr" '{repo:$repo,number:$pr,error:"pr_view_failed"}'
  exit 0
fi

checks_raw="$(gh pr checks "$pr" --repo "$repo" 2>/dev/null || true)"
ci_status="unknown"
ci_detail=""
if [[ -n "$checks_raw" ]]; then
  if echo "$checks_raw" | grep -Eq $'\t(fail|failure|cancelled|timed_out|action_required)\t'; then
    ci_status="red"
  elif echo "$checks_raw" | grep -Eq $'\t(pending|queued|in_progress|expected)\t'; then
    ci_status="pending"
  elif echo "$checks_raw" | grep -Eq $'\t(pass|success|skipping|neutral|skip)\t'; then
    ci_status="green"
  fi
  ci_detail="$(echo "$checks_raw" | awk -F'\t' '$2 ~ /fail|failure|cancelled|timed_out|action_required|pending|queued|in_progress/ {print $1 ":" $2}' | paste -sd ', ' - || true)"
fi

owner="${repo%%/*}"
name="${repo#*/}"
threads_json="$(gh api graphql -f query='
query($owner:String!,$name:String!,$number:Int!) {
  repository(owner:$owner,name:$name) {
    pullRequest(number:$number) {
      reviewThreads(first:100) {
        nodes {
          isResolved
          isOutdated
          resolvedBy { login }
          comments(first:8) {
            nodes { author { login } body }
          }
        }
      }
    }
  }
}' -f owner="$owner" -f name="$name" -F number="$pr" 2>/dev/null || echo '{}')"

threads_nodes="$(printf '%s' "$threads_json" | jq -c '.data.repository.pullRequest.reviewThreads.nodes // []')"
thresholds="$(jq -c '.thresholds' "$team_json")"

jq -n \
  --argjson pr "$pr_json" \
  --arg repo "$repo" \
  --arg ciStatus "$ci_status" \
  --arg ciDetail "$ci_detail" \
  --argjson threads "$threads_nodes" \
  --argjson thresholds "$thresholds" \
  --arg fetchedAt "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  --argjson now "$(date -u +%s)" \
  '
  def is_bot:
    ascii_downcase | test("bugbot|cursor\\[bot\\]|github-actions");
  def is_i18n:
    ascii_downcase
    | test("/i18n/|/locales?/|/l10n/|/translations?/|/lang/")
      or test("\\.(po|xliff|xlf)$")
      or test("(^|/)(en|es|fr|pt|de|nl|it|pl|sv|da|fi|nb|ja|zh|ko)(-[a-z]{2})?\\.(json|ya?ml)$");
  def hot_groups($path):
    [
      (if ($path | test("openapi|swagger|\\.graphql|/(api|schema)/|schema\\.(json|ya?ml|ts)$"; "i")) then "api-schema" else empty end),
      (if ($path | test("/(auth|permissions?|rbac|polic(y|ies))/"; "i")) then "auth" else empty end),
      (if ($path | test("/migrations?/"; "i")) then "migration" else empty end),
      (if ($path | test("feature-?flags?|/flags/"; "i")) then "feature-flag" else empty end),
      (if ($path | test("/generated/|\\.generated\\."; "i")) then "generated-client" else empty end)
    ];
  def excerpt:
    gsub("\\s+"; " ") | .[0:240];
  def days($iso):
    if ($iso | length) == 0 then null
    else ((($now - ($iso | fromdateiso8601)) / 86400) | floor)
    end;

  def latest: (.latestReviews // .reviews // []);
  def author: .author.login;
  def files: (.files // []);
  def non_i18n: files | map(select((.path // "") | is_i18n | not));
  def i18n_files: files | map(select((.path // "") | is_i18n));

  $pr
  | author as $author
  | ($threads // []) as $nodes
  | [
      $nodes[]
      | . as $thread
      | ($thread.comments.nodes // []) as $comments
      | {
          resolved: ($thread.isResolved == true),
          outdated: ($thread.isOutdated == true),
          resolvedBy: ($thread.resolvedBy.login // ""),
          firstAuthor: ($comments[0].author.login // ""),
          authorComments: [$comments[] | select((.author.login // "") == $author)] | length,
          otherComments: [$comments[] | select((.author.login // "") != $author and (.author.login // "") != "")] | length,
          lastOtherAfterAuthor: (
            (([$comments | to_entries[] | select((.value.author.login // "") != $author) | .key] | max) // -1)
            > (([$comments | to_entries[] | select((.value.author.login // "") == $author) | .key] | max) // -1)
          ),
          excerpt: (($comments[0].body // "") | excerpt)
        }
      | .premature = (
          .resolved and (.outdated | not) and .resolvedBy == $author and .otherComments > 0
          and (.authorComments == 0 or (.lastOtherAfterAuthor | not))
        )
    ] as $threadRows
  | (non_i18n) as $codeFiles
  | (i18n_files) as $localeFiles
  | (($codeFiles | map((.additions // 0) + (.deletions // 0)) | add) // 0) as $codeLines
  | ([$codeFiles[].path | hot_groups(.)[]] | unique) as $hot
  | ((files | length) > 0 and ($codeFiles | length) == 0) as $i18nOnly
  | {
      count: [latest[] | select(.state == "APPROVED" and .author.login != $author)] | length,
      logins: [latest[] | select(.state == "APPROVED" and .author.login != $author) | .author.login] | unique,
      changesRequested: [latest[] | select(.state == "CHANGES_REQUESTED")] | length
    } as $approvals
  | ([latest[] | select((.author.login // "") | is_bot)] | last) as $bugbotReview
  | (if $bugbotReview == null then "none"
     elif (($bugbotReview.body // "") | test("high([ -])risk|risk[^.]{0,40}high"; "i")) then "high"
     elif (($bugbotReview.body // "") | test("medium([ -])risk|risk[^.]{0,40}medium"; "i")) then "medium"
     elif (($bugbotReview.body // "") | test("low([ -])risk|risk[^.]{0,40}low"; "i")) then "low"
     else "unknown"
     end) as $bugbotRisk
  | (days($pr.createdAt)) as $openDays
  | (days($pr.updatedAt)) as $quietDays
  | (if $pr.isDraft then []
     else
       [
         (if $ciStatus == "red" then "red pipeline" else empty end),
         (if $ciStatus == "pending" then "pending pipeline" else empty end),
         (if ($pr.mergeable == "CONFLICTING" or $pr.mergeStateStatus == "DIRTY") then "conflicts" else empty end),
         (if ([$threadRows[] | select(.resolved | not)] | length) > 0 then "unresolved comments" else empty end),
         (if $approvals.changesRequested > 0 then "changes requested" else empty end),
         (if ($openDays >= $thresholds.staleOpenDays or $quietDays >= $thresholds.staleUpdateDays) then "stale" else empty end)
       ]
     end) as $nudges
  | [
      (if $bugbotRisk == "high" then "bugbot-high" else empty end),
      (if ($hot | length) > 0 then "hot-path" else empty end),
      (if ($codeFiles | length) >= $thresholds.largeNonI18nFiles or $codeLines >= $thresholds.largeNonI18nLines then "large-diff" else empty end),
      (if ([$threadRows[] | select(.premature)] | length) > 0 then "premature-resolve" else empty end)
    ] as $baseReasons
  | (if $bugbotRisk == "medium" and ($baseReasons | length) > 0 then $baseReasons + ["bugbot-medium"] else $baseReasons end) as $reasons
  | {
      repo: $repo,
      number: $pr.number,
      title: $pr.title,
      url: $pr.url,
      author: $author,
      isDraft: $pr.isDraft,
      createdAt: $pr.createdAt,
      updatedAt: $pr.updatedAt,
      headSha: $pr.headRefOid,
      baseRef: $pr.baseRefName,
      mergeable: $pr.mergeable,
      mergeStateStatus: $pr.mergeStateStatus,
      reviewDecision: $pr.reviewDecision,
      additions: $pr.additions,
      deletions: $pr.deletions,
      changedFiles: $pr.changedFiles,
      openDays: $openDays,
      quietDays: $quietDays,
      ci: { status: $ciStatus, detail: $ciDetail },
      reviewThreads: {
        total: ($threadRows | length),
        unresolved: ([$threadRows[] | select(.resolved | not)] | length),
        resolved: ([$threadRows[] | select(.resolved)] | length),
        unresolvedBugbot: ([$threadRows[] | select((.resolved | not) and (.firstAuthor | is_bot))] | length),
        prematureResolve: (([$threadRows[] | select(.premature)] | length) > 0),
        prematureCount: ([$threadRows[] | select(.premature)] | length),
        resolvedExcerpts: [
          $threadRows[]
          | select(.resolved)
          | { author: .firstAuthor, resolvedBy: .resolvedBy, outdated: .outdated, premature: .premature, excerpt: .excerpt }
        ] | .[0:20]
      },
      approvals: $approvals,
      bugbot: {
        present: ($bugbotReview != null),
        risk: $bugbotRisk,
        excerpt: (($bugbotReview // {} | .body // "") | excerpt)
      },
      files: {
        i18nOnly: $i18nOnly,
        i18nCount: ($localeFiles | length),
        nonI18nCount: ($codeFiles | length),
        nonI18nLines: $codeLines,
        hotPaths: $hot,
        nonI18nPaths: [$codeFiles[].path] | .[0:40]
      },
      commitCount: (($pr.commits // []) | length),
      commitMessages: [($pr.commits // [])[].messageHeadline] | .[0:12],
      nudges: $nudges,
      escalation: {
        recommend: (($reasons | length) > 0),
        reasons: $reasons
      },
      fetchedAt: $fetchedAt
    }
  '
