

---

# JavaScript / TypeScript Memory Leak Field Guide

> Memory leaks in JS are **reference leaks, not allocation leaks**.
> Garbage collector only frees *unreachable* objects — everything reachable leaks.

---

## Memory Root Model

Anything reachable from:

• Global objects
• Module singletons
• Event listeners
• Timers
• Closures
• Active Promises

…is a GC root and **will never be freed.**

---

# 15 Deadly Leak Patterns

---

## 1. Undisposed Event Listeners (MOST COMMON)

```ts
fs.watch(path, () => {...});   // never disposed
```

Leaking root: event emitter

Fix:

```ts
const w = fs.watch(...);
w.close();
```

---

## 2. Floating Background Promises

```ts
importData(url);  // no owner
```

Leak: Promise keeps closures alive forever

Fix: supervisor ownership

---

## 3. Forgotten Timers

```ts
setInterval(() => heavyObject.do(), 1000);
```

Leak: timer keeps heavyObject forever

Fix: `clearInterval`

---

## 4. Global Caches with No Eviction

```ts
const cache = new Map();
```

Leak: infinite retention

Fix: LRU / TTL / WeakMap

---

## 5. Retained Resolved Promises

```ts
const p = doTask();
cache.set(id, p);
```

Leak: p keeps all captured data forever

Fix: store result, not Promise

---

## 6. Closures Capturing Large Context

```ts
items.forEach(i => bigObj.process(i));
```

Leak: closure keeps bigObj

Fix: pass minimal data

---

## 7. Unbounded Arrays

```ts
logs.push(event);  // forever
```

Leak: permanent heap growth

Fix: rolling buffer

---

## 8. Zombie Worker Threads

```ts
new Worker("./task.js");  // never terminated
```

Leak: OS thread + heap leak

Fix: worker.terminate()

---

## 9. Retained Request Objects

```ts
sessions.set(req.id, req);
```

Leak: sockets + buffers retained

Fix: extract minimal data

---

## 10. Observer Registrations

```ts
model.on("change", handler);
```

Leak: model → handler → captured data

Fix: removeListener

---

## 11. Never-cleared AbortControllers

```ts
const ac = new AbortController();
```

Leak: retains signal listeners

Fix: cleanup listeners

---

## 12. Circular Domain Object Graphs

GC can handle cycles — but roots keep whole graph alive

Fix: break references

---

## 13. Streaming without Close

```ts
stream.on("data", ...);
```

Fix: stream.destroy()

---

## 14. Retaining Large JSON Blobs

Fix: stream + chunk

---

## 15. Static Singletons with State

```ts
class Store { static data = []; }
```

Leak: never freed

---

# How to Find Leaks (Real Methods)

| Tool                            | What it shows  |
| ------------------------------- | -------------- |
| `--inspect` heap snapshot       | Retained roots |
| Chrome DevTools                 | Dominators     |
| `clinic heapprofile`            | Growth         |
| `process.memoryUsage()`         | Trend          |
| VS Code extension host devtools | UI leaks       |

---

# Leak Smell Tests

• Memory grows linearly
• GC time increases
• CPU spikes after idle
• Heap never returns baseline
• Extension host becomes sluggish

---

# Architect Rule

> If you don’t explicitly free it — it leaks.

---



 this is the **real production survival checklist.**
Use this whenever a Node service or VS Code extension starts slowing down, freezing, or crashing after hours/days.

---

# Memory Leak Debugging Checklist (JS / TS / Node / VS Code)

---

## PHASE 1 — Confirm a Leak Exists

### 1. Check live memory trend

```ts
setInterval(() => {
  const m = process.memoryUsage();
  console.log((m.heapUsed / 1024 / 1024).toFixed(1), "MB");
}, 30000);
```

✔ If heap grows continuously → leak confirmed
✔ If it oscillates → normal GC

---

## PHASE 2 — Take Heap Snapshots

Run with:

```
node --inspect index.js
```

or VS Code Extension Host → Developer Tools → Memory

1️⃣ Snapshot at cold start
2️⃣ Snapshot after workload
3️⃣ Snapshot after idle GC

✔ Compare retained object growth

---

## PHASE 3 — Find Retained Roots

In DevTools:

• Sort by **Retained Size**
• Open **Dominator Tree**
• Look for growing Maps, Arrays, Closures, Promises, Listeners

These are your leaks.

---

## PHASE 4 — Match Leak Patterns

| If you see            | Suspect              |
| --------------------- | -------------------- |
| Growing Map           | Cache leak           |
| Growing Closure       | Floating promises    |
| Growing EventListener | Undisposed listeners |
| Growing Promise       | Hung jobs            |
| Growing Buffer        | Streams not closed   |
| Growing Timeout       | Forgotten timers     |

---

## PHASE 5 — Verify Ownership

For each suspect:

• Who created it?
• Who owns it?
• Who disposes it?

If answer #3 is missing → leak found.

---

## PHASE 6 — Patch with Lifetime Control

Add `.finally()`, `.dispose()`, `.close()`, `clearTimeout()`, `AbortController`, LRU eviction.

---

## PHASE 7 — Validate Fix

Repeat snapshots:

✔ heap returns to baseline
✔ no linear growth
✔ GC cycles stabilize

---

## PHASE 8 — Hardening Rules

| Rule                      | Purpose                 |
| ------------------------- | ----------------------- |
| Track all background jobs | Prevent zombie Promises |
| Centralize disposables    | No forgotten listeners  |
| Add TTL to caches         | No infinite retention   |
| Add shutdown hooks        | Clean exit              |
| Add concurrency limits    | Avoid explosion         |

---

## Quick Leak Sniff Test

If memory increases when idle → you still have a leak.

---

## Architect mantra

> **Leaks are not bugs. They are missing lifecycles.**

---
Excellent — VS Code extensions are **leak factories** if not architected correctly.
This is the *real anatomy of how they leak and how they die.*

---

# VS Code Extension Leak Anatomy

> The Extension Host is a long-running Node.js process.
> Anything you leak stays **forever** — even after disabling your extension.

---

## Primary Leak Roots

| Root                           | Why it leaks               |
| ------------------------------ | -------------------------- |
| context.subscriptions          | Disposables never disposed |
| vscode.EventEmitter            | Listener chains            |
| setInterval / setTimeout       | Permanent roots            |
| Floating Promises              | Hung microtasks            |
| Global singletons              | Never freed                |
| Language Server Protocol (LSP) | Zombie processes           |

---

# 12 Real Leak Mechanisms

---

## 1. Undisposed Disposables (Killer #1)

```ts
vscode.workspace.onDidChangeTextDocument(handler);
```

Leak: handler retained forever

Fix:

```ts
context.subscriptions.push(
  vscode.workspace.onDidChangeTextDocument(handler)
);
```

---

## 2. Zombie Background Tasks

```ts
startIndexer();  // no ownership
```

Leak: Promise keeps closures

Fix: job supervisor

---

## 3. Never-cleared Timers

```ts
setInterval(refresh, 5000);
```

Fix: clearInterval in deactivate()

---

## 4. Webview Event Retention

```ts
panel.webview.onDidReceiveMessage(...)
```

Leak: panel holds extension memory

Fix: dispose panel & remove listeners

---

## 5. Unbounded File Watchers

```ts
vscode.workspace.createFileSystemWatcher("**/*");
```

Leak: OS handles + closures

Fix: dispose watcher

---

## 6. Retained Large Models

ASTs, symbol tables stored globally

Fix: TTL eviction

---

## 7. LSP Zombie Servers

Language server processes never terminated

Fix: server.stop()

---

## 8. Retained Diagnostics

`languages.createDiagnosticCollection()` not disposed

---

## 9. Floating async loops

`while(true) await sleep()`

Fix: cancellation

---

## 10. Cached Promises

```ts
cache.set(uri, analyze(uri));
```

Fix: cache result, not Promise

---

## 11. Stale TextDocument References

Keep full doc objects

Fix: store uri + version only

---

## 12. Unbounded OutputChannel Logs

Never cleared output channels

---

# How Extensions Die

| Symptom        | Root Cause             |
| -------------- | ---------------------- |
| Slow UI        | Microtask starvation   |
| High RAM       | Listener & cache leaks |
| Never unload   | Zombie jobs            |
| Needs reload   | Hung Promises          |
| Random freezes | Worker thread leaks    |

---

# Hardening Pattern

```ts
export function activate(ctx: vscode.ExtensionContext) {
    const jobs = new JobSupervisor();
    ctx.subscriptions.push(jobs);

    const timer = setInterval(runTask, 5000);
    ctx.subscriptions.push({ dispose: () => clearInterval(timer) });
}
```

Everything has a lifecycle.
Everything must die.

---

# Architect Rule

> **If it does not die — it leaks.**

---
This is a *very important* topic.
## **VS Code Webviews are the #1 hidden memory-leak vector in extension development.**

Let’s dissect exactly how they leak and how to build them safely.

---

# VS Code Webview Memory Traps (Field Guide)

> Webviews run in a separate Chromium process, but **their JS objects, message ports, and closures leak into the Extension Host** if misused.

---

## Why Webviews Are Dangerous

Every webview creates:

• A Chromium renderer
• A message channel
• Event bridges
• Closure references inside extension host

If you forget to destroy any of these — your extension host never frees memory.

---

# 12 Deadly Webview Leak Traps

---

## 1. Not disposing WebviewPanel

```ts
const panel = vscode.window.createWebviewPanel(...);
```

Leak: panel retains Chromium renderer + JS bridge forever.

Fix:

```ts
ctx.subscriptions.push(panel);
```

---

## 2. Unreleased onDidReceiveMessage listeners

```ts
panel.webview.onDidReceiveMessage(msg => handle(msg));
```

Leak: closure retains entire extension context.

Fix:

```ts
ctx.subscriptions.push(
  panel.webview.onDidReceiveMessage(...)
);
```

---

## 3. Message storms (microtask starvation)

```ts
setInterval(() => panel.webview.postMessage(state), 10);
```

Leak: microtask queue explosion, memory pressure.

Fix: debounce, throttle, batch.

---

## 4. Retaining Webview state objects

Large JSON state stored in memory forever.

Fix: persist minimal state externally.

---

## 5. Leaking DOM event handlers in webview

Webview JS:

```js
button.onclick = () => bigObject.do();
```

Leak: never removed → Chromium heap leak.

Fix: removeEventListener on unload.

---

## 6. Retaining TextDocument in closures

```ts
const doc = editor.document;
panel.webview.onDidReceiveMessage(() => doc.getText());
```

Leak: full file buffer retained.

Fix: store URI only.

---

## 7. Not clearing webview intervals

Webview JS:

```js
setInterval(poll, 1000);
```

Leak: renderer never GC’s.

Fix: clearInterval on dispose.

---

## 8. Multiple hidden panels

Hidden but not disposed webviews still retain memory.

Fix: singletons + reuse.

---

## 9. Webview recreates instead of reuse

Repeated open creates multiple renderers.

Fix: panel reuse.

---

## 10. Using `retainContextWhenHidden: true` blindly

Huge Chromium heap retained forever.

Fix: avoid unless necessary.

---

## 11. Blob URLs never revoked

```js
URL.createObjectURL(blob);
```

Leak: huge binary blobs retained.

Fix: URL.revokeObjectURL()

---

## 12. Bidirectional closure retention

Extension ↔ Webview closures keep each other alive.

Fix: message-only protocol, no function passing.

---

# Golden Webview Rule

> Treat Webviews like browser tabs —
> If you don’t close them, your extension host slowly dies.

---

# Safe Webview Template

```ts
const panel = vscode.window.createWebviewPanel(...);
ctx.subscriptions.push(panel);

ctx.subscriptions.push(
  panel.webview.onDidReceiveMessage(msg => handle(msg))
);
```

Webview JS:

```js
window.addEventListener("unload", () => {
  clearInterval(timer);
});
```

---


