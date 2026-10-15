# checkJs config

Example strict config copied from `cds-driver-management-exp`.

Backend (`backend/tsconfig.json`) targets Node. `module` and `moduleResolution` are `Node16`, `lib` is ES2024, and `types` is Node plus Jest. `include` is the journeys island only: `v4/journeys/**/*.js` and `v4/journeys/**/*.d.ts`.

Frontend (`frontend/tsconfig.json`) targets the bundler. It adds `DOM` libs, `jsx: react-jsx`, `module: ESNext`, `moduleResolution: Bundler`, path aliases, and Vitest types. `include` is an allowlist of journey API files plus the multi-stop-planning tree (`*.js`, `*.jsx`, `*.d.ts`), not the whole frontend.

## Backend

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2024"],
    "module": "Node16",
    "moduleResolution": "Node16",
    "allowJs": true,
    "checkJs": true,
    "noEmit": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitThis": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    "forceConsistentCasingInFileNames": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "maxNodeModuleJsDepth": 0,
    "types": ["node", "jest"]
  },
  "include": [
    "v4/journeys/**/*.js",
    "v4/journeys/**/*.d.ts"
  ]
}
```

## Frontend

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "allowJs": true,
    "checkJs": true,
    "noEmit": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitThis": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    "forceConsistentCasingInFileNames": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "maxNodeModuleJsDepth": 0,
    "paths": {
      "@/*": ["./src/*"],
      "#test-ids": ["./src/test-ids/index.js"]
    },
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": [
    "src/api/hooks/useJourneys.js",
    "src/api/hooks/tests/useJourneys.test.js",
    "src/api/queries/journeys.js",
    "src/api/queries/tests/journeys.test.js",
    "src/types/connex-cds.d.ts",
    "src/views/driver-management-new/views/multi-stop-planning/**/*.js",
    "src/views/driver-management-new/views/multi-stop-planning/**/*.jsx",
    "src/views/driver-management-new/views/multi-stop-planning/**/*.d.ts"
  ]
}
```
