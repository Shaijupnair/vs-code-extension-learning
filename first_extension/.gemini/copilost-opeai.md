
# GitHub Copilot Instructions for VS Code Extension Development

## 1. Language and Type Safety Rules

* Always prefer **TypeScript over JavaScript**.
* Enable `"strict": true` in `tsconfig.json`.
* Never use `any`. If absolutely necessary, use `unknown` and narrow it properly.
* Always define explicit return types for functions.
* Use `readonly` where mutation is not required.
* Avoid implicit `undefined`. Use union types like `string | undefined`.
* Never rely on type coercion. Always use strict equality (`===`).

### Example Standard

```ts
function activate(context: vscode.ExtensionContext): void {
  // Explicit return type
}
```

---

## 2. Module System and Imports

* Use ES Modules syntax.
* Never mix `require()` and `import`.
* Use named imports instead of `import * as`.
* Avoid default exports in extensions.

Correct:

```ts
import { window, commands, ExtensionContext } from 'vscode';
```

Wrong:

```ts
const vscode = require('vscode');
```

---

## 3. Async and Concurrency Rules

* Never use `.then()` chains. Always use `async/await`.
* Always wrap async code in `try/catch`.
* Never ignore returned promises.
* Never block the event loop with synchronous file or CPU-heavy operations.

Correct:

```ts
try {
  const result = await someAsyncOperation();
} catch (error: unknown) {
  if (error instanceof Error) {
    console.error(error.message);
  }
}
```

---

## 4. VS Code Extension Architecture Rules

* Keep `activate()` minimal.
* Register commands inside `activate()`.
* Dispose all disposables via `context.subscriptions.push(...)`.
* Separate business logic from VS Code API logic.
* Do not put heavy logic directly inside command callbacks.

Structure:

```
src/
  extension.ts
  commands/
  services/
  utils/
```

---

## 5. Error Handling Strategy

* Never swallow errors.
* Always log using `console.error` or VS Code `OutputChannel`.
* Show user-friendly messages using `window.showErrorMessage`.
* Distinguish between programmer errors and runtime errors.

---

## 6. Performance Rules

* Avoid large synchronous loops.
* Use streaming for large file processing.
* Cache results where appropriate.
* Debounce event handlers.
* Never recompute heavy logic on every event trigger.

---

## 7. Memory and Resource Management

* Always dispose:

  * Event listeners
  * Webview panels
  * Timers
  * File watchers
* Avoid global mutable state.
* Use singleton pattern carefully.

---

## 8. Configuration Management

* Always define settings in `package.json`.
* Use `workspace.getConfiguration()` to read settings.
* Validate configuration values before using them.
* Do not assume config exists.

---

## 9. Logging Standards

* Use a dedicated `OutputChannel`.
* Do not spam logs.
* Use structured logging style.
* Provide debug toggle via configuration.

---

## 10. Webview Safety Rules

* Always use `Webview.asWebviewUri`.
* Never inject raw user input into HTML.
* Enable Content Security Policy.
* Avoid inline scripts.
* Use message passing via `postMessage`.

---

## 11. Node.js API Usage Rules

* Prefer `fs/promises` over callback style.
* Avoid deprecated Node APIs.
* Handle path using `path` module.
* Never assume OS-specific path separators.

---

## 12. Testing Standards

* Use `@vscode/test-electron`.
* Write unit tests for logic outside VS Code API.
* Mock VS Code APIs.
* Avoid integration tests unless required.

---

## 13. Linting and Formatting

* Use ESLint with TypeScript rules.
* Enable:

  * noImplicitAny
  * strictNullChecks
  * noUnusedLocals
  * noUnusedParameters
* Use Prettier for formatting.
* Never disable lint rules without reason.

---

## 14. Coding Style Requirements

* No implicit returns in arrow functions for complex logic.
* Use named functions for complex logic.
* Keep functions small (single responsibility).
* Avoid nested callbacks.
* Use early return instead of deep nesting.

---

## 15. Security Rules

* Validate all external inputs.
* Do not execute shell commands without sanitization.
* Avoid eval().
* Do not trust workspace files blindly.
* Handle untrusted workspace mode properly.

---

## 16. Packaging Rules

* Always define `engines.vscode`.
* Keep activation events minimal.
* Avoid `*` activation.
* Bundle extension using `esbuild` or `webpack`.
* Tree-shake unused code.

---

## 17. How Copilot Should Generate Code

When generating code:

* Always include type definitions.
* Include error handling.
* Include disposal logic.
* Avoid global mutable variables.
* Include comments explaining execution flow.
* Provide explanation of edge cases.
* Follow strict TypeScript conventions.
* Generate modular code.
