# Stage 5: Type rigor

A green `type-check` still allows mostly-optional schemas, `any`, `object`, `Record<string, any>` and untyped collections. This stage removes them before human review. Work contracts first, then upstream reuse, then the application as a last resort.

Read [checklist-schemas-and-types.md](checklist-schemas-and-types.md), sections 1, 2, 3, 4, 6, 8 and 12, and the `jsdoc` and `typescript-type-safety` skills.

**You can still change `-utils` and `-dao` in this stage.** Moving a type upstream is the point of the stage, not a follow-up. Every upstream change loops back through stage 3 propagation and stage 4.

Null policy: **undefined only in application code.** `null` appears only on fields the DB or an external source can store as `null`, and is coerced to `undefined` at the parse boundary where one exists. No `?? null` and no new `| null` in app code.

## Pass 1: optional and nullable audit

For every Zod schema the slice added or changed, list every `.optional()`, `.nullable()` and `.nullish()` field in the slice note's "Optional fields" table. For each one:

1. **Does it have to be optional?** Check the JSON/OpenAPI `required` list, DAO defaults (S35), mapper output and stored data. Make it required where every writer sets it.
2. **Is it a discriminated union in disguise?** Look for optional fields that co-vary: a JSON schema `oneOf`, mapper branches on a field, or groups always set together (for example freight `price`/`pay` versus `ranges`/`rangeRateType`). Model them as `z.discriminatedUnion` on a real discriminator, or a `z.union` of strict objects when there is none. Build each variant from a shared base with `.extend`. On legacy objects, propose it, ask, and land it in its own commit behind the stage 0 tests (S27).
3. **Should it be nullable instead?** Trace the field to its source. A value read from DynamoDB or Aurora that can be stored as `null` is `.nullable()` or `.nullish()` on the stored/read schema, not `.optional()`. Create and update input schemas keep the API's rules.
4. **Coerce null to undefined at the boundary.** For each nullable field, check whether a runtime parse exists on that path (handler, DAO or response parse). If it does, propose `.nullish().transform(value => value ?? undefined)` in the contract so `z.output` is `T | undefined`, and record it under "Transform candidates". If there is no parse yet, log it as the first tightening once there is. Ask before changing a legacy response shape.
5. **Refinements.** Remove `.refine` and `.superRefine` unless the user approves that specific one. Cross-field logic stays in application code: split the schema (or use a union) and let the code branch.

## Pass 2: scan and reuse

1. **List the files.** Everything in `tsconfig.json` `include`, plus app-side `.js` the island pulls in:

   ```bash
   npx -p typescript@6.x tsc -p backend/tsconfig.json --listFilesOnly | rg -v node_modules
   ```

2. **Scan** those files, and the slice's contract and DAO declarations:

   ```bash
   rg -n '\{any\}|any\[\]|Promise<any>|\{\*\}' <files>
   rg -n '\{object\}|\{Object\}|object\[\]|Promise<object>' <files> <dao .d.ts>
   rg -n 'Record<string, ?(any|unknown)>|\[key: string\]: unknown' <files>
   rg -n -B1 'new (Map|Set)\(\)' <files>          # flag any without @type on the line above
   rg -n '/\*\* @type \{[^}]+\} \*/ \(' <files>    # casts
   rg -n '\?\? null|\| null' <files>
   rg -n '\.(super)?[Rr]efine\(' <zod-contracts domain>
   rg -nU '\*/\s*\n\s*/\*\*' <files>              # stacked JSDoc blocks: the outer one is ignored
   ```

3. **Ledger.** Record each hit in the slice note's "Vague types" table: file and line, current type, runtime evidence of the value (test, mock, DAO), candidate fix, outcome.
4. **Resolve, in order:**
   1. Use an existing type from `zod-contracts`, the DAO `.d.ts`, or an SDK.
   2. Compose at the source with `.extend`, or export a nested sub-schema from `zod-contracts`. Ask before adding a new export.
   3. Fix a DAO or SDK declaration that is `object` or wrong at runtime (for example `ProductType.lookupById` resolves an array). Make the fix now, in `-dao`.
   4. Delete the annotation and let inference carry the type (callback `@param {any}`, filter predicates).
   5. Give collections concrete element types with `@type` (`Map<string, StoredLocation>`).

## Pass 3: last resort in the application

Only for hits with no upstream home after Pass 2, and only once the user agrees it shouldn't go to `-utils` or `-dao` in this slice:

- A minimal local `@typedef`: only the fields the code reads, no index signature, no generics, no `Pick`/`Omit`/`Partial`, defined once and shared with `@import`. Record the reason in the ledger.
- When a value is genuinely polymorphic, or the file is outside the island, keep the type and add a one-line comment saying why. Don't widen the island.

## Verify and report

1. Run `type-check` before and after, and count hits per scan pattern before and after. Run targeted tests through npm scripts.
2. A real bug the typing found gets a test proving the fix and a row in "Bugs the typing found".
3. Tell the user: optional fields tightened, unions introduced, nullable fields and coercion candidates, refinements removed, vague-type counts before and after, upstream changes made, local typedefs with reasons, and kept-as-is sites. Batch the "ask" items into one `AskQuestion`.

## Gate

- [ ] Every optional, nullable and nullish field in the slice's schemas has an "Optional fields" row with evidence and a decision.
- [ ] No `.refine` or `.superRefine` remains without the user's approval.
- [ ] Every scan hit has a "Vague types" row with an outcome.
- [ ] Every remaining vague type is a contract type, an agreed local typedef, or has a one-line keep-as-is comment.
- [ ] No new `Pick`/`Omit`/`Partial`, schema `.pick`/`.omit`/`.partial`, generics, index signatures, `?? null`, or schema loosening.
- [ ] Stage 4's gate still holds after the last loop.
