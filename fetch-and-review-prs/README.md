# Fetch and Review PRs

Team PR triage + deep review into `~/Github/pr-reviews/`.

## Invoke

- `/fetch-and-review-prs` — all default authors, at their configured depth
- “Review PRs from \<name\>” — additive, or only those people if the request says only/just
- “Fully review \<name/pod/PR\>” — deep-review even when the author is triage
- `strict-nudge` posts the same GitHub comments as a normal run

## Default review groups

| Group | Default full reviews | Default triage |
|-------|----------------------|----------------|
| Pod 19 — Sales and Quoting, and Pricing (primary) | Fabian Martinez, Sebastian Vasquez, Juan Pablo Betancourt, Andres Uribe | Marcos Aguilera, Chad Lott, Vladimir Koshcheyev |
| Pod 15 — Scale Ticketing (secondary) | Isis Salamanca | Juan David Varela, Francisco de Freitas, Edwar Figueroa |
| Peer | Jonathan Harrison | — |

A full review is repeated when the latest commit or the Jira acceptance criteria change. An unchanged diff is not re-read.

Triage PRs get readiness, short nudge labels, and cheap file, comment, and Bugbot signals. A full review follows only when a skim confirms the signal, a 7-day spot-check is due, or John asks. i18n-only PRs are listed and left for a later Senior/Lead triage skill.

A triage PR that is green, has no approval from a senior on its pod, and has no approval from `principal.login` gets a GitHub comment mentioning those seniors. Skip that mention when the principal has already approved. Nudge labels are posted on the GitHub PR in the same run. Neither comment goes on the Jira ticket.

## What you get

| Artifact | Updated |
|----------|---------|
| `pr-reviews/YYYY-MM-DD/INDEX.md` | Every run |
| `pr-reviews/YYYY-MM-DD/readiness.md` | Every run |
| Cluster `*.md` | When a full review is required |
| `state/prs/*.json` | Every run |
| GitHub nudge comment | Every run, when the PR has nudge labels |
| GitHub senior mention | When a ready triage PR has no senior or principal approval |

## Related skills

- `/command-alkon-best-practices`
- `pr-review`, `dev-coding-practices`, `typescript-type-safety`, `test-code-quality`
