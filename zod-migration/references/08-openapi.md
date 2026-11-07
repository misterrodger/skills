# Stage 8: OpenAPI

Replace the hand-written JSON Schema and Swagger for the slice with a minimal, Zod-first `zod-openapi` `createDocument`, and keep structural parity with the legacy document.

Read [checklist-openapi.md](checklist-openapi.md), all of it, [checklist-process.md](checklist-process.md), section "Stage 5-8", and [stack-map.md](stack-map.md), section "OpenAPI pieces".

## Steps

1. **Ask** before starting the swap in this area, and offer a narrow and a fuller scope. In a large service, keep the OpenAPI swap out of functional PRs.
2. **Baseline.**
   - Generate the current legacy document: run `generate-api-schemas` if the repo has it, then `OpenAPI3.initialize(require('../specification-params'))` and `await OpenAPI3.getSpecificationDocs({ publicApisOnly: false })`.
   - Write it to a JSON file outside the source tree, and confirm it matches the handlers and `api-docs.js` files, i.e. that it is up to date.
   - Run `npm run validate-api-schemas` and record the result.
   - Use the legacy schemas as evidence in the strictness ledger. Any object they show as open is a non-strict question for the user.
3. **Write the documentation drift test before the swap.**
   - It discovers operations by globbing the `api-docs.js` folders, the same discovery the generator uses, so new and removed routes are tracked automatically.
   - For every operation it asserts the path, method, operation id, parameters, request body, responses, security, and required fields.
   - It asserts no examples or descriptions.
   - It runs green against the legacy document first.
   - It sits alongside the stage 0 route/API runtime tests and doesn't replace them.
   - Start from `cds-waste-compliance-service/backend/tests/openapi-spec.test.js`, but replace its hard-coded operation map with the glob.
4. **Write the Zod document.**
   - One `backend/v4/schemas/openapi-document.js` calls `createDocument`, plugging in the shared schemas imported from `zod-contracts`.
   - Include basic info and path descriptions only.
   - Don't add examples, `.meta()` ids or descriptions on the shared schemas, or wrapper helpers.
   - Component names are set in this file, not on the shared schemas.
   - Split it into per-resource fragment files only if the file gets too large to read.
   - Keep the `api-docs.js` files, for discovery fields only.
5. **Merge, mid-migration.**
   - While some resources are still legacy, one small merge function overlays the `createDocument` paths and components onto the legacy document.
   - The validate and publish scripts pass the merged document to `connex-api-node-v4`'s `validate-api-doc` and `publish-api-doc`, as waste compliance does. Keep the `publicApisOnly` behaviour for non-develop publishes.
   - Delete the merge function once every resource is on Zod.
6. **Retire the legacy pieces for the slice.** The handlers parse with the shared schema, and the BFF parses with the same schema in this slice. Remove the `API.ValidateSchema` calls and the resource's `register.js` registrations and JSON schema files.
7. **Check parity.**
   - Regenerate the document and diff it against the baseline. Structural differences must be zero, or each one explained and approved.
   - Descriptive metadata (descriptions, examples, titles) may drop. Report what was lost so the user can choose what to add back.
   - Check how any `.transform` appears: input shape for requests, output shape for responses.
   - A field the contract doesn't model **may** mean the schema is wrong. Decide which side is wrong, and loop back to stage 3 if it's the schema.
8. **Validate.** Run `npm run validate-api-schemas` on the merged document, the drift test, the stage 0 tests, `type-check`, and the full suite.
9. **Self-review.** Go through every line of [checklist-openapi.md](checklist-openapi.md), record the findings in the slice note, and loop until none are left to fix now.

`zod-openapi` is a devDependency, unless a running app serves Swagger from the Zod document.

## Gate

- [ ] The baseline document is saved, and the drift test passed against it before the swap.
- [ ] The Zod document covers every operation in the slice, and the drift test passes against the merged document.
- [ ] `ValidateSchema` and `register.js` entries are gone for the slice, and the BFF is on the shared schema.
- [ ] `validate-api-schemas` passes, the parity diff has been reported, and the lost metadata has been listed for the user.
- [ ] The OpenAPI checklist has been checked, and the slice note's OpenAPI section is filled in.
