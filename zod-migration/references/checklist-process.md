# Zod migration: process checklist

Read 'Always' at the start of the work; re-read each stage section when you reach that stage.

Quotes and sources: ~/Github/planning/zod-migration-skill/FEEDBACK-PROCESS.md

## Always

- [ ] **P53** Never `git add`, commit, push or merge unless John explicitly asks. Make changes locally, run type-check and tests, and leave everything unstaged for John to review.
- [ ] **P19** In plan mode, or when told not to make changes, investigate and report findings, then wait. Never implement before telling John the result.
- [ ] **P56** Stash unrelated local changes before starting. When John stops, redirects or narrows work, stash it (never reset or delete); revert only when he says "revert". If he says neither, stash.
- [ ] **P55** Rename or move files with `git mv` before editing so the diff shows a rename. If a move was done wrongly, restore the file and redo it with `git mv`.
- [ ] **P40** Actually run the repo's type-check and tests after changes, including on staged or changed files, and fix every remaining error before reporting done. Never infer or simulate a result.
- [ ] **P41** Run tests only through npm scripts (`npm test -- <path>`, `npm run test-individual -- <path>`, `npm run test`), never `npx jest`.
- [ ] **P45** At the end of implementation, list the issues you believe are real runtime bugs surfaced by parsing or typing, separately from ordinary type fixes.
- [ ] **P46** Fix type errors by improving the upstream type (-utils, -dao, SDK). A runtime guard added only to satisfy the checker is a last resort; report every one to John.
- [ ] **P21** ASK: for architecture, scope or placement decisions (including "extend the fixture or relax the schema"), present realistic options with tradeoffs and a recommendation, then let John choose.
- [ ] **P24** ASK: if a validation, contract or type error needs a large fix, stop and ask John before implementing it.
- [ ] **P67** Implement only the requested behaviour, with good tests. No extra capability and no unrequested behavioural change (for example new null-return guards) inside a typing or migration change.
- [ ] **P68** Leave unrelated code, schemas, doc fields and legacy patterns (for example nested loops) alone. Remove hand-written validation Zod now covers only when that is obvious and simple.
- [ ] **P52** Apply /dev-coding-practices, /typescript-type-safety (or /jsdoc for checkJs repos) and /test-code-quality while planning and implementing. When reviewing others' PRs, check whether shared zod-contracts types could replace local types or validation.
- [ ] **P48** Every finding or recommendation (including where a response parse should go) names the exact file, line and concrete change. Demonstrate any claimed crash with a reproducing test.
- [ ] **P50** When reporting `.d.ts` or type changes, say plainly for each consumer whether it is broken now or fixed now. No ambiguous "breaking" tables.
- [ ] **P51** Answer the exact question asked with concrete enumerations (for example type-only versus runtime usages, named consuming repos), not general advice.

## Stage 0-1: before starting and scoping

- [ ] **P54** Work on the branch John names, following the pattern `jdrodger/<TICKET>-type-safety-*`.
- [ ] **P6** Before proposing changes (especially to -dao or an SDK), read the Jira ticket, any earlier ticket or PR it references, and related open or merged PRs, and check your approach is consistent.
- [ ] **P4** Before introducing a pattern (tsconfig, test builders, DAO type folders, OpenAPI file, pipeline type-check), check the precedent repos and `.tours` guidance and align with them. Say so if you deviate.
- [ ] **P1** Before changing code in the slice, confirm route/API-level tests exist (ideally at least one integration test per endpoint) that would detect a behaviour change; add them if missing.
- [ ] **P2** Check existing tests for behaviour coverage and determinate, tight assertions; report gaps, including removable AI-added logic. Mutation testing (Stryker) runs locally only. Coverage improvements go in a separate PR before the refactor.
- [ ] **P3** When the slice touches OpenAPI-backed validation, generate the Swagger doc before changes, regenerate it afterwards, and report differences (there should be none, or only irrelevant ones).
- [ ] **P8** ASK: identify a specific bounded slice, present it, and implement nothing until John confirms the scope.
- [ ] **P9** Propose low-risk slices still in development or not fully released (for example automation, NMI, yard), not a whole domain or a hot path like dispatch. When scope widens, narrow it, stashing work.
- [ ] **P10** For code already in production, include only endpoints and features you understand and can test manually, and extend automated coverage alongside. Delete the existing OpenAPI only after an entire repo is swapped.
- [ ] **P11** Keep the first iteration minimal: convert existing input schemas to Zod plus a derived type, or add one real runtime parse to prove the approach. Don't parse data that doesn't need it yet.
- [ ] **P14** When a pattern change is proposed for one endpoint, survey the rest of the repo and report where else it is warranted or already used. A survey is a report, not permission to implement.
- [ ] **P73** Write scope findings (for example whether setup or company-admin contain sizeable team code) into the Zod migration planning notes in `~/Github/planning`, tracking each team separately.

## Stage 2: contract plan

- [ ] **P20** ASK: write a plan before implementing (detailed if asked; sub-agents or several PRs allowed), ask John your open questions, and flag every place you substitute a custom approach for existing code.
- [ ] **P57** Plan the work as a small number of PRs (around 2-4), each self-contained, concise and tested, rather than one large PR.
- [ ] **P5** Before declaring or loosening any type, search `connex-utils-node-v4` zod-contracts, `connex-dao-node-v4`, and recent or open work in them, and report what exists and where.
- [ ] **P12** ASK: list every object in the slice with a proposed mode, strict by default; propose loose only for existing widely used canonical objects. John confirms all in one batch; re-ask on revisit only if evidence changed.
- [ ] **P25** ASK: if the slice has no zod-contracts domain folder yet, ask whether to create one now or where new and updated types should go, before putting types anywhere.
- [ ] **P13** ASK: throughout the work, look for constants that should move to -utils; recommend zod-contracts for greenfield or `-node-v4/src/constants` for legacy or risky code, and wait for confirmation.
- [ ] **P16** Every plan lists concrete opportunities to move schemas, types, constants or test data into -utils and to make existing schemas stricter, as proposals, not silent changes.
- [ ] **P26** ASK: before replacing JSON Schema/OpenAPI with `createDocument` in an area. In large services, keep the swap out of type or functional PRs or on a narrow proven slice, and describe the fuller scope.
- [ ] **P7** Before proposing to move zod-contracts into another package, verify it has a bump/publish workflow equivalent to utils-node and plan how to remove any circular dependency.
- [ ] **P22** ASK: before rolling out a new typing or testing pattern broadly, show example syntax or implement it in a single file for John to review.
- [ ] **P18** When scaffolding for a team, express later phases only as `declare`-style input/output shapes; do not implement them.
- [ ] **P27, P77** ASK: write DAO/DynamoDB or data-model changes affecting other teams as a separate request doc (alternatives, tradeoffs, recommendation; fields as TypeScript types with comments; concise; link only Epics) for engineering approval first.
- [ ] **P74** Put options to John as questions. Once he decides, plan docs keep only the chosen approach with no alternatives sections; record anything still unresolved in the docs.

## Stage 3-4: implement, propagate, iterate

- [ ] **P29** Make contract or type fixes in the owning repo (-utils, -dao, cds-resource-scheduler) and propagate to every affected repo while nothing is merged. Don't patch the consuming repo locally.
- [ ] **P30** Edit -utils directly and wire it locally into consumers for tests and type-check. John raises and merges the -utils PR first, then the others.
- [ ] **P31** Build -utils, copy the zod-contracts dist into `connex-dao-node-v4/node_modules`, then -utils and -dao into each app repo's `node_modules`. Never bump, publish, or edit consumer package.json versions.
- [ ] **P32** While `node_modules` holds a fresh local build of -utils or -dao, do not run `npm install` or `npm ci`.
- [ ] **P39** To try a shared UI library change (for example cds-resource-scheduler) in a consumer, link it locally (`file:` dependency or temporary import) instead of publishing, and confirm any deleted files are unused.
- [ ] **P34** When a -utils bump is needed, include the -utils improvements already discussed (not new ones) in that same change.
- [ ] **P35** After any -utils change, re-check -dao and every consuming app repo and PR, and report what needs updating.
- [ ] **P37** After propagating, verify imported types resolve from the package's type entry point (not just exist in `dist`), vanilla-JS runtime imports from zod-contracts still load, and included files and other consumers aren't hurt by risky partial canonical objects.
- [ ] **P36** Each iteration, create the strict tsconfig if missing and add that iteration's files to `include` at the right time; once a whole folder is covered, switch to a focused glob over the island.
- [ ] **P23** ASK: when type-check first reports errors for an iteration, stop, summarise them by category with a triaged list (and a plan if needed), and fix only what John chooses.
- [ ] **P47** After an error-fixing pass, remind John of every item left unresolved or decided by judgement (for example `@ts-expect-error` on invalid-request tests, loose DAO types left with comments).
- [ ] **P42** After each change, run the relevant tests locally to catch problems before CI. When John says the run is too slow, run only targeted checks during iteration.
- [ ] **P15** Within the confirmed domain or island, apply the shared types to all the domain's files, not only the endpoints the ticket touches.
- [ ] **P71** Give files used outside the strictly typed island minimal or no changes. Weigh any large relocation or refactor against growing the island incrementally, and recommend whether to do it.
- [ ] **P17** When a fix grows large, do the small part now and list the rest as suggested follow-up tickets; remind John to log them. A temporary local workaround is acceptable only with a recorded follow-up.
- [ ] **P64** Limit TypeScript to the Zod schema and `z.infer` files in `src/zod-contracts` of the shared package (no `-ts` twin, extra root tsconfig or unused scripts). App repos stay vanilla JS with JSDoc and checkJs.
- [ ] **P65** Don't add `typescript` to app repo package.json; the single type-check script runs TypeScript v6 through `npx`. Keeping `@types/*` packages is fine.
- [ ] **P66** Before adding Zod, establish where runtime schemas are used. Add it to `dependencies` only there; type-only consumers (for example -dao) don't install it. Check -utils doesn't force Zod into unrelated consumers.
- [ ] **P69** Update existing handlers, endpoints, schemas and DAO entries (especially without backward-compatibility concerns) rather than creating parallel new ones.
- [ ] **P70** Every edit must do something needed. Don't re-add removed code unless demonstrably used, including through "magic" reads. Delete confirmed-unused code with all its references and tests.
- [ ] **P72** Add no bespoke error-formatting or BadRequest-mapping helpers. Call Zod inline; structured error handling comes later.
- [ ] **P76** Mark unresolved domain questions for colleagues, out-of-scope validation work, and types added locally that belong upstream with short code comments or TODOs, not guesses or implementations.
- [ ] **P75** When a transitional rollout technique is adopted (for example loose parsing of partial canonical read schemas), record in the zod-schema docs when to use it elsewhere and that it is removed later.

## Stage 5-7: review, tests, OpenAPI

- [ ] **P28** ASK: before removing validators or defensive code, report the realistic risk of removing each one and list other relaxed types or guards on the branch. A question is not an instruction to delete; keep guards that add value.
- [ ] **P43** Production type-check stays at 0 errors and existing tests keep passing. A pass scoped to test-file type errors changes only fixtures, mocks, builders and assertions without weakening types; report needed upstream fixes instead.
- [ ] **P3 (again, at stage 7)** Regenerate the OpenAPI document after the swap and report any differences from the stage 7 baseline. There should be none, or only descriptive metadata.
- [ ] **P63** Full review is the default. When John says he wants a PR closed quickly, review for correctness only; don't block on duplicated code or missing JSDoc types.

## Handoff and PRs

- [ ] **P44** Before declaring done, confirm every intended file is present and nothing extra is in the diff, re-run the full tests and type-check locally, and report newly type-checked files with before/after error counts.
- [ ] **P49** Assess bot or reviewer PR feedback for validity and report to John before acting on it.
- [ ] **P60** ASK: keep each PR within its agreed scope. In feature PRs, move churn-causing type updates to a follow-up unless John agrees; on type-safety branches they stay. Re-examine large diffs for simpler approaches.
- [ ] **P58** Put agreed follow-up work on new branches created from the current branches, so they become stacked follow-up PRs.
- [ ] **P59** An initial scaffolding PR contains only CI/CD, very basic Zod schemas and types, and minimal scaffolding; placeholder folders (fixtures, constants) hold only `.gitkeep`.
- [ ] **P61** Compiled `.js` and `.d.ts` output from `src/zod-contracts` is built by the pipeline and not added to PRs.
- [ ] **P62** Wire lint, type-check and format into CI via one reusable opt-in cds-workflow workflow (config in cds-dev-quality-tools), aligned with dispatch-service, no duplicate type-check, as a separate follow-up PR.
- [ ] **P78** A -utils branch that adds or changes contracts includes one consumer-facing bullet under `Unreleased` in CHANGELOG.md before merge.
- [ ] **P33** Publishing is John's job, in order: -utils, then -dao, then app repos. Don't start downstream changes that depend on an unpublished version; after John publishes, update the downstream branch.
- [ ] **P38** After a -utils publish, confirm it works with small changes in two repos: one that installs Zod and uses a schema for real, one type-only. Avoid high-profile repos such as the AWS SDK.
