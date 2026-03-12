
Below is a **Feature Specification + Testing Strategy** structured as an actual debugger architecture document that maps cleanly onto **VS Code + DAP + GDB MI + multi-core embedded realities**.

This spec is intentionally written at *product architecture level* so it can directly drive:

• Protocol design
• DAP extension schema
• UI/UX panel design
• GDB backend architecture
• Automated test harness
• Certification readiness

---

# Custom Processor Debugger Extension

### Product Feature Specification & Validation Plan

---

# 0. Architectural Positioning

| Layer                | Responsibility                                 |
| -------------------- | ---------------------------------------------- |
| VS Code Extension    | UX, State, Launch Definitions, Views, Commands |
| DAP Server (Node/TS) | Orchestration, multi-core state, UI sync       |
| GDB Controller       | MI2 command scheduler, parser, tracing         |
| Transport            | TCP, serial, JTAG server                       |
| Target               | Simulator / Hardware Board                     |

---

# 1. Launch & Connection System (Foundation Layer)

### Launch Types

| Launch Type              |
| ------------------------ |
| Single Core Simulator    |
| Multi Core Simulator     |
| Single Core Board Attach |
| Multi Core Board Attach  |

### Capabilities

* Simulator spawn (local / docker / remote)
* GDB server attach
* Board reset & halt sequences
* Init script runner
* Multi-GDB or single multi-inferior GDB support
* Pre-launch validation
* Pre-launch task dependencies
* Environment variable injection
* Dynamic GDB server port allocation and identification (single core and multi-core)

### VS Code Domain

* `launch.json`
* Launch configuration validation schema
* Dynamic settings UI for complex arguments
* Auto-generated launch templates

### Tests

| Test                       |
| -------------------------- |
| Sim spawn/kill cycles      |
| Attach/detach stability    |
| Broken GDB recovery        |
| Multi-core attach ordering |
| Script injection tests     |

---

# 2. GDB Initialization & Script System

* Mandatory command chain (internal)
* User script injection
* Board-specific packs
* Version-adaptive MI profile

**Failure recovery + trace replay**

### Tests

* Script fault injection
* Order dependency testing
* Version compatibility matrix

---

# 3. Execution Control

| Feature                     |
| --------------------------- |
| Continue                    |
| Step                        |
| Step Instruction            |
| Step Into                   |
| Step Out                    |
| Drop to Frame               |
| Reverse Step (if supported) |
| Multi-core sync/async       |

### Tests

* Multi-core race conditions
* Latency & stepping determinism
* Instruction boundary accuracy

---

# 4. Breakpoint Engine

| Type                                    |
| --------------------------------------- |
| SW / HW                                 |
| Conditional                             |
| Conditional breakpoint expression caching |
| Thread/Core specific                    |
| Function entry/exit                     |
| Function breakpoint                     |
| Prologue/Epilogue                       |
| Data watchpoints                        |
| Pending breakpoints                     |
| Temporary breakpoints                   |
| Breakpoint hit count filtering          |
| Address Breakpoint                      |
| Address range breakpoints               |
| Live breakpoint insertion while running |

### Tests

* Live BP insertion correctness
* HW slot exhaustion behavior
* Multi-core isolation

---

# 5. Stack, Thread, Core Model

* Stack frame model
* Thread grouping by core
* Core-aware stepping & breakpoints
* UI Core Selector

### Tests

* Context switch storms
* Cross-core BP tests

---

# 6. Variables View

| Capability                    |
| ----------------------------- |
| Per-frame variable resolution |
| Lazy loading                  |
| Large struct paging           |
| Custom formatters             |
| Expression watch persistence  |
| Auto refresh on frame change  |

### Tests

* Deep struct expansion
* Huge stack frames
* Format override accuracy

---

# 7. Register View

| Capability             |
| ---------------------- |
| 1024+ bit registers    |
| Register grouping      |
| Bitfield visualization |
| Per-core context       |
| Format adapters        |

### Tests

* Huge register performance
* Bitfield mapping correctness

---

# 8. Disassembly View

* Mixed source/asm
* Symbolized addresses
* Highlight PC
* Inline stepping

### Tests

* Inlined code stepping
* No-source scenarios

---

# 9. Memory View

| Feature               |
| --------------------- |
| Symbol-based          |
| Address-based         |
| Chunked paging        |
| Refresh watch         |
| Dump/restore          |
| Hex/ASCII/Struct view |

### Tests

* Multi-MB dumps
* Partial failures
* Performance regression

---

# 10. Expression Engine

* GDB expression passthrough
* UI expression persistence
* Auto evaluation on stop

---

# 11. Console Systems

| Console     |
| ----------- |
| GDB Command |
| Trace View  |
| Program I/O |

**Bidirectional sync to UI**

---

# 12. Profiling & Non-Debug Run

* Run without debug
* Trace/coverage hooks
* Instruction counters
* Exportable results

---

# 13. Reset / Power Control

| Reset        |
| ------------ |
| Pre-launch   |
| In-debug     |
| Core-local   |
| Board-global |

---

# 14. State Persistence

* Watch persistence
* Expression persistence
* Memory watch persistence
* Format preferences

---

# 15. Termination & Recovery

| Action              |
| ------------------- |
| Terminate           |
| Detach              |
| Disconnect          |
| Reattach            |
| Hard reset recovery |

---

# 16. Source Mapping

* Auto source root detection
* User override
* Path remapping
* Missing file resolution UI

---

# 17. Telemetry & Stability

* MI transaction tracing
* Deadlock detection
* Auto reconnect
* Crash recovery

---

# 18. UI / UX Domain Integration

| View        |
| ----------- |
| Variables   |
| Registers   |
| Memory      |
| Disassembly |
| Cores       |
| Threads     |
| Trace       |
| GDB Console |
| Profiler    |

---

# 19. Automation & Testing Harness

| Test Type                |
| ------------------------ |
| MI unit tests            |
| Virtual board simulator  |
| Multi-core chaos testing |
| Memory dump stress       |
| Fault injection          |
| Load tests               |

---

# 20. Missing Enterprise-grade Features (Added)

| Feature                    |
| -------------------------- |
| Snapshot/restore           |
| Time travel (if supported) |
| Tracepoints                |
| Coverage                   |
| Scriptable automation      |
| Headless mode              |
| CI regression runner       |

---

