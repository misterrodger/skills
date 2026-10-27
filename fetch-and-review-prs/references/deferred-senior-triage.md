# Deferred: Senior/Lead PR triage

i18n-only pull requests are outside principal review. Locale changes often touch many files and often contain omissions, and that review belongs with the pod seniors and leads.

Do not build the Senior/Lead triage skill from this note. When that skill is written, start from:

- `files.i18nOnly` from `scripts/pr-readiness.sh`
- the day's deferred-i18n list in `pr-reviews/YYYY-MM-DD/INDEX.md`
- the same resolved-comment excerpts, because a translation PR can hide a still-valid comment
- the senior-tag rule, which proposes asking the pod seniors to review a ready i18n-only PR that they have not approved and that `principal.login` has not approved

Until then, record each i18n-only PR and leave it out of John's full reviews, spot-checks, escalation, and GitHub nudges.
