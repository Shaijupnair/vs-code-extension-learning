Here is the  **Master Architect’s Playbook** containing all **112 Principles**. This combines the original production-hardened list with the 12 modern architectural additions, organized by domain.

### **ASYNC / CONCURRENCY / PROMISES**

1. Every Promise must have an owner.
2. Never create floating Promises.
3. Never await inside hot UI paths.
4. Never use async Promise constructors.
5. One Promise = one transaction.
6. Use Promise.allSettled for partial failure tolerance.
7. Never allow hung Promises.
8. Always time-bound remote calls.
9. Always cancel background jobs on shutdown.
10. Limit concurrency explicitly.
11. **Circuit Breakers over Retries:** Stop calling failing dependencies immediately to prevent thundering herds.

### **MEMORY & RESOURCE SAFETY**

12. Every event listener must be disposed.
13. Every file handle must be closed.
14. Never keep long-lived closures.
15. Never store large objects in globals.
16. Avoid retaining Promise chains.
17. Use weak maps for caches.
18. Release references in `.finally()`.
19. Always clear timers.
20. Never leak disposables.
21. Treat closures as memory roots.

### **ERROR HANDLING**

22. Never swallow errors.
23. Errors must be centralized.
24. No silent `catch {}` blocks.
25. Every failure path must be observable.
26. Convert errors into domain errors.
27. Never throw strings.
28. Never rely on console logging for errors.
29. Do not mix exception and error-code models.
30. Fail fast on invalid state.
31. Log root causes, not symptoms.
32. **Result Types over Throwing:** Prefer returning `Result<T, Error>` to make failure modes explicit in the type system.

### **DESIGN & STRUCTURE**

33. One module = one responsibility.
34. No circular dependencies.
35. Never depend on runtime side effects.
36. Never hide async inside sync APIs.
37. APIs must be cancellation-aware.
38. No static mutable state.
39. Separate orchestration from execution.
40. Prefer composition over inheritance.
41. Domain logic must be framework-free.
42. No business logic in UI layer.
43. **Functional Core, Imperative Shell:** Push side effects (I/O) to the system boundaries; keep core logic pure.
44. **Idempotency is Mandatory:** Every retry-able operation must safely handle being called multiple times.
45. **Context Keys are State (VS Code):** Drive UI visibility via declaration, not imperative code logic.

### **TYPESCRIPT TYPE SYSTEM**

46. No `any` in core layers.
47. Prefer `unknown` over `any`.
48. Make illegal states unrepresentable.
49. Model domain invariants in types.
50. Use branded types for IDs.
51. Never widen types unnecessarily.
52. No implicit undefined.
53. Prefer `readonly`.
54. Always type async returns explicitly.
55. Avoid structural typing for domain IDs.
56. **Exhaustive Matching:** Switch statements on unions must handle every case (enforced via `never` type).

### **PERFORMANCE**

57. No synchronous I/O in servers.
58. Avoid large JSON in memory.
59. Use streaming for large data.
60. Use chunked processing.
61. Measure before optimizing.
62. Avoid hot Promise chains.
63. Batch network calls.
64. Avoid repeated parsing.
65. Cache immutable results.
66. Bound memory growth.
67. **Lazy Activation:** Do zero work at startup; import modules only when the user executes a command.

### **EVENT LOOP / THREADING**

68. Never block the event loop.
69. Move CPU heavy work to workers.
70. Avoid microtask starvation.
71. Never spin in async loops.
72. Use backpressure.
73. Yield long loops.
74. Avoid recursive Promise chains.
75. Use `worker_threads` when needed.
76. Understand libuv pools.
77. Treat event loop as scarce resource.

### **TESTABILITY**

78. Every module must be testable in isolation.
79. Avoid hidden singletons.
80. No random behavior without seeding.
81. Time must be injectable.
82. IO must be abstracted.
83. No side effects in constructors.
84. Avoid global config.
85. No hardcoded paths.
86. Deterministic tests only.
87. Test async failure paths.

### **SECURITY & ROBUSTNESS**

88. Validate all external input.
89. Never trust JSON schemas blindly.
90. No dynamic eval.
91. Escape all shell args.
92. Avoid prototype pollution.
93. Freeze config objects.
94. Never log secrets.
95. No secrets in code.
96. Avoid regex DOS.
97. Fail closed, not open.
98. **Webviews are Untrusted Sandboxes:** Treat Webview messages exactly like external API calls (validate & sanitize).
99. **Degrade Gracefully:** If an optional service fails, the main application must remain usable.

### **DEPLOYMENT & OPERATIONS**

100. Every background job must shutdown cleanly.
101. Health checks must exist.
102. All critical paths must be observable.
103. Graceful shutdown always.
104. Config must be externalized.
105. Support rolling upgrades.
106. No magic environment assumptions.
107. Build artifacts must be immutable.
108. Logs must be structured.
109. Treat Node as long-running service, not script.
110. **Correlation IDs are Non-Negotiable:** Every log entry must be traceable to a specific request ID.
111. **Lock Your Supply Chain:** Commit lockfiles and use strict dependency versioning.
112. **Telemetry is for Usage:** Measure feature adoption and usage patterns, not just error rates.