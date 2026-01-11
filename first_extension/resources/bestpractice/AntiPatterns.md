
These are the **real production killers** — every large JS/TS system that collapses collapses because of *these exact mistakes.*

---

# 50 Deadliest JavaScript / TypeScript Architectural Anti-Patterns

---

## PROMISE / ASYNC DISASTERS

1. Floating Promises (never awaited or tracked)
2. Async Promise constructors
3. Never-settled Promises (hung jobs)
4. Fire-and-forget without ownership
5. Promise chains with no catch
6. Recursive Promise chains (microtask starvation)
7. `await` inside `forEach`
8. Parallel loops without concurrency limits
9. Blocking `await` in UI thread
10. Returning mixed sync/async APIs

---

## MEMORY LEAK GENERATORS

11. Undisposed event listeners
12. Global caches with no eviction
13. Long-lived closures holding heavy objects
14. Retaining resolved Promises
15. Storing request objects globally
16. Forgotten timers
17. Unbounded arrays/maps
18. Capturing large contexts in lambdas
19. Zombie background tasks
20. Never releasing disposables

---

## EVENT LOOP & THREADING KILLERS

21. CPU-heavy loops on main thread
22. Microtask starvation
23. Infinite async recursion
24. Busy-waiting with Promises
25. Sync I/O in servers/extensions
26. Nested event loops
27. Blocking `Atomics.wait` in main thread
28. Not yielding long loops
29. Ignoring backpressure
30. Worker threads without lifecycle control

---

## ERROR & RELIABILITY FAILURES

31. Swallowing errors
32. Logging without failing
33. Throwing strings
34. Ignoring rejection reasons
35. Converting errors to booleans
36. Partial commits on failure
37. No timeout on remote calls
38. No retries on idempotent operations
39. Cascading failures
40. Silent corruption

---

## ARCHITECTURE ROT

41. Circular module dependencies
42. Static mutable singletons
43. Hidden side effects in imports
44. Business logic in UI layer
45. Runtime type guessing
46. Overuse of `any`
47. Implicit undefined everywhere
48. Framework-coupled domain logic
49. Hard-coded environment assumptions
50. No graceful shutdown path

---

These 50 have **destroyed billion-request systems and VS Code extensions alike.**

---


