# Checklist: schemas, types, DAO, constants, checkJs and style

Go through every line below against the diff and record each finding as fix-now, ask John, or log.

Quotes and sources: ~/Github/planning/zod-migration-skill/FEEDBACK-SCHEMAS-AND-TYPES.md

## 1. Source of truth and where types live

- [ ] **S1** Every new or changed schema or type is defined first in `connex-utils-node-v4/src/zod-contracts/<domain>`, then flows through `-dao` into app code. Nothing is defined first downstream.
- [ ] **S2** App repos (-service, -exp, bm-yard, frontend, api-docs) define no Zod schemas or inline request/response types. They import from zod-contracts and may call `.parse`/`safeParse` on imported schemas.
- [ ] **S3** Before declaring any type, search -utils (including open PRs), -dao and package-provided declarations; reuse or derive from what exists.
- [ ] **S4** Wrong, missing or loose types are fixed in the owning repo (zod-contracts, -dao, connex-sdk-node-v4, cds-resource-scheduler) and propagated. No local patch, cast or redefinition in consumers.
- [ ] **S5** Each entity's schemas live in exactly one `zod-contracts/<domain>` folder, one domain per microservice slice. ASK: before creating a new domain folder or placing types elsewhere.
- [ ] **S6** Cross-domain primitives and canonical entities (date options, coerced numbers, address, jurisdiction, hours time, regexes) live in `zod-contracts/_common`, never `kernel`. Check other domains for an extractable canonical schema first.
- [ ] **S7** Shared code in `connex-asphalt-node-v4` that the migration touches moves into `connex-utils-node-v4` zod-contracts.
- [ ] **S8** -service, -exp (BFF and frontend) and shared UI libraries import the same zod-contracts schemas, types and constants; no parallel handwritten copies unless a stated tradeoff justifies one.
- [ ] **S9** The plan names concrete schemas, types and constants in consumer repos to move into utils.
- [ ] **S10** Everything placed in utils is used by more than one consumer. UI/editor-only types stay in the UI library, with label maps keyed by shared codes from utils.
- [ ] **S11** A shared-worthy type added locally because it is not yet in utils carries a `TODO` saying it should move to connex-utils.
- [ ] **S12** Boundary and type-helper files sit alongside production code, not under `test/boundary`. ASK: before a large relocation refactor; recommend whether it serves growing the island step by step.
- [ ] **S13** No JSDoc-only `types.js` files and no new types file for a small change. Add to the existing types file or `.d.ts`; export from the root index only if consumers need it.
- [ ] **S14** App repos add no facade or barrel `.d.ts` (e.g. `connex-dao-boundaries.d.ts`, `*-request.types.d.ts`). Import directly from domain subpaths. A narrow same-basename `.d.ts` beside legacy JS for island isolation is allowed.
- [ ] **S15** No large hand-written local typedefs not derived from Zod; derive from -utils or move there. ASK: if one stays local, confirm with John and state why.
- [ ] **S16** Every added field, enum value or schema traces to existing data or a stated requirement; remove invented ones.
- [ ] **S17** Every removed field, property or lookup is backed by evidence of its former use, and consumers such as the frontend were checked.
- [ ] **S18** In a dark or greenfield domain, shared types are applied across all of that domain's files in the island. In released or shared code, stay within the confirmed slice.

## 2. Composition and type utilities

- [ ] **S19** No `Pick`/`Omit`/`Partial` reshaping contract types in app code. Compose subsets in zod-contracts, preferring `.extend`; schema-level `.pick`/`.omit`/`.partial` are fine. Only sanctioned `Partial`: a test builder's `overrides` parameter.
- [ ] **S20** Domain variants of common objects are built from the `_common` schema, adding only fields that genuinely differ.
- [ ] **S21** Near-identical record variants share one schema and endpoint with a discriminator field; region- or jurisdiction-dependent shapes are discriminated unions with one Zod schema per variant.
- [ ] **S22** Existing schemas, endpoints and DAO entries are reused or extended rather than adding near-duplicates.
- [ ] **S23/S24** App-repo helpers get no `@template` generics or overloads. Generics are only for library code (connex-aws/dao wrappers, base-ui) where they carry the specific type and reduce downstream casts or guards.
- [ ] **S23** Overloads TypeScript collapses become one signature; parameters with alternative shapes use `|`, not `&`.

## 3. Strictness, optional and nullable

- [ ] **S25** Every schema is `z.strictObject`, consistently applied, required where evidence says required. ASK: before any non-strict schema (loose, open, compatibility-optional, legacy-mirroring); if approved, add a code comment, slice note and strictness-ledger entry.
- [ ] **S25** The existing JSON/OpenAPI schema is the first evidence for required and nullable fields. On revisit, ask John again only if something changed.
- [ ] **S26** Greenfield, dark or unreleased schemas: fields required unless clearly optional, no mostly-optional objects, no `unknown` or loose objects, no backward-compat branches, legacy fallbacks or coercion.
- [ ] **S27** Each pass lists concrete tightenings and questions every optional field. For legacy objects, a tightening lands only in its own commit, backed by evidence.
- [ ] **S28** Status and enum-like fields are literals or enums in the -utils schema; a deliberately narrow union is documented so widening needs an explicit type change.
- [ ] **S29** Optional fields use `.optional()` / `field?: T` with no `.nullable()`, `| null` or `| undefined` unless the runtime produces it; parameters don't accept both null and undefined unless callers pass both.
- [ ] **S30** Each `.nullable()`/`.nullish()` traces to the existing OpenAPI schema or real stored data; there, keep nullable rather than `.optional()`. In greenfield or dark code, prefer omission.
- [ ] **S31** For `.nullable().optional()` fields, consider a null-to-undefined transform and confirm its effect on the inferred type; on legacy objects this is a later tightening.
- [ ] **S32** No `.passthrough()` and no `additionalProperties: true`. `z.looseObject` only on an approved legacy partial read projection, applied directly to that schema, with a comment saying it is transitional.
- [ ] **S33** No type or schema is widened (`| string`, `| undefined`, new optional property, `??` fallback) to silence the checker; validate at the hinges and trust downstream.
- [ ] **S34/S127** ASK: before making a field optional to reduce churn. Every intentionally optional field has a one-line comment naming why and its source contract or the record variants lacking it.
- [ ] **S35** Where DAO defaults guarantee a value, make the persisted/read schema required and leave create-input fields as they are.
- [ ] **S36** No field becomes optional or nullable just because a fixture omits it. ASK: recommend per case whether to extend the fixture or fix the schema.

## 4. Zod style in zod-contracts

- [ ] **S37** zod-contracts export small composable schemas; `.transform` is fine, but no business logic in `.superRefine` or similar unless clearly justified. That logic stays in the app.
- [ ] **S38** No bespoke wrappers around Zod or zod-openapi (`closedObject`, `openObject`, `outcomeShape`, `registeredSchema`, `parseResponse`); use plain Zod and `createDocument`.
- [ ] **S39** A recurring value format gets a reusable primitive schema with real validation (e.g. `sha256Schema`), optionally branded, not a bare `z.string()`.
- [ ] **S40** Use Zod built-in validators or readable validation before raw regex. Retained regex and time schemas live in `_common`, non-trivial ones have tests as documentation, other-ticket work is a TODO.
- [ ] **S41** String-encoded booleans and numbers use `z.coerce`, not custom preprocess schemas; parsed types come from `z.output`.
- [ ] **S42** Generic and larger response transforms (projecting, reshaping, formatting) live in zod-contracts via `.transform` with `z.input`/`z.output`. Suggest app-side transforms to move. ASK: present parse-location options with tradeoffs.
- [ ] **S43** Shared schemas carry no `.meta()`/`.openapi()` id, description, example or name metadata; docs details go in the app's `createDocument`. Exception: mark deprecated properties with Zod `deprecated` metadata.
- [ ] **S44** Exported schemas are camelCase with a `Schema` suffix, never kebab-case or PascalCase.
- [ ] **S45** Zod object keys are unquoted unless syntax requires quotes.
- [ ] **S46** Schema-building code is declarative, with no imperative mutation plus casts.
- [ ] **S47** Small schema files are combined unless each is imported on its own somewhere.

## 5. Dependencies and packaging

- [ ] **S48** Each domain is its own sub-path (`connex-utils-node-v4/zod-contracts/dist/<domain>`); schemas and types are exported inline, no grouping objects or rename-on-destructure; consumers import at exactly that depth.
- [ ] **S49** Compiled zod-contracts `.js`/`.d.ts` are produced in the pipeline, not committed; consumers import only the `/zod-contracts` sub-path.
- [ ] **S50** TypeScript exists only as Zod schema and `z.infer` files inside `src/zod-contracts`: no `zod-contracts-ts` folder, nothing at repo root, no extra root tsconfig, no unused `prepare` script.
- [ ] **S51** Type-only consumers (e.g. -dao) have no `zod` dependency. List every runtime-schema use inside -utils. Verify a publish with one real-parsing consumer and one type-only consumer.
- [ ] **S52** Only runtime-parsing repos list `zod` under `dependencies`; `zod-openapi` is a devDependency; Zod versions and the -utils peer relationship are aligned. ASK: before forcing Zod onto an unrelated consumer.
- [ ] **S53** Before relocating contracts to another package, confirm it has a bump/publish workflow and a plan to remove any circular dependency with utils-node.
- [ ] **S54** Any type a consumer imports from an internal library is exported from the package's type entry point, not just present in `dist`.

## 6. DAO declarations

- [ ] **S55** Dependency direction is utils to dao to apps: -dao imports utils types and owns DAO methods, utils never imports -dao.
- [ ] **S56** DAO `.d.ts` files touched by the slice are updated using -utils types; DAO type folders sit in -dao; hand-written `.d.ts` types migrate to zod-contracts; app-repo DAO stubs move to -dao or are logged as follow-up.
- [ ] **S57/S58** DAO methods return specific contract-derived types, never `Promise<object>`, `any` or `any[]`; a possible `null` doesn't break the type; repeated query-result shapes share a common generic; call sites don't re-annotate inline.
- [ ] **S59** Where a `.d.ts` or library type uses `any` or `unknown`, explain and check the effect on vanilla-JS JSDoc + checkJs callers.
- [ ] **S60** A DAO type left as `object` has a concise comment saying why and what it may contain; existing useful param docs are kept.
- [ ] **S61** DAO `.d.ts` matches what the implementation returns, including `undefined`, with no unexplained `| undefined`; no runtime DAO change that forces caller updates.
- [ ] **S62** A DAO entity is typed properly or reverted, never left with only a few typed properties.
- [ ] **S63** Every connex-dao-node-v4 change materially changes types or behaviour; drop pure declaration-syntax rewrites.
- [ ] **S64** In libraries shipping `.d.ts` (connex-dao), types, doc comments and documented defaults live only in the `.d.ts`; the `.js` repeats no JSDoc.
- [ ] **S65** A temporary local connex-dao cast or deferred DAO typing has a named follow-up ticket recorded in the plan.
- [ ] **S66** Where a DAO strips fields with an omit list, consider an allow list and justify the choice.
- [ ] **S67** A new group of related fields is nested as its own sub-object on the existing DAO entity.
- [ ] **S68** A proposed DAO record schema has no redundant fields (duplicate payload copies, near-identical timestamps).
- [ ] **S69** New DAO keys follow the pattern (pk `<entityRef>-<typeId>`, GSI hash keys based on pk). ASK: before diverging.
- [ ] **S70** ASK: DAO/data-model changes that may affect other teams get a request doc (alternatives, tradeoffs, recommendation) for wider engineering approval before implementation.
- [ ] **S71** DAO test files apply the `.d.ts` types to their data, starting with one file for John to review.

## 7. Constants and enums

- [ ] **S72** ASK: recommend a home for each constant and have John confirm: `zod-contracts/<domain>` for greenfield, `connex-utils-node-v4/src/constants` for legacy when risk warrants. Watch for move candidates throughout.
- [ ] **S73** Domain-vocabulary constants that would drift or duplicate (record types, reason/status codes, groupings) are defined in -utils `as const`, not local `Set`s; app-specific ones stay local.
- [ ] **S74** Within a domain folder, constants sit in a `constants/` subfolder, not `name.constants.ts` files.
- [ ] **S75** Compare against existing shared constants rather than hard-coded strings; once a shared constant is introduced, every relevant handler uses it.
- [ ] **S76** A constant shared by zod-contracts and vanilla JS has one source and a simple import (change the vanilla side if needed), no shim file or parity tests; module format and runtime loading are verified.
- [ ] **S77** Constant and reference-data objects use `as const satisfies <Type>` (JSDoc: `@satisfies` plus `@type {const}`) consistently.
- [ ] **S78** `satisfies` targets an existing schema-derived named type, never an inline object type literal.
- [ ] **S79** No `/** @type {const} */` on simple scalar constants unless actually needed.

## 8. JSDoc style in JS

- [ ] **S80** JSDoc type imports are a single `/** @import { A, B } from 'pkg' */` near the top with clean package paths; no inline `import('...')` or repeated imports.
- [ ] **S81** Simple JSDoc annotations fit on one line.
- [ ] **S82** Use `type`, not `interface`, unless there is a stated reason.
- [ ] **S83** No `@returns` where the type can be inferred, including fixtures and builders. A boundary return type (e.g. handler) is allowed only if a wrong return value still errors.
- [ ] **S84** Inline `@type` refreshes are minimal and could not hide a future error.
- [ ] **S85** No casts to silence errors, no double casts through `unknown`, no cast-only "validators"; fix via correct upstream types or a real validator, checking the codebase and npm first.
- [ ] **S86** No manual annotation on `parse`/`safeParse` or other calls whose types are inferred.
- [ ] **S87** No `any`, `object`, `object[]` or `@param {object}` where a contract or shared type exists; mappers and handler `request` are concretely typed; fix the most impactful cases first without overcomplicating.
- [ ] **S88** Migrated types show concrete fields on hover, not `[x: string]: unknown`; never leave `{}` placeholders; take field types from planning and domain docs.
- [ ] **S89** `handlerContext` is never `object` or widened; type it from a Zod-derived type, then the handler framework's type, then the existing driver-management-exp `.d.ts`. Adding a type library is acceptable.
- [ ] **S90** Accumulator arrays are typed so pushes are checked, and `.filter` results narrow correctly.
- [ ] **S91** Type-check helpers return type predicates on shared types (e.g. `is Jurisdiction`).
- [ ] **S92** Readonly typing uses one form, not a mix of `readonly` modifiers and `Readonly<>`.

## 9. checkJs and tsconfig

- [ ] **S93** Create a strict `tsconfig.json` if missing (like dispatch-service journeys); add the slice's migrated files to `include` when ready, switching to a glob once a whole domain folder is covered.
- [ ] **S94** No per-file `// @ts-check`; remove old ones. Checking is only via tsconfig `include` with `checkJs`.
- [ ] **S95** Every file claimed as checked is matched by `include`; the type-check was actually run, not simulated, and changed and staged files show zero errors.
- [ ] **S96** The check scope is a focused glob over the migrated area, not the whole repo nor an ad-hoc list.
- [ ] **S97** Cut legacy modules off the island via narrow imports or a narrow same-basename `.d.ts`, verified with `--listFilesOnly`; never by disabling strict options. Report every `exclude` with a defensible reason.
- [ ] **S98** Files also used outside the island get minimal or no type or behaviour changes.
- [ ] **S99** One `tsconfig.json` (plus at most a `tsconfig.test.json` extending it) and one generic `type-check` script; no domain-named, temporary or jsconfig+tsconfig pairs.
- [ ] **S100** Config matches the strictest sibling repos, copied from a representative repo with frontend/backend differences noted; no unjustified `strict: false`; config file choice consistent across repos.
- [ ] **S101** App repos don't add `typescript` to package.json (`@types/*` fine); the script runs `npx -p typescript@6.x tsc --noEmit -p ...`; no TS6-removed options (`baseUrl`) or invalid `lib` entries.
- [ ] **S102** The test tsconfig includes test files and excludes the rest; Jest/Vitest globals are typed via `types` config, not per-file imports or suppressions.
- [ ] **S103** Lint exceptions are inline per line, never whole-file.
- [ ] **S104** DAO and service calls get real types (added to -dao if reasonable); valuable invalid-request test cases use `@ts-expect-error` with an explanation; list judgement calls back to John.
- [ ] **S105** Included files don't rely on risky partial canonical objects (Location, Vehicle) unless handled; downstream consumers of those shared schemas are checked for impact.
- [ ] **S106** App repos add no `.ts` source; strictness comes from strict config and JSDoc-imported Zod types; app code and library code are treated differently.
- [ ] **S107** Implicit `any` on callbacks and untyped libraries (e.g. connex-cds http) is fixed with reusable `.d.ts` types or typed stubs, starting with get, post and put.

## 10. Runtime parsing, guards and fail-fast

- [ ] **S108** External data is Zod-parsed once at the boundary (API, DB, external response) and derived types passed inward; internal mappers don't re-validate; error mapping is centralised.
- [ ] **S109/S130** Handlers parse `request.payload` with the shared schema at entry into a new `const parsedRequest` (never reassign `request`) and use it downstream. Report bugs found to John.
- [ ] **S110** Hand-written validation of external data becomes a parse against a -utils schema; during migration remove only validation that is obviously and simply redundant.
- [ ] **S111** No type error is fixed with a loose local type plus manual checks; use or extend a -utils schema and parse strictly.
- [ ] **S112** In greenfield or dark code, remove guards, `??` fallbacks, optional defaults and re-validation for states the types rule out; keep defensive checks only where integrity or concurrency requires.
- [ ] **S113** No `{...(x !== undefined ? { x } : {})}`; make the value required at the caller.
- [ ] **S114** Delete defensive-only files and their tests; add no helper doing shape/stop validation or business logic such as retiming.
- [ ] **S115** Fix type errors by improving the upstream type first. ASK: before stripping an existing guard on an unparsed or legacy path, and before adding any checker-only runtime guard (last resort).
- [ ] **S116** Typing diffs add no unrequested behaviour changes, such as new `return null` guards.
- [ ] **S117** The early phase includes at least one real runtime parse; frontend HTTP calls annotate requests with the derived type at the call site and parse responses with the shared schema.
- [ ] **S118** Response parsing happens inline in the existing helper before its return, with no separate `parseResponse` helper.
- [ ] **S119** A handler keeping `ValidateSchema` also parses with a -utils Zod schema, reusing an existing one.
- [ ] **S120** No schema for data that doesn't need parsing yet, unless a minimal one already exists in -utils.
- [ ] **S122** No new error-format helpers (`formatInternalError`, BadRequest mapping, readable-error packages) in migration PRs; call Zod inline and defer to the structured error-handling work.
- [ ] **S123** Type-safe code uses connex-api-node-v4 `NotFound`/`BadRequest` declarations; SDK error classes are not modified; deprecated versions are not used.
- [ ] **S124** A new failure mode has a single typed response shape used by API and UI consumers.
- [ ] **S125** Frontend code keeps the mandatory `?.` rule. Backend code accesses just-parsed Zod values directly, without `?.`, so it fails fast.

## 11. Comments and naming

- [ ] **S126** No "AI-generated" header or disclaimer comments; remove any added earlier on the branch.
- [ ] **S128** Established domain and brand names (e.g. Journey/Journeys) are never renamed to generic synonyms in identifiers, files or schemas.
- [ ] **S129** Contracts use semantically correct types, enums and names (e.g. country-first codes like `UK_DEFRA`) and call out shortcut reuse with tradeoffs. Simplify redundant identifiers now; recommend and ticket cross-repo renames.
- [ ] **S131** Functions are declared before use; non-handler utilities in an endpoint `index.js` move to `/utils`, one file each.
- [ ] **S132** Each change has a readable main control flow; helpers are real abstractions, not arbitrary chunks.
- [ ] **S133** Near-duplicate builders, loops or files are merged, or given distinct names if they genuinely differ.
- [ ] **S134** Where those lint rules apply, no `!` non-null assertions and no always-true conditionals.
