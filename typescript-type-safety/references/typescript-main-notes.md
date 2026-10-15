# TypeScript main notes

## Guiding principles

- **Prefer in this order:** type *declaration* → type *inference* → type *assertion* — but the choice is about *scope*, not "annotate everything first." **Declare at boundaries** (signatures, public APIs, object literals meant to match a known shape) where the type is a contract others depend on. **Infer inside the boundary** (locals, simple returns, generic instantiation), checking that inference stays correct and narrow; fall back to a declaration only when it widens or goes wrong. **Assert last** — `as` overrides the compiler rather than checking, so each one hides a potential bug (`as const` is the benign exception, since it narrows rather than lies).
- **Never `any`.** Use `unknown` (forces the caller to narrow). If you must escape, `// @ts-ignore` is preferable to `any`. Weak fallbacks that still say *something*: `any[]`, `Record<string, any>`, `() => any`.
- **`const` over `let`.** `let` widens to `any`/the base type; `const` preserves the literal type and avoids accidental widening.
- **`type` over `interface`.** Compose with `&` (intersection) and `|` (union). `interface` only describes object shapes and silently merges declarations of the same name in scope, which is a footgun.
- **`readonly` by default** for anything you don't intend to mutate.
- **When to annotate, concretely:** type anything public. Annotate an object literal *when it should conform to a known shape* — the annotation turns on excess/missing-property checking and catches typos at the definition site. A purely local literal can just infer (like a function default); reach for `as const` when you want the precise readonly type, or `satisfies T` when you want to check against a shape *and* keep the precise type (annotation alone widens). Usually annotate complex functions; for simple ones, check inference is good enough; when in doubt, annotate.

## Setup & config

- Turn on `strict` as early in a project's life as possible — retrofitting is painful.
- Don't target too low; aim for **ES2020+**.
- **ESM in Node:** set `"type": "module"` in `package.json`, and `"module": "NodeNext"` in `tsconfig`. You author `.ts`, it emits `.mjs` (CommonJS files emit `.js`).
- **Missing types:** if the npm page shows the TS badge, types ship with it. Otherwise `npm i -D @types/<pkg>`. Writing `@types`/`.d.ts` lets you adopt type-checking without converting a whole JS codebase.
- **JSX:** pick a `jsx` compiler option (`preserve`, `react`, `react-jsx`) — different projects need different ones, so try them.
- **Triple-slash directives** can enable strictness file-by-file as you incrementally harden a repo: `/// <noImplicitAny>` etc.
- `tsc --watch` for auto-recompile.

## Everyday syntax

- Let literal values and default params infer their literal type — don't annotate them.
- Prefer `key: 'value' | undefined` to optional `key?`. The explicit `undefined` forces you to handle the absent case and the compiler flags every use site.
- **`void`** = returns nothing. **`never`** = unreachable / always throws — prefer `never` to `void` for those blocks.
- Use lowercase primitives (`string`, `number`, `boolean`, `symbol`). Never the boxed `String`/`Number` wrapper types.
- Declare and reuse aliases: `type MyObj = { name: string }`, then annotate with it.
- Anonymous/inline types where one-off: `const f = (p: { a: number; b: number }): number => p.a + p.b`.
- Function types: `type Fn = (a: string) => void` or `function fn(a: string): string`.
- Types are navigable like objects: `Person['name']` → `string`.
- Symbol/template-string index signatures (TS 4.4+): `type Obj = { [sym: symbol]: number }`.

## Functions, overloads, generics

- **Overloads:** multiple signatures, one implementation. Order most-specific → least-specific. The implementation must satisfy all signatures.
  - First instinct should be to **split into separate functions** instead — only overload when one function genuinely handles different arg types differently (common in lib code; adds complexity).
  - **The "differently-typed outputs" trap:** if you want one helper to take slightly different arrays and return correspondingly different types, trying to express that with overloads or generics gets verbose fast. Simpler: do the `map`/`filter` at the call site and let the helper be a single-purpose predicate/transform. You get the correct narrow type *and* simpler code.
- **Generics** keep the relationship between input and output types intact.

```ts
function first<T>(arr: T[]): T { return arr[0] }
first([1, 2, 3])    // T inferred as number
first<string>(x)    // or specify explicitly
```

- **Constrain** with `extends` ("must contain"): `function len<T extends { length: number }>(x: T) { return x.length }`.
- Multiple type vars and defaults: `function pair<K, V>(k: K, v: V) {}`, `type Container<T = string>`.
- Use generics to **express a relationship** that plain types lose — when an input type drives the output type, or two params must vary together. Without it the link collapses to `any` and you lose warnings if you later add type-specific logic.
- **Where generics earn their keep:** library/shared code, where accepting the extra complexity buys tighter type safety for *consumers*. In app code, prefer the simpler call-site approach above before reaching for them.
- **TSX gotcha:** write the type param with a trailing comma — `<T,>(x: T) => …` — so the compiler doesn't parse `<T>` as a JSX element.
- **Point-free kills inference.** If a composed/point-free function won't infer, write it out longhand, read off the inferred type, annotate the implementation, then refactor back to point-free.

## Composing & transforming types

- **Union** `A | B`, **intersection** `A & B`, **`extends`** to compose (nothing to do with OOP).
- **Index/dynamic types** for keys not known ahead of time: `type Dict = { [key: string]: string }`. Constrain keys with `[K in SomeUnion]`.
- **Template union types** generate permutations: `type Id = \`id-\${Product}-\${Status}\``.
- **Mapped types** transform every property:

```ts
type Immutable<T> = { readonly [P in keyof T]: T[P] }
type Optional<T>  = { [P in keyof T]?: T[P] }
```

- **Conditional types** + **`infer`** to extract:

```ts
type ElementType<T> = T extends (infer U)[] ? U : never
type ParamOf<T> = T extends (p: infer P) => any ? P : never
```

- **Distributive conditionals** apply across each member of a union: `type Nullable<T> = T extends any ? T | null : never`.
- **Recursive** and **variadic tuple** types for nested/variable shapes:

```ts
type Flatten<T> = T extends Array<infer U> ? Flatten<U> : T
function concat<T extends unknown[], U extends unknown[]>(a: T, b: U): [...T, ...U] { return [...a, ...b] }
```

## Built-in utility types

Reach for these when composing/decomposing objects:

- **Shape edits:** `Partial<T>`, `Required<T>`, `Readonly<T>`, `Pick<T, K>`, `Omit<T, K>`.
- **Union edits:** `Exclude<T, U>`, `Extract<T, U>`, `NonNullable<T>`.
- **Function/class introspection:** `Parameters<F>`, `ReturnType<F>`, `ConstructorParameters<C>`, `InstanceType<C>`.
- **Build maps:** `Record<Keys, T>` — same type across keys, e.g. `Record<string, Product>`.
- **Keys:** `keyof typeof obj` → union of an object's keys.
- **Strings:** `Capitalize<T>` / `Uncapitalize<T>` (the useful ones); `Uppercase`/`Lowercase` exist too.
- **Promises:** `Awaited<T>` recursively unwraps to the resolved value.

## Narrowing & guards

TS narrows via assignment, conditionals, truthiness/equality, and:

- **Built-in guards:** `typeof`, `instanceof`, `Array.isArray()`.
- **Type predicates** (`x is T`) — the **default** validator: returns a boolean, branches cleanly, and composes with `filter`. Essential for callbacks/HOFs, otherwise filter typing degrades:

```ts
const isString = (v: unknown): v is string => typeof v === 'string'
arr.filter((x): x is string => typeof x === 'string')  // string[], not (string | number)[]
```

- **Assertion functions** (`asserts x is T`) — same idea but *throws* instead of returning a boolean. Reach for these only when an invalid value means you can't continue anyway. With arrow syntax you must use a type alias, not an inline annotation:

```ts
function assertNumber(v: unknown): asserts v is number {
  if (typeof v !== 'number') throw new Error('Not a number')
}
```

- **Branded types** solve a *different* problem — not the check, but making the validated-ness persist in the type so an unchecked `string` can't be passed where a validated `Email` is required: `type Email = string & { readonly __brand: 'Email' }`. Add only when you actually need that guarantee to travel; skip it otherwise.

- **Discriminated/tagged unions** + `in` narrowing — see the next section for how to model and exhaustively handle them.
- **JSDoc** can drive inference and even generate `.d.ts` from JS — handy for hardening JS lib code without a full migration.

## Discriminated unions & exhaustiveness

- **Model with a union, don't loosen with optionals.** Tie related fields together behind a discriminant so illegal combinations can't be represented:

```ts
// good — each variant carries exactly its own fields
type Result =
  | { success: true;  userName: string; email: string }
  | { success: false; reason: string }

// avoid — a bag of optionals; every field is now maybe-undefined everywhere
type Result = { success: boolean; userName?: string; email?: string; reason?: string }
```

  This is the same instinct as preferring `'value' | undefined` to `key?`: make the compiler force you to handle each case.

- **Exhaustiveness with `assertNever`.** TS has no built-in, so keep a one-line helper that throws (compile-time *and* runtime safety — the runtime throw catches values that slip past the types, e.g. from an API):

```ts
function assertNever(x: never): never {
  throw new Error(`Unhandled case: ${JSON.stringify(x)}`)
}

function handle(r: Result) {
  switch (r.success) {
    case true:  return r.userName
    case false: return r.reason
    default:    return assertNever(r) // errors at compile time if a variant is unhandled
  }
}
```

## `satisfies`, `as const`, and deriving types from values

Four ways to apply a type to a value literal, differing in whether the value is *checked* and which type flows *forward*:

| Form | Checks against `T`? | Type going forward |
|---|---|---|
| `const x: T = {…}` | yes | the wide `T` (literal detail lost) |
| `{…} satisfies T` | yes | the narrow literal type |
| `{…} as const satisfies T` | yes | readonly literal values |
| `{…} as const` | no | readonly literal values |

- Reach for **`satisfies`** to type loose-but-checkable values without losing precision: config objects; tightening lib types that default to wide, e.g. `new URLSearchParams({…} satisfies MyParams)` or a `fetch` body `satisfies MyPostBody`; tuple inference; enforcing the shape of an `as const` object/array.
- Use **`as const`** when minting a constant with no prior type and you want the exact readonly literal. It's **deep/recursive**, unlike `Object.freeze`, which only freezes the top level.

Deriving reusable types from an `as const` value:

```ts
const sizes = { sm: 1, md: 2, lg: 3 } as const
type Sizes     = typeof sizes                       // the whole object type
type SizeKey   = keyof typeof sizes                 // 'sm' | 'md' | 'lg'  (works without as const)
type SizeValue = (typeof sizes)[keyof typeof sizes] // 1 | 2 | 3

const tags = ['new', 'sale', 'hot'] as const
type Tag = (typeof tags)[number]                    // array of consts → 'new' | 'sale' | 'hot'
```

## Validate at the boundary

Anything entering from outside your type system is *not* the type you wish it were — type it `unknown` and validate (a schema lib like Zod, or a hand-written guard) before use. Treat these as untrusted:

- `fetch`/API responses, `.json()`, and `JSON.parse`
- user input and form data
- `localStorage` / `sessionStorage`, and URL/query params (the user can edit these)
- webhook payloads, DB/object-store reads (incl. S3), filesystem reads

## Standard-library rough edges (`ts-reset`)

A few built-ins are typed too loosely (or too strictly) by default; Matt Pocock's **`ts-reset`** patches the common ones. Worth knowing even if you don't adopt it:

- `JSON.parse` and `Array.isArray` hand you `any` — re-type as `unknown` and validate.
- `Object.keys` / `Object.entries` return wide types; narrow again explicitly.
- `.filter(Boolean)` won't drop the falsy *type* without a type predicate.
- `.includes` / `.indexOf` on `as const` arrays are over-strict — they reject values not in the literal union, so you can't even test for them.

## Assertions (last resort)

- **`as const`** — assert a readonly literal type, on a property or whole object/array: `const x = { a: 'a' } as const`.
- **`as`** — `(value as string).length`, `const o = obj as X`.
- **`!`** — definite assignment, "this is not null/undefined": `data!.name`. Use sparingly.
- **`<T>value`** — older syntax; doesn't work in JSX/TSX.

## Assignment rules worth remembering

- `unknown` is assignable only to `unknown`/`any`; validate before use.
- `void` is assignable only to `any`.
- Nothing is assignable to `never`.
- With `strictNullChecks`, you must opt `null`/`undefined` into a type explicitly to use them.

## Structural typing & object freshness

- TS is **structurally (duck) typed** — compatibility is about shape, not declared name.
- **Excess-property ("freshness") checks** only fire on *fresh* object literals checked immediately. To keep the safety net:
  - Pass object literals directly into functions/returns.
  - Assign literals straight to a typed variable, not through an untyped intermediate.
- Weak types (all-optional) always get extra-property checking — good; disable with `as`/`unknown` only if you must.
- **Bivariance:** TS permits some unsound covariance for ergonomics. Stay strict-first — keep literals fresh, match arg types exactly, and use type guards for function/callback signatures. (`in`/`out` variance annotations exist; rarely worth it.)

## TypeScript in React

- **Style objects:** type with `React.CSSProperties` for autocomplete. (MUI: its `style` prop already accepts `CSSProperties`, but idiomatic MUI uses `sx`, which is its own theme-aware `SxProps<Theme>` — wider than `CSSProperties`, so don't use `CSSProperties` there.)
- **Children:** type as `React.ReactNode` (accepts text, numbers, elements, fragments, null). Narrow to `React.JSX.Element` only if you specifically require a single element. Self-close `<Button />` when passing no children.

```tsx
function Card({ children }: { children: React.ReactNode }) { return <div>{children}</div> }
```

- **Wrapping an HTML element:** derive props from the element with `ComponentProps<'button'>` and spread the rest, so you inherit every native prop with autocomplete:

```tsx
function Button({ variant, ...rest }: ComponentProps<'button'> & { variant: 'primary' | 'ghost' }) {
  return <button className={variant} {...rest} />
}
```

  - **React 19:** `ref` is now a normal prop, so `ComponentProps<'button'>` already includes it and `forwardRef` is no longer needed (it's being deprecated). The older `ComponentPropsWithRef` / `ComponentPropsWithoutRef` split is mostly legacy now.
  - Add extra props with `&` (or `interface Props extends ComponentProps<'button'> { … }`).
- **Passing state setters down:** a `setState` prop is `React.Dispatch<React.SetStateAction<T>>`.
- **Event handlers:** typed automatically when written inline (`onChange={e => …}`). To *extract* a handler to a named function, write it inline first, hover to read the type, then annotate — e.g. `React.ChangeEventHandler<HTMLInputElement>`, or type the event itself as `React.ChangeEvent<HTMLInputElement>`.
- **Hooks:**
  - `useState` infers from the initial value; otherwise specify, e.g. `useState<User>()`. For async data use `useState<ApiData | undefined>(undefined)` since it's empty until loaded.
  - `useRef<HTMLInputElement>(null)` — type the specific element; you don't need to add `| null` to the type argument yourself.
  - `useEffect` needs no type.
  - `useContext` — see below; it's the one hook with real typing friction.

  **`useContext` pattern.** The friction is that `createContext` demands a default value, but there's often no sensible one. Typing it loosely (`T | null`/`undefined`) then forces a null-check in *every* consumer. The fix: create it as `T | undefined` with an `undefined` default, and hide the check inside a custom hook that throws when used outside a provider — consumers then get a clean, non-`undefined` `T`:

```tsx
type Auth = { user: User; logout: () => void }

const AuthContext = createContext<Auth | undefined>(undefined)

function useAuth(): Auth {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx // narrowed to Auth — no undefined leaks to callers
}
```

  - **React 19 provider syntax:** render the context directly — `<AuthContext value={auth}>…</AuthContext>`. `<AuthContext.Provider>` is the legacy form (still works, being deprecated). Forgetting `value` passes `undefined` and overrides the default.
  - **React 19 `use`:** `use(AuthContext)` can replace `useContext` and, unlike it, may be called conditionally/in loops. Same typing story.

- **General technique:** when you don't know a prop/callback's type, write it inline, hover to read the inferred type, then lift that type into an annotation.
- **Where types live:** a `types.ts` per app/feature for your own types; a `.d.ts` only to supply types for an untyped third-party lib. Prefer `import type { Foo } from …` for type-only imports (clearer intent, reliably erased at build).

> Already covered above and applies here unchanged: `Record` for keyed objects, `type` vs `interface`, inferred defaults, `as const` for literal precision, and `unknown` + Zod + `ts-reset` for external/API data (see **Validate at the boundary**).

## Testing your types

Mostly relevant to library/shared code, where a type regression breaks consumers silently:

- **`expectTypeOf`** (via Vitest) for positive assertions: `expectTypeOf(fn('a')).toEqualTypeOf<string>()`. `assertType` works too.
- **`@ts-expect-error`** for negative assertions — the line *must* error or the directive itself fails, so it pins down what your types should reject:

```ts
// @ts-expect-error — variant requires a reason
const bad: Result = { success: false }
```

## Types in plain JS

You can get most of TypeScript's checking without authoring `.ts`:

- Add `// @ts-check` to the top of a `.js` file to opt that file in.
- Add a `jsconfig.json` (or `tsconfig` with `allowJs`/`checkJs`) to turn checking on across the project.
- Annotate with JSDoc, and pull in real types from your `.ts`/`.d.ts`: `/** @type {import('./types').Result} */`.
- Gate it in CI with `tsc --noEmit`, and keep a local "ship" script that runs the same check before pushing.

## Iterators & generators

- **Iterator:** implements `Iterable<T>`; has `next()` returning `{ value, done }`.
- **Generator** (`function*` + `yield`, typed `Generator<T>`) is the simpler way to author iterators. Use for large/infinite sequences. Async variants exist.

## Know it exists, but reach for it rarely

- **Enums:** the basic literal enum is fine; otherwise prefer `as const` unions.
- **Classes:** `private`/`protected`/`static`/`abstract`, constructor param properties, generics, decorators, mixins (`interface C extends A, B {}`). Fine when you need them, but don't default to OOP.
- **Namespaces:** prefer modules.
- **Custom errors:** subclass `Error`, dispatch on `instanceof` — acceptable, but don't drive control flow through exceptions.
- **Dynamic import:** `const m = await import('./widget')`.
