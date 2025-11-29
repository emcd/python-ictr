*******************************************************************************
001. Layered Architecture with Protocol-Based Boundaries
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

The diagnostic output system needs to support multiple usage patterns:
developers want simple one-line debug statements, libraries need non-intrusive
registration, and applications require fine-grained control over output
formatting and routing. Existing approaches either tightly couple components
(hard to extend) or require extensive boilerplate (poor developer experience).

The system must accommodate:

* **Multiple output targets**: stderr (default), files, logging integration,
  custom sinks
* **Multiple formatting strategies**: plain text, Rich-colorized, custom
  layouts
* **Library-friendly configuration**: per-module settings without global
  pollution
* **Optional dependencies**: Rich library should enhance but not be required
* **Testing support**: output capture, deterministic formatting

Decision
===============================================================================

Implement a four-layer architecture with protocol-based boundaries:

**Layer 1 - Dispatcher**: Entry point managing reporter selection and
activation control. Provides attribute-based access (``ctrl.note(...)``) and
caches reporter instances per address + flavor combination.

**Layer 2 - Reporter**: Coordination layer binding textualizer to printer for
specific address + flavor. Handles active/inactive state and packages user
content into structured records.

**Layer 3 - Textualizer**: Transforms records into formatted text lines using
composed subsystems (introducer for prefixes, linearizers for content).
Receives column constraints from printer layer.

**Layer 4 - Printer**: Abstracts output targets. Provides textualizer control
information (columns, colorization capability) and writes formatted output.

Layers communicate through protocols (structural typing) rather than
inheritance, enabling independent implementation and testing.

Alternatives
===============================================================================

**Single Monolithic Class**

Combine dispatcher, formatting, and output in one class with template methods
for customization.

*Rejected*: Violates single responsibility principle. Hard to test formatting
without output. Configuration becomes unwieldy (one class with 20+ template
methods). Cannot independently replace formatting vs output strategies.

**Observer Pattern with Event Bus**

Route messages through event bus to registered handlers.

*Rejected*: Over-engineering for diagnostic output. Async complexity not
needed. Per-module configuration becomes awkward (need module-scoped
subscriptions). Testing harder (must mock event bus infrastructure).

**Plugin Architecture with Entry Points**

Use setuptools entry points for formatters and outputs.

*Rejected*: Runtime configuration more important than install-time plugins.
Adds packaging complexity. Testing requires filesystem manipulation.
Per-module configuration unclear (how to specify which module uses which
plugin).

Consequences
===============================================================================

**Positive Consequences**

* **Independent evolution**: Layers can change implementation without
  affecting others as long as protocols are maintained.
* **Testing clarity**: Each layer tests independently with mock
  implementations of dependencies.
* **Configuration flexibility**: Factory pattern enables per-address,
  per-flavor customization at each layer.
* **Optional dependencies**: Rich integration isolated in textualizer layer
  with graceful fallback.
* **Clear extension points**: Protocols document exactly what custom
  implementations must provide.

**Negative Consequences**

* **Indirection overhead**: Four layers add call stack depth compared to
  monolithic approach (negligible for diagnostic output).
* **Protocol verbosity**: Each protocol requires TypedDict or Protocol
  definition plus documentation.
* **Learning curve**: Developers must understand layer responsibilities to
  customize effectively.

**Neutral Consequences**

* **Factory pattern ubiquity**: Almost every component uses factory pattern
  for instantiation (consistent but more conceptual overhead).
* **Protocol over ABC**: Structural subtyping more flexible but less explicit
  than abstract base classes.
