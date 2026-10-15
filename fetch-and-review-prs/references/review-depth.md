# Review depth

Default daily pass covers every author in `team.json`. Depth depends on `reviewDepth`.

## Depths

| Depth | Who | What a default run does |
|-------|-----|-------------------------|
| `full` | Pod 19 seniors, Jonathan Harrison | Readiness, Jira context, and a deep cluster review when `headSha` or acceptance criteria changed |
| `triage` | Other Pod 19 developers, all of Pod 15 | Open-PR listing plus basic readiness. No diff, no review-skill stack, no cluster file |

Pod 15 stays on triage even though Isis Salamanca is a senior. She is the strong senior on a lower-priority pod. Promote a Pod 15 PR to `full` only when the user asks, or when a triage card shows a principal-level risk (see Escalation).

## Summary order

1. Pod 19 — full reviews, then triage cards
2. Peer — Jonathan, full reviews
3. Pod 15 — triage cards

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

## Escalation (still triage unless the user asks for a review)

Call these out at the top of the chat summary. Do not deep-review them on a default run.

- Very stale
- Merge conflicts
- CI red
- `CHANGES_REQUESTED` with no newer approval
- Open more than `staleOpenDays` with zero non-author approvals

## Overrides for a single run

| User says | Effect |
|-----------|--------|
| Review / full review \<name\> | `full` for that author this run, even if their default is `triage` |
| Review / full review Pod 15 (or Pod 19) | `full` for every author in that pod this run |
| Only / just \<name or pod\> | Limit the run to those authors |
| Triage only / listing only | No deep reviews; triage cards for everyone included |
| Extra names with no “only” | Additive, as in author resolution |

“Review PRs from Marcos” means a full review of Marcos for that run.

## What full review is for

Use full review to check judgment: design, failure handling, tests, API contracts, and whether the change matches the ticket. Seniors multiply whatever standard you spend time on. Triage exists so the rest of the queue stays visible without becoming the bottleneck.
