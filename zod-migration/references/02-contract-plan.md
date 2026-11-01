# Stage 2: Contract plan

Plan the contracts, DAO types and app changes before editing anything. Every schema in the plan is strict unless the user approves otherwise.

Read [checklist-process.md](checklist-process.md), section "Stage 2". Skim the headings of [checklist-schemas-and-types.md](checklist-schemas-and-types.md) so the plan doesn't set up findings for stage 5.

## Steps

1. **Read the evidence first:**
   - the existing JSON/OpenAPI schemas for each object (`required`, `nullable`, `additionalProperties`, enums)
   - for Setup entities, `cds-setup-service/backend/v4/<entity>/schemas`
   - for objects that other services write, the writers and a sample of stored records, if available
   - the existing `zod-contracts` schemas you could extend

   Every `.nullable()`, `.optional()` and `.nullish()` must trace back to this evidence. Don't invent fields, and don't drop fields silently.
2. **Map each object to a contract:**
   - Which domain it belongs to: the owning domain, or a named read projection inside the consuming domain if another team owns the entity.
   - How it is composed: `.extend` from an existing or `_common` schema first. Use a discriminated union for near-identical variants. Don't create a parallel schema.
   - Its input and output: where the app reshapes data (projecting up or down, formatting, coercing strings), propose a `.transform`, with `z.input` and `z.output` types, instead of app code.
   - Any deprecated properties, marked `.meta({ deprecated: true })`.
3. **Strictness.** Default every object to `z.strictObject`, with required fields wherever the evidence allows. Only propose a non-strict option where strict could break a hot path, typically a widely used canonical object that other services write and that the contract models only partly. For each proposal, give the risk and what would make it strict later.
4. **Plan the DAO signatures.** For each DAO function in the slice, give the current signature (`object`, `Promise<object>`, loose types) and the specific contract-derived signature. Write inputs are built from contract types, e.g. `XUpdate & { crn: string }`. Match what the code actually does at runtime. Don't add `| undefined` unless it's real.
5. **Plan the app changes:**
   - where each handler parses (`parse` or `safeParse`)
   - which local types and schemas get deleted
   - which BFF schemas move to the shared schema
   - which files join `tsconfig` `include`
6. **List the constants candidates**, each with a recommended home and the reason.
7. **Ask once.** Use one `AskQuestion` batch covering:
   - any non-strict proposals
   - constants homes
   - transform candidates
   - any new domain
   - open questions on evidence

   Record the answers in the slice note's strictness ledger and candidates tables.

## Gate

- [ ] Each object has a target schema, a composition source, and evidence for its optional and nullable fields.
- [ ] Every non-strict schema is **approved by the user** and recorded in the ledger.
- [ ] **The user confirmed** the constants homes and the transform candidates.
- [ ] The DAO signature changes are listed.
- [ ] The app parse points and the `include` additions are listed.
