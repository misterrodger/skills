# Context staleness

## Jira (`pr-reviews/context/tickets/<KEY>/`)

1. Always call Atlassian MCP `getJiraIssue` for keys in the current run.
2. Compare remote `fields.updated` to `meta.json.jiraUpdated`.
3. Refresh `issue.md` + `meta.json` when updated/status/summary/AC changed; otherwise reuse file and note `reused`.

`meta.json` shape:

```json
{
  "jiraKey": "CARBON-1234",
  "fetchedAt": "ISO-8601",
  "jiraUpdated": "ISO-8601",
  "jiraStatus": "In Progress",
  "confluencePageIds": [],
  "linkedPrHeadShas": {}
}
```

## Confluence

Refresh when page `version` > cached version, or cache missing.

## Approved PR deep review

Do not fetch a full diff or deep-rewrite cluster Markdown during proposal mode. After John selects a review, refresh readiness and Jira context, then deep-rewrite cluster MD when any of:

- No prior `lastDeepReviewSha` for that PR
- Current `headSha` ≠ `lastDeepReviewSha`
- Jira AC text changed since last deep review

Otherwise carry forward prior cluster MD and refresh only the Readiness section.

Set `lastDeepReviewAt`, `lastDeepReviewSha`, `lastSpotCheckAt`, and `lastSpotCheckSha` only after the corresponding selected review completes.

## Approved comment fingerprints

Before an approved nudge or senior mention, refresh readiness and recheck its gate. Skip re-nudge within `strictNudgeCooldownHours` if the posted label fingerprint is unchanged since `lastStrictNudgeAt`. Apply the equivalent senior-tag check to `lastSeniorTagAt` and `seniorTagFingerprint`. Proposals do not update these fields.
