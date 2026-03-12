# GitHub Copilot Instructions — VS Code Extension Development

## 1. Core Language & Type Safety
- **Language**: Always use TypeScript. No `.js` files.
- **Strictness**: Assume `"strict": true`. Never use `any`. Use `unknown` with type guards.
- **Functions**: Always define explicit return types on exported functions. Use JSDoc for all public APIs.
- **Variables**: Prefer `const`. Use `readonly` for immutable properties. Use `===` only.
- **Naming**:
  - Variables/Functions: `camelCase`
  - Classes/Interfaces: `PascalCase`
  - Private Members: `_camelCase` (underscore prefix)
  - Booleans: Use prefixes (`isEnabled`, `hasError`).

## 2. Architecture & Project Structure
- **Entry Point**: Keep `extension.ts` minimal. Register commands/providers and exit.
- **Logic**: Business logic must reside in `src/services/`. No direct VS Code API calls in services (for testability).
- **Organization**:
  - `src/commands/`: One file per command.
  - `src/providers/`: Tree, Hover, and Completion providers.
  - `src/utils/`: Pure helper functions.
- **Disposables**: Every class owning resources must implement `vscode.Disposable`. Push all disposables to `context.subscriptions`.

## 3. VS Code API Patterns
- **Async**: Use `async/await` exclusively. Never use `.then()/.catch()`.
- **I/O**: Use `vscode.workspace.fs` for file operations to support remote/virtual filesystems.
- **Commands**: All command IDs must match `package.json`. Use `window.withProgress` for long-running tasks.
- **Webviews**: 
  - Always use a strict Content Security Policy (CSP).
  - Use `asWebviewUri` for local resources.
  - No `eval()` or inline scripts.
- **Workspace Trust**: Check `vscode.workspace.isTrusted` before performing sensitive operations.

## 4. Error Handling & Logging
- **Try/Catch**: Wrap every `await` call in a `try/catch` block.
- **User Feedback**: Use `window.showErrorMessage` for user-facing errors; log technical details to an `OutputChannel`.
- **Logging**: Use a singleton `vscode.OutputChannel`. No `console.log` in production code.

## 5. Performance & Resource Management
- **Events**: Debounce event handlers (like `onDidChangeTextDocument`).
- **Memory**: Set references to `undefined` in `dispose()` methods. Never hold `TextDocument` references long-term.
- **Activation**: Use specific activation events in `package.json` (e.g., `onCommand`). Never use `*`.

## 6. Testing & Quality
- **Unit Tests**: Test logic in `services/` and `utils/` using mocks.
- **Integration Tests**: Use `@vscode/test-electron` for API-dependent tests.
- **Linting**: Follow `@typescript-eslint/strict` rules. Never disable lint rules without a "why" comment.

## 7. Generation Rules
- Always generate code that includes error handling and disposal logic.
- If a suggested change impacts `package.json` (like adding a command), explicitly mention the required manifest update.
- If a task is complex, explain the architecture briefly before providing the code.