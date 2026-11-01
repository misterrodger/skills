# Checklist: OpenAPI, Swagger, and JSON Schema (stage 7)

Check every line against the plan or diff, and record each finding as fix-now, ask John, or log.

Quotes and sources: ~/Github/planning/zod-migration-skill/FEEDBACK-OPENAPI.md

## 1. Approach and scope (Zod-first, minimal metadata)

- [ ] **O1.1** For a migrated operation, request, response, and parameter shapes exist only as Zod schemas; the OpenAPI document, runtime validation, and derived types all come from them.
- [ ] **O1.2** In smaller services (S&Q, Pricing, Bulk-materials), a migrated endpoint replaces both `ValidateSchema` and the hand-written OpenAPI JSON schema with Zod `parse`/`safeParse` plus `createDocument`.
- [ ] **O1.3** ASK: before swapping OpenAPI to `createDocument` in an area, confirm with John, proposing a narrow slice and describing what a fuller scope would cover.
- [ ] **O1.4** In a large service (for example dispatch), the OpenAPI/`ValidateSchema` swap ships as its own later phase, never bundled into a functional or type-improvement PR.
- [ ] **O1.5** The first step converts only the existing input (request) JSON schemas to Zod schemas and derived types in `-utils`, feeds them to `createDocument`, and calls `parse` inline.
- [ ] **O1.6** Target unreleased or in-development endpoints first; in production code touch only endpoints you know and can test manually, and extend automated coverage as you go.
- [ ] **O1.7** The migrated document carries much less descriptive metadata than the current Swagger, with no examples.
- [ ] **O1.8** The legacy OpenAPI/JSON-schema document is not deleted, and docs are not generated purely from `createDocument`, until every resource in the repo has migrated.
- [ ] **O1.9** The migrated document keeps operation IDs (`{verb}-{resource}`), Swagger tags grouped by resource, URL standards, and the security model, confirmed correct after generation.
- [ ] **O1.10 / O7.10** The `-exp` BFF and frontend import the same shared Zod schemas; the BFF parses with them in the same slice, with no null-to-omit coercion kept for backward compatibility.
- [ ] **O1.11** Before swapping a production area, the plan states how the change could affect current production.

## 2. Library and tooling choices

- [ ] **O2.1** The diff depends on `zod-openapi` and has no `@asteasolutions/zod-to-openapi`, `extendZodWithOpenApi`, `OpenAPIRegistry`, or `OpenApiGeneratorV31`.
- [ ] **O2.2** The document is built by calling `createDocument` from `zod-openapi`.
- [ ] **O2.3** `zod-openapi` is a devDependency unless a running app serves Swagger from it; `zod` is a peerDependency of `-utils` and a direct dependency of parsing consumers; Zod versions match across repos and unrelated consumers are unaffected.
- [ ] **O2.4** Only shared Zod schema and `z.infer` files are TypeScript; the application's OpenAPI document and handlers stay JavaScript.
- [ ] **O2.5** Any library-specific construct introduced (for example `.openapi('Name')`) is explained, including what it does and whether a cleaner placement exists.

## 3. Where OpenAPI metadata lives

- [ ] **O3.1** Shared `-utils` schemas have no `.openapi(...)` or `.meta({ id })` calls; component names are attached in the application's OpenAPI document where each schema is used.
- [ ] **O3.2** Shared schemas carry no id, description, or example metadata and avoid `.meta()`, except `deprecated` on properties where appropriate; any kept doc info lives in the main `createDocument` call.
- [ ] **O3.3** The OpenAPI document and `api-docs.js` import every request and response schema from `-utils` zod-contracts, with no inline `z.object(...)` or inline types.
- [ ] **O3.4** Shared Zod schemas feeding the document are camelCase with a `Schema` suffix (for example `entityRefParamSchema`).
- [ ] **O3.5** Each migrated operation keeps a thin `api-docs.js` with discovery fields only (handler, path, method, operation id, security); schema shapes live in the Zod document.

## 4. Document composition (one file, no helpers)

- [ ] **O4.1 / O4.4** Each backend has one `openapi-document.js` calling `createDocument` directly, readable top to bottom, split per resource only if it gets too large to read.
- [ ] **O4.2** No wrapper helpers around Zod or zod-openapi (for example `registeredSchema`, `closedObject`, `openObject`, `outcomeShape`, `from-zod`, `to-query-parameters`, `get-schema-list`); use plain Zod and `createDocument`.
- [ ] **O4.3** Per operation, the document holds only basic info and an optional path description, referencing the shared Zod schema for request, response, and parameters.
- [ ] **O4.5** Mid-migration, the published document is the legacy spec with only migrated paths and components overlaid by one small merge function, used by validate and publish, deleted once every resource is on Zod.
- [ ] **O4.6** Every structural schema change (for example switching to `oneOf`) has a stated reason and is still needed, or it is reverted.
- [ ] **O4.7** Where a schema uses `.transform`, codecs, or pipes, check JSON Schema generation limitations and whether the document shows the input or output shape.
- [ ] **O4.8** Local JSON schemas duplicating a shared contract are replaced by the shared Zod export, with the impact on schema registration and generated docs reported.

## 5. Baseline and parity

- [ ] **O5.1** Before any change, save the full legacy document as a baseline. Run `generate-api-schemas` first, which only refreshes `v4/api-docs/schema-type-defs.js` from `register.js`. Then dump `OpenAPI3.getSpecificationDocs({ publicApisOnly: false })` after `OpenAPI3.initialize(...)`. Confirm the baseline is current, and note any auto-generated diffs.
- [ ] **O5.2** After migration, regenerate and diff against the baseline; structure is locked, and the only acceptable differences are descriptive metadata.
- [ ] **O5.3** The parity report lists the descriptive Swagger content (descriptions, examples, ids) the simplified document drops, so John can choose what to add back.
- [ ] **O5.4** Before the swap, add a drift test that discovers operations by globbing `api-docs.js` folders and asserts route, method, operation id, parameters, request body, responses, security, and required fields; no examples; kept after the swap.
- [ ] **O5.4 / O8.7** Start the drift test from `cds-waste-compliance-service/backend/tests/openapi-spec.test.js`, replacing its hard-coded expected operation map with glob discovery; raise any inherited spec-test failure with John rather than fixing silently.
- [ ] **O5.5** Before the swap, each touched endpoint has at least one route/API integration test hitting it; these runtime tests complement the drift test, not replace it.
- [ ] **O5.6** No tests that only restate a schema's shape; schema tests exist only where there is logic (for example `.transform`).
- [ ] **O5.7** A slice is done only with characterization tests, Zod request/response/params coverage, `createDocument` paths, the drift test, `parse`/`safeParse` with registration removed, `npm run validate-api-schemas` passing, and checkJs opt-in.

## 6. Mirroring legacy schema settings in Zod

- [ ] **O6.1** When mirroring a legacy object in Zod, the field list and strictness come first from its existing OpenAPI JSON schema.
- [ ] **O6.2** For released endpoints, the first Zod version keeps the source's required and nullable settings, with tightening as a later separate step; objects are strict by default.
- [ ] **O6.2** ASK: if the source is open (`additionalProperties` absent or `true`) and stripping or rejecting unknown fields could break a hot path, ask John before writing a non-strict schema; an approved exception gets a code comment and ledger entry.
- [ ] **O6.3** Each `.nullable()`, `.optional()`, or `.nullish()` traces to the source OpenAPI schema or real stored data; where the source stores `null`, the schema accepts `null`.
- [ ] **O6.4** No loosening with `additionalProperties: true`, `.passthrough()`, or loose objects by default; fields are enumerated.
- [ ] **O6.5** ASK: a partial read/stored projection of a record owned by another service may use `.loose()` on the schema itself (no second variable, type inferred from the plain shape), proposed to John first; create, update, and request schemas stay non-loose.
- [ ] **O6.6** Unreleased or in-development endpoints start strict and required, with no `unknown`-heavy shapes, no null-to-omit coercion, and no backward-compatibility code.
- [ ] **O6.7** When the OpenAPI schema or a fixture has a field the contract lacks (or the reverse), check both sides and recommend per case whether to fix the contract, OpenAPI schema, or fixture.
- [ ] **O6.8** Every field in the migrated schema traces to the legacy OpenAPI schema, stored data, or a stated requirement, and every removed field is justified.

## 7. Request/response validation (parse/safeParse vs ValidateSchema)

- [ ] **O7.1** A migrated handler has no `API.ValidateSchema(request, '<name>')` call; it parses with the shared Zod schema so types flow through the handler.
- [ ] **O7.2** The resource's JSON-schema registration in `backend/v4/schemas/register.js` is removed in the same slice, except shared schemas still used by unmigrated endpoints.
- [ ] **O7.3** Use `parse` when invalid input is exceptional and the existing error mapper owns the response; use `safeParse` only when the handler turns the failure into a specific API result.
- [ ] **O7.4** The handler parses inline at entry and uses the parsed value, not the raw `request`, for the rest of the handler.
- [ ] **O7.5** Where the full swap is deferred (large services like dispatch), handlers still on `ValidateSchema` also parse with an existing `-utils` Zod schema to get types.
- [ ] **O7.6** Hand-written checks duplicating what Zod, OpenAPI, or DB constraints enforce are removed; business and cross-record checks stay.
- [ ] **O7.7** No `BadRequest` mapping, custom error helper, or readable-error package around Zod failures; readable errors wait for the structured error-handling work.
- [ ] **O7.8** Response schemas are parsed where responses are consumed (the frontend is preferred), and each recommendation names the exact file and line.
- [ ] **O7.9** Log as follow-ups, not in the slice: automatic DAO and API request/response parsing, Standard Schema in `ValidateSchema`, a new Zod validation utility, readable errors, and centralizing legacy validation.

## 8. Publishing/validation scripts and Swagger UI serving

- [ ] **O8.1** The `createDocument` output (or merged document) is validated and published with the existing `connex-api-node-v4` scripts (`validate-api-schemas` runs `scripts/validate-api-schema.js`; `publish-api-doc` runs `scripts/publish-api-doc.js`); no new publisher.
- [ ] **O8.2** `npm run validate-api-schemas` passes on the merged document before the slice is called done.
- [ ] **O8.3** Generation, validation, and publishing work inside the existing `.github` / `cds-workflow` CI without pipeline changes.
- [ ] **O8.4** Swagger UI for the Zod-generated document reuses how `cds-dispatch-service` already creates and serves docs, with no new server.
- [ ] **O8.5** Endpoints are still auto-discovered from `api-docs.js` as `connex-api-node-v4` does today; no manual route list is added.
- [ ] **O8.6** A new generation pattern is demonstrated end to end on one well-chosen endpoint for John's review before it is rolled out.

## History to know

- Waste-compliance (Aug 2026) started on `@asteasolutions/zod-to-openapi`, hit a Zod 3 vs 4 peer conflict, switched to `zod-openapi` on Aug 9, and settled on one `openapi-document.js` per backend with thin `api-docs.js` files and no helpers.
- Waste-compliance is the brownfield reference: it validates and publishes its `createDocument` document through `connex-api-node-v4`; its OpenAPI spec test was deferred on Aug 15 and hard-codes its expected operation map.
- Dispatch journeys (Sep 14-15) scoped a four-endpoint `createDocument` overlay, then reverted it as too much for one PR; the interim became `ValidateSchema` plus a shared Zod schema, and service size was the only reason.
- Bulk-materials (Oct 20) reverted a full-slice attempt to input schemas only; review rejected `unknown`-heavy types, metadata in types, wrapper helpers, assumed passthrough, schema-only tests, and late or unused parsing.
- Bulk-materials started with Automation Monitor and the Yard Automation simulator, was not implemented as of Oct 30, and an Oct 26 concern about stripped Setup location fields led to loose read projections.
