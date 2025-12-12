*******************************************************************************
002. Hierarchical Configuration Following Package Structure
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

Applications and libraries need independent diagnostic configuration without
conflicts. The standard library ``logging`` module addresses this through
logger hierarchies, but has limitations:

* Library developers are strongly advised against custom log levels
* Logger propagation defaults to enabled, causing noise pollution
* Configuration is mutable and can be changed by any code
* Libraries must explicitly opt-out of propagation to avoid interfering with
  applications

The diagnostic system needs:

* **Library isolation**: Libraries configure diagnostics without affecting
  application or other libraries
* **Application control**: Applications can enable/disable library diagnostics
  selectively
* **Hierarchical inheritance**: Subpackages inherit parent configuration with
  local overrides
* **Immutable configuration**: Configuration errors detected at setup time,
  not runtime

Decision
===============================================================================

Implement hierarchical configuration following Python package structure:

**Address-Based Registry**: Configuration keyed by module/package address
(``"myapp"``, ``"myapp.subsystem"``, ``"library"``). Each address specifies
active flavors, max trace level, printer factory, and compositor factory.

**Hierarchical Inheritance**: When resolving configuration for
``"myapp.subsystem.module"``, search in order:

1. Exact match (``"myapp.subsystem.module"``)
2. Parent package (``"myapp.subsystem"``)
3. Grandparent package (``"myapp"``)
4. Global configuration (``None`` key)

First match for each configuration property wins. This allows fine-grained
overrides without duplicating entire configurations.

**Immutable Accretive Registry**: Use accretive dictionary (append-only) for
address registrations. Libraries register during import. Applications can
update active flavors but cannot delete library registrations.

**Per-Flavor Overrides**: Each address can specify per-flavor configuration
(custom compositor, context inclusion). Enables "all errors use logging but
notes use stderr" scenarios.

Alternatives
===============================================================================

**Flat Global Configuration**

Single global configuration with no hierarchy.

*Rejected*: Libraries and applications conflict. No way for libraries to
provide defaults that applications can override. Requires every module to
explicitly configure or use globals (violates library-friendly goal).

**Prefix-Based Matching**

Allow wildcard patterns (``"myapp.*"``, ``"library.*.debug"``).

*Rejected*: Adds regex complexity. Matching order becomes ambiguous (which
pattern takes precedence?). Harder to reason about configuration resolution.
Python package hierarchy already provides natural specificity ordering.

**Logger-Style Propagation**

Follow ``logging`` model: messages propagate up hierarchy with per-level
enable/disable.

*Rejected*: Propagation causes noise pollution (why logging recommends
libraries disable it). Inverted control flow harder to reason about. Disabling
propagation in libraries shifts responsibility to library authors rather than
application users.

**Configuration Files**

Load configuration from TOML/YAML/INI files.

*Rejected*: Adds deployment complexity (where is config file? how to specify
path?). Library configuration awkward (do libraries ship config files?).
Runtime file parsing. Does not eliminate need for programmatic API (testing,
dynamic configuration). File-based config can be added later as optional
convenience.

Consequences
===============================================================================

**Positive Consequences**

* **Library independence**: Each library registers its own configuration
  without seeing or affecting others.
* **Application control**: Applications modify active flavors for specific
  addresses to enable library diagnostics.
* **Inheritance clarity**: Configuration resolution follows Python's own
  package hierarchy, matching developer mental model.
* **Immutability safety**: Accretive registry prevents configuration changes
  after registration (except explicit updates by applications).
* **Testability**: Tests can register temporary configurations that shadow
  defaults without mutation.

**Negative Consequences**

* **Registration timing**: Libraries must register before application
  installation if using builtins pattern (documented deployment pattern).
* **Memory overhead**: Each address stores full configuration even if mostly
  inheriting from parent (mitigated by sharing immutable objects).
* **Discovery complexity**: No introspection API to list all registered
  addresses (could be added if needed).

**Neutral Consequences**

* **Search cost**: Configuration resolution walks up package hierarchy
  (typically 2-4 steps, negligible for diagnostic output).
* **Granularity trade-off**: Per-module configuration possible but not
  required (most users configure at package level).
