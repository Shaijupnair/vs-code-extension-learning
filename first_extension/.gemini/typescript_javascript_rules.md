# TypeScript & JavaScript Rules

## Core Principles
- **Modern Syntax**: Use the latest stable ECMAScript features (ES6+).
- **Type Safety**: In TypeScript, strict typing is mandatory. Avoid `any` at all costs; use `unknown` if necessary.
- **Functional Style**: Prefer pure functions and immutability where possible.

## Variable & Naming Conventions
- Use `const` by default. Use `let` only if reassignment is strictly necessary.
- **Never** use `var`.
- Use `camelCase` for variables and functions.
- Use `PascalCase` for classes, interfaces, types, and React components.
- Boolean variables should use prefixes like `is`, `has`, `can`, or `should` (e.g., `isValid`, `hasAccess`).

## TypeScript Specifics
- **Interfaces vs Types**: Use `interface` for public API definitions and object shapes; use `type` for unions, intersections, and primitives.
- **Explicit Returns**: Always explicitly define the return type for exported functions.
- **Async/Await**: Prefer `async/await` over `.then()` chains.
- **Null Checks**: Use Optional Chaining (`?.`) and Nullish Coalescing (`??`) instead of verbose `&&` checks.

## Code Quality & patterns
- **Early Returns**: Use guard clauses to handle invalid states early and avoid deep nesting.
- **Destructuring**: Prefer object and array destructuring for cleaner access.
- **Equality**: Always use strict equality (`===`) instead of loose equality (`==`).
- **Error Handling**: Do not swallow errors silently. If using `try/catch`, handle the specific error or log it appropriately.

## Prohibited
- Do not use `console.log` in production-ready code blocks (use a proper logger).
- Do not use `namespaces` (use ES Modules `import`/`export`).
- Do not leave unused imports or variables.
