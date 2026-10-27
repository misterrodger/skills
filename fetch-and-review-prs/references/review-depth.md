# Review depth

Default daily pass covers every author in `team.json`. Depth depends on `reviewDepth`.

## Depths

| Depth | Who | What a default run does |
|-------|-----|-------------------------|
| `full` | Pod 19 seniors, Pod 15 seniors, Jonathan Harrison | Readiness and a proposed deep review when `headSha` changed or no prior review exists; acceptance-criteria freshness is checked if selected |
| `triage` | Other Pod 19 and Pod 15 developers | Open-PR listing plus basic readiness. No diff, no review-skill stack, no cluster file |

Pod 15 seniors Isis Salamanca and Sulakshana Sawsarikar receive full-depth proposals. Sulakshana's authored PRs are included only when their repository matches her `repoScope`; her reviews count as senior approvals across Pod 15 regardless of repository. Propose other Pod 15 PRs for full review only when a triage card shows a principal-level risk (see Escalation). Review them when the user explicitly asks.

## Summary order

1. Pod 19 — full reviews, then triage cards
2. Peer — Jonathan, full reviews
3. Pod 15 — senior full-depth proposals, then triage cards

Within a pod, list seniors before other developers, then order PRs by bucket: ready, blocked, stale watch, very stale.

## Triage card (basic information)

One row or short block per open PR. Include:

- Author, pod, role
- Repo, number, title, URL
- Draft or ready
- Created age and days since update
- CI (`green` / `red` / `pending` / `unknown`) and failing check names when red
- Non-author approvals, `CHANGES_REQUESTED`, unresolved threads
- Merge conflicts
- Jira key from title, body, or branch when present
- Readiness bucket

Do not summarize the diff. Do not fetch Jira unless a key is already obvious and a one-line status helps the listing.

## Escalation proposals

Call these out in the proposal queue. Do not deep-review them on a default run.

- Very stale
- Merge conflicts
- CI red
- `CHANGES_REQUESTED` with no newer approval
- Open more than `staleOpenDays` with zero non-author approvals

## Overrides for a single run

| User says | Effect |
|-----------|--------|
| Review / full review \<name or PR\> | Explicitly authorize full review for that selected scope after revalidation |
| Review / full review Pod 15 (or Pod 19) | Explicitly authorize eligible full reviews for every author in that pod after revalidation |
| Only / just \<name or pod\> | Limit the run to those authors |
| Triage only / listing only | Proposal mode; no GitHub comments or deep reviews |
| Extra names with no “only” | Additive, as in author resolution |

“Review PRs from Marcos” is explicit authorization to full-review Marcos's eligible PRs. A plain daily pass that lists Marcos only proposes reviews.

## What full review is for

Use full review to check judgment: design, failure handling, tests, API contracts, and whether the change matches the ticket. Seniors multiply whatever standard you spend time on. Triage exists so the rest of the queue stays visible without becoming the bottleneck.
