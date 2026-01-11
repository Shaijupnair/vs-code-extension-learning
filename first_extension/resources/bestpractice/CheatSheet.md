Here is the **Master Architect’s Prevention Guide** for VS Code Extension Development.

This document consolidates the 50 architectural patterns we analyzed into a single, high-signal reference. It is designed for **Code Reviews**, **Refactoring Sprints**, and **Onboarding**.

---

# 🛡️ Master Architect’s Prevention Guide

**Target Audience:** Senior Developers & Architects
**Scope:** VS Code Extensions (TypeScript/Node.js)

## **I. Reliability & Resilience (The "It Crashed" Prevention)**

| ID | The Failure Mode | The Smell (Code Review Red Flags) | The Architectural Fix | Impact |
| --- | --- | --- | --- | --- |
| **41** | **Swallowed Promises** | Calling `async` functions without `await` or `.catch()`. | Use a centralized `TaskManager` or `SafeExecutor` to wrap all background tasks. | **Critical** |
| **45** | **Event Throwing** | Throwing errors inside `on('data')` or `EventEmitter` callbacks. | Wrap listeners in `try/catch` or use a `SafeEmitter` decorator. | **Critical** |
| **48** | **Missing Timeouts** | `await new Promise(...)` that waits forever for an external event. | Wrap promises in `Promise.race([task, timeout])` or use a `Watchdog`. | **High** |
| **42** | **No Retry/Backoff** | Connecting to sockets/pipes once and failing immediately. | Implement `Exponential Backoff` with Jitter for network/IPC connections. | **High** |
| **49** | **No Graceful Shutdown** | `process.kill()` used immediately on Stop. | Protocol Shutdown (`-gdb-exit`) → SIGTERM → SIGKILL escalation ladder. | **High** |
| **43** | **Malformed Input** | Reading `config.value` directly without validation. | Use **Zod** or **Joi** schemas to validate & sanitize inputs at the gate. | **Medium** |
| **47** | **No Rate Limiting** | Sending 100 requests to GDB on every Step event. | Use **Request Coalescing** or `debounce` to drop stale requests. | **Medium** |
| **39** | **No Lifecycle Hooks** | Spawning processes that outlive the extension. | Implement `vscode.Disposable` on Services and push to `context.subscriptions`. | **Critical** |
| **50** | **Reload Zombies** | "Port already in use" after reloading window. | Use `tree-kill` in `dispose()` to ensure child process trees are wiped. | **Critical** |
| **30** | **Secrets in JSON** | Storing passwords in `globalState` or settings. | Use `vscode.SecretStorage` (OS Keychain integration). | **Critical** |

---

## **II. Performance & Concurrency (The "It's Slow" Prevention)**

| ID | The Failure Mode | The Smell (Code Review Red Flags) | The Architectural Fix | Impact |
| --- | --- | --- | --- | --- |
| **36** | **Sync FS APIs** | `fs.readFileSync`, `glob.sync` on main thread. | Use `fs.promises` or **Streaming Parsers** (`stream-json`) for large files. | **Critical** |
| **35** | **Direct FS Access** | Hard dependency on `fs` module in logic classes. | Inject an `IFileSystem` interface (Gateway Pattern) for mocking & virtualization. | **High** |
| **29** | **Heavy Activation** | Parsing large JSON/XML inside `activate()`. | **Lazy Initialization**: Load data only when the first command/debug session starts. | **High** |
| **23** | **Unversioned Cache** | Reading JSON cache without checking version fields. | **Schema Migration**: Check `version` field and migrate/discard old data. | **High** |
| **24** | **Cache No TTL** | Unlimited file growth in `globalStorage`. | **LRU Cache Manager**: Enforce Max Size (e.g., 500MB) and Max Age (7 days). | **Medium** |
| **26** | **Concurrent Writes** | Multiple sessions writing to the same file. | **Async Deduplication**: If write is pending, return existing promise. | **Medium** |
| **25** | **Partial Writes** | Writing directly to the final file path. | **Atomic Write**: Write to `.tmp` → `fs.rename()` to target. | **High** |
| **46** | **Stack Overflow** | Recursive functions on unknown data structures. | **Iterative Expansion**: Use an explicit stack/queue on the Heap + Cycle Detection. | **Medium** |

---

## **III. Architecture & Maintainability (The "Spaghetti" Prevention)**

| ID | The Failure Mode | The Smell (Code Review Red Flags) | The Architectural Fix | Impact |
| --- | --- | --- | --- | --- |
| **31** | **God Object** | `GDBController.ts` has 3000+ lines and does everything. | **Service-Oriented**: Split into `BreakpointService`, `VariableService`, etc. | **High** |
| **32** | **Circular Deps** | Module A imports B, B imports A. | **Dependency Inversion**: Extract shared `Interfaces` to a separate package. | **High** |
| **33** | **Global Mutable** | `static currentSession` variables. | **Session Context**: Pass explicit context objects to stateless helpers. | **Critical** |
| **37** | **No Dependency Inv.** | `new DockerMapper()` inside business logic. | **Dependency Injection**: Pass `IPathMapper` in constructor. | **High** |
| **34** | **VS Code Coupling** | Importing `vscode` in core logic files. | **Hexagonal Architecture**: Abstract Host/UI behind an `IHost` adapter. | **Medium** |
| **38** | **Logic in activate** | `activate()` contains complex business logic. | **Composition Root**: `activate` should only wire classes together. | **Medium** |
| **44** | **Using `any**` | `JSON.parse()` results cast to `any`. | **Boundary Validation**: Use **Zod** to validate external data structure at runtime. | **High** |
| **40** | **No Telemetry** | Empty catch blocks or `console.error` only. | **Observability**: Centralized `TelemetryService` with PII sanitization. | **Medium** |

---

## **IV. Memory & Resources (The "Leak" Prevention)**

| ID | The Failure Mode | The Smell (Code Review Red Flags) | The Architectural Fix | Impact |
| --- | --- | --- | --- | --- |
| **1** | **Event Listener Leak** | `on()` without `off()` or `dispose()`. | Use `SafeListen` helper or `context.subscriptions.push()`. | **High** |
| **3** | **Closure Retention** | Large objects captured in long-lived closures. | Clear references (`this.data = null`) manually in `dispose()`. | **Medium** |
| **8** | **Map/Set Growth** | `Map<string, any>` that never shrinks. | Use `WeakMap` or implement a `Pruning Strategy` (clean on session end). | **Medium** |
| **9** | **C++ Buffer Leak** | Passing JS Buffers to C++ add-ons carelessly. | Ensure explicit buffer lifecycle management in Native Modules. | **Low** |

---

## **V. Code Review Checklist (Quick Reference)**

When reviewing a Pull Request, ask these 5 questions:

1. **Safety:** "If this network call hangs forever, does the UI freeze?" (See #48, #41)
2. **Concurrency:** "If the user reloads the window right now, does the background process die?" (See #50, #39)
3. **Scale:** "If the project has 10,000 files, does this sync `fs` call block the Main Thread?" (See #36, #29)
4. **Data:** "If GDB changes its output format, does this crash or show a clear error?" (See #44, #43)
5. **Structure:** "Can I test this logic without mocking the entire VS Code API?" (See #34, #37)

---

### **Next Step**

Would you like me to create a **"Refactoring Roadmap"** based on this guide, helping you prioritize which of these patterns to tackle first in your existing codebase?