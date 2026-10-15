// eslint.config.mjs — ESLint v9 flat config with typed linting.
// Requires: eslint @eslint/js typescript-eslint  (see setup.md)
import eslint from '@eslint/js'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist/', 'build/', 'coverage/', 'node_modules/'] },

  eslint.configs.recommended,
  // Type-aware strict rules: bans `any`, the no-unsafe-* family, floating promises, etc.
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  {
    languageOptions: {
      parserOptions: {
        projectService: true, // discovers tsconfig automatically for typed rules
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // --- Align presets to the house style --------------------------------
      // stylisticTypeChecked defaults this to 'interface'; we prefer `type`.
      '@typescript-eslint/consistent-type-definitions': ['error', 'type'],
      // Enforce `import type` (pairs with verbatimModuleSyntax).
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
      ],

      // --- Opinions the presets don't enable -------------------------------
      '@typescript-eslint/switch-exhaustiveness-check': 'error', // forces assertNever / full unions
      '@typescript-eslint/prefer-readonly': 'error',
      '@typescript-eslint/method-signature-style': ['error', 'property'],
      'prefer-const': 'error',
      'no-var': 'error',

      // Project convention: prefer `undefined` over `null`. Off by default
      // because it fights DOM/3rd-party APIs (useRef(null), getElementById).
      // Turn on in app code you fully control:
      // 'no-restricted-syntax': [
      //   'error',
      //   { selector: 'TSNullKeyword', message: 'Prefer undefined over null.' },
      // ],
    },
  },

  // Tests: loosen strictness where it only adds noise.
  {
    files: ['**/*.{test,spec}.{ts,tsx}', 'tests/**'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unsafe-assignment': 'off',
      '@typescript-eslint/no-non-null-assertion': 'off',
    },
  },
)
