.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Product Requirements Document
*******************************************************************************

Executive Summary
===============================================================================

This package is a non-intrusive logging and debug printing system for Python
applications that provides a clean, type-safe API for emitting diagnostic
messages. It serves as a complete reimplementation and evolution of the
``icecream-truck`` package, offering standard message flavors (note, error,
success, etc.), hierarchical trace levels, automatic exception tracebacks, and
optional rich formatting.

The product enables both quick debugging sessions and production logging with
minimal boilerplate, featuring an optional global dispatcher pattern that
reduces boilerplate while maintaining fine-grained per-module configuration
control.

Problem Statement
===============================================================================

Python developers face several challenges with existing debugging and logging
solutions:

**Configuration vs. Convenience Trade-off**: The standard library ``logging``
module provides powerful features but requires understanding of loggers,
handlers, formatters, and propagation rules. While ``print()`` debugging is
quick, it lacks structure and filtering. The ``icecream`` package bridges this
gap with ``ic.install()`` for global access, but still offers limited control
over output categorization and filtering.

**Library Integration Conflicts**: Libraries using ``logging`` can conflict
with application logging configuration. Library developers are strongly advised
not to create custom log levels, and logger propagation can cause unwanted
output spam. There is no good way for libraries and applications to coexist
without configuration clashes.

**Insufficient Debugging Granularity**: The ``logging`` module provides only
one DEBUG level. Developers need multiple debugging depths to control output
verbosity during development and troubleshooting without being overwhelmed by
trace noise from deeply nested calls or verbose subsystems.

**Incomplete Exception Context**: While ``logging`` provides ``exc_info`` for
capturing tracebacks, developers must remember to enable it explicitly. Many
diagnostic scenarios would benefit from automatic exception capture with full
stack traces, exception chaining (``__cause__`` and ``__context__``), and
readable formatting.

**Extensibility Gaps**: While it is not difficult to integrate packages like
``rich`` with ``logging`` or ``icecream``, there is repetitive code involved
across projects. There should be graceful import fallbacks if optional
dependencies fail to load, and recipes to reduce boilerplate for common
integration patterns.

Goals and Objectives
===============================================================================

Primary Objectives
-------------------------------------------------------------------------------

* **Minimal boilerplate**: Enable diagnostic output with single-line calls
  after initial setup.

* **Hierarchical debugging**: Provide 10 trace levels (0-9) for granular
  control over debugging output depth and automatic indentation visualization.

* **Library-friendly**: Allow libraries to register configurations without
  conflicting with application settings or other libraries.

* **Deep exception reporting**: Automatically capture and format exception
  tracebacks with full stack traces and exception chaining.

* **Production-safe**: Support leaving diagnostic calls in production code with
  fine-grained activation control per module and flavor.

Secondary Objectives
-------------------------------------------------------------------------------

* **Rich formatting integration**: Seamlessly integrate with Rich library for
  colorized, styled output when available.

* **Extensibility**: Provide clear extension points for custom compositors,
  introducers, and output targets.

* **Type safety**: Full type hint coverage for IDE autocomplete and static
  analysis support.

Success Metrics
-------------------------------------------------------------------------------

* Developers can add basic diagnostic output with ≤3 lines of setup code.
* Trace level output visually shows call depth through indentation.
* Exception tracebacks include full stack traces and chained exceptions.
* Libraries can register without affecting application or other library configs.
* All public APIs have complete type annotations.

Target Users
===============================================================================

Application Developers
-------------------------------------------------------------------------------

**Profile**: Python developers building applications who need debugging and
diagnostic output during development and production troubleshooting.

**Needs**:

* Quick debugging during development without setup overhead.
* Structured diagnostic output that can be filtered by severity/category.
* Production-safe logging that can be selectively enabled per module.
* Clear exception reporting with full context.

**Technical proficiency**: Intermediate to advanced Python developers
comfortable with type hints and modern Python features (3.10+).

**Usage context**: Command-line applications, web services, data processing
pipelines, and other Python applications requiring diagnostic output.

Library Developers
-------------------------------------------------------------------------------

**Profile**: Python package authors who want to provide diagnostic output
without interfering with application logging configuration.

**Needs**:

* Non-intrusive registration that doesn't pollute global configuration.
* Ability to define library-specific flavors and output formats.
* Coexistence with other libraries and application logging.
* Respect for application's choice to enable/disable library diagnostics.

**Technical proficiency**: Advanced Python developers familiar with package
distribution and API design.

**Usage context**: Open source libraries, internal company packages, and shared
utilities that need optional diagnostic capabilities.

Functional Requirements
===============================================================================

Core Diagnostic System (Critical Priority)
-------------------------------------------------------------------------------

**REQ-001: Optional Global Access**

The package must support optional installation into Python builtins for
convenient access from any module without explicit imports.

Acceptance Criteria:

* Installation function makes diagnostic system available in builtins.
* Default builtin name is configurable.
* Installation preserves existing builtin attributes.
* Raises exception if builtin name conflicts with existing attribute.
* Direct instantiation and usage without builtins must also be supported.

**REQ-002: Message Categorization**

The package must support categorizing diagnostic messages by flavor name or
numeric trace level.

Acceptance Criteria:

* String flavor names (e.g., 'note', 'error') select message categories.
* Numeric trace levels 0-9 select debugging depth categories.
* Category selection returns callable object for emitting messages.
* Invalid category names raise clear exceptions.

**REQ-003: Selective Activation**

The package must support enabling/disabling diagnostic output by category and
module.

Acceptance Criteria:

* Default active categories include all standard message flavors.
* Active categories can be specified globally.
* Active categories can be specified per module/package.
* Disabled categories produce no output.

Standard Message Categories (Critical Priority)
-------------------------------------------------------------------------------

**REQ-004: Semantic Message Categories**

The package must provide standard message categories with semantic meanings for
common diagnostic scenarios.

Acceptance Criteria:

* ``note`` category for informational messages.
* ``monition`` category for warnings.
* ``error`` category for error conditions without exception tracebacks.
* ``errorx`` category for errors with automatic exception traceback capture.
* ``abort`` category for critical failures without exception tracebacks.
* ``abortx`` category for critical failures with automatic exception traceback
  capture.
* ``future`` category for deprecation warnings and upcoming changes.
* ``success`` category for successful operation confirmations.
* ``advice`` category for suggested actions or recommendations.
* Each category has distinct visual styling in output.

**REQ-005: Category Aliases**

The package must provide short aliases for standard categories to reduce typing
during interactive debugging.

Acceptance Criteria:

* Single-letter aliases: ``n``, ``m``, ``e``, ``a``, ``f``, ``s``, ``v``.
* Aliases map to corresponding full category names.
* Aliases behave identically to full category names.

Hierarchical Trace Levels (Critical Priority)
-------------------------------------------------------------------------------

**REQ-006: Visual Debugging Depth**

The package must support numeric trace levels with automatic indentation to
visualize call depth and execution flow.

Acceptance Criteria:

* Trace levels 0 through 9 are supported.
* Each level adds 2 spaces of indentation to output.
* Trace level 0 has no indentation.
* Trace level 9 has 18 spaces of indentation (9 * 2).

**REQ-007: Depth Filtering**

The package must support setting maximum active trace level to control
debugging output verbosity.

Acceptance Criteria:

* Global maximum trace level can be configured.
* Per-module maximum trace level can be configured.
* Trace levels above maximum produce no output.
* Default maximum trace level is -1 (all traces disabled).

Exception Handling (Critical Priority)
-------------------------------------------------------------------------------

**REQ-008: Automatic Exception Capture**

The package must automatically capture active exceptions for designated
categories without requiring explicit exception passing.

Acceptance Criteria:

* ``errorx`` and ``abortx`` categories automatically capture active exception.
* Exception is included as additional detail in output.
* Works within except blocks using ``sys.exc_info()``.
* ``error`` and ``abort`` categories do not capture exceptions.

**REQ-009: Deep Stack Trace Rendering**

The package must render complete exception information including stack traces
and exception context.

Acceptance Criteria:

* Stack traces show file path, line number, and code snippet for each frame.
* Exception type and message are formatted clearly.
* Stack traces use readable formatting.
* TODO: Exception chaining (``__cause__`` and ``__context__``) is rendered.
* TODO: Exception groups are handled appropriately.

Module Configuration (High Priority)
-------------------------------------------------------------------------------

**REQ-010: Module-Specific Settings**

The package must support module-specific configuration to allow libraries to
register independent diagnostic settings.

Acceptance Criteria:

* Module-specific configuration registration is supported.
* Module configurations inherit from parent package configurations.
* Top-level packages inherit from global configuration.
* Module-specific settings override inherited values.

**REQ-011: Configuration Hierarchy**

The package must support hierarchical configuration inheritance following Python
package structure.

Acceptance Criteria:

* Configuration inherits through package hierarchy.
* Sub-packages inherit from parent packages.
* Top-level packages inherit from global settings.
* Explicit settings override inherited values.

Message Content (High Priority)
-------------------------------------------------------------------------------

**REQ-012: Simple Messages**

The package must support emitting diagnostic messages with simple string
content.

Acceptance Criteria:

* String messages are formatted with category prefix.
* Multi-line strings are formatted with proper indentation.
* Empty strings are handled gracefully.

**REQ-013: Structured Details**

The package must support providing multiple detail arguments for structured
diagnostic information.

Acceptance Criteria:

* Multiple detail arguments are accepted.
* Details are separated by configurable separator.
* Details are formatted with appropriate prefixes and indentation.
* Any object type can be passed as detail.

**REQ-014: Explicit Content Structure**

The package must support structured content objects that explicitly separate
summary from details.

Acceptance Criteria:

* Structured content objects with summary and details are supported.
* Summary and details are formatted consistently.
* Empty details are handled gracefully.

Output Formatting (Medium Priority)
-------------------------------------------------------------------------------

**REQ-015: Customizable Prefixes**

The package must support customizable introduction text for diagnostic output.

Acceptance Criteria:

* Default prefixes show category label with separator.
* Trace level prefixes show level number.
* Prefix templates can be customized via configuration.
* Templates support metadata interpolation (timestamp, module, thread, etc.).

**REQ-016: Optional Rich Formatting**

The package must integrate with Rich library for colorized output when
available.

Acceptance Criteria:

* Rich formatting is enabled automatically when Rich is importable.
* Colors are applied based on category specifications.
* Graceful fallback to plain text when Rich is unavailable.
* Rich formatting can be explicitly disabled via configuration.

Extensibility (Medium Priority)
-------------------------------------------------------------------------------

**REQ-017: Custom Formatting**

The package must support custom formatting logic through extension points.

Acceptance Criteria:

* Custom formatting factories can be provided during configuration.
* Factories receive necessary context for formatting decisions.
* Type hints guide correct factory implementation.

**REQ-018: Custom Output Targets**

The package must support routing output to custom targets beyond stderr.

Acceptance Criteria:

* Custom output factories can be provided during configuration.
* Output can be routed to files, logging, or other targets.
* Default output target is stderr.

Non-Functional Requirements
===============================================================================

Compatibility
-------------------------------------------------------------------------------

* **NFR-001**: Support Python 3.10 and later (including 3.11, 3.12, 3.13, 3.14).
* **NFR-002**: Support both CPython and PyPy implementations.
* **NFR-003**: Rich library integration is optional; all core features work
  without Rich installed.

Type Safety
-------------------------------------------------------------------------------

* **NFR-004**: All public APIs must have complete type annotations.
* **NFR-005**: Type hints must pass Pyright strict mode checking.
* **NFR-006**: IDE autocomplete must work for all common usage patterns.

Reliability
-------------------------------------------------------------------------------

* **NFR-007**: Diagnostic output failures must not crash the application.
* **NFR-008**: Invalid category names must raise clear, actionable exceptions.
* **NFR-009**: Configuration errors must be detected at setup time, not at
  usage time.

Usability
-------------------------------------------------------------------------------

* **NFR-010**: Common usage patterns require ≤3 lines of setup code.
* **NFR-011**: Error messages must clearly identify the problem and suggest
  solutions.
* **NFR-012**: Default configuration must work for 80% of use cases without
  customization.

Constraints and Assumptions
===============================================================================

Technical Constraints
-------------------------------------------------------------------------------

* Must work on Linux, macOS, and Windows operating systems.
* Terminal output width detection may not work in all environments.
* Rich library features require Rich to be installed (optional dependency).

Assumptions
-------------------------------------------------------------------------------

* Users have basic understanding of Python logging and debugging concepts.
* Applications using builtins installation will call installation function
  during startup.
* Library developers will register configurations before application
  installation (when using builtins pattern).
* Terminal output is the primary target (file output via custom output
  targets).
* Exception tracebacks are captured within except blocks (for errorx/abortx).

Out of Scope
===============================================================================

The following features are explicitly excluded from this version:

* **Async support**: No special handling for asyncio or concurrent execution
  contexts (may be added in future versions).
* **Structured logging backends**: No built-in integration with structured
  logging systems like JSON logging or ELK stack (achievable via custom
  printers).
* **Remote logging**: No network transport or remote aggregation features.
* **Log rotation**: No built-in log file rotation or management (use custom
  printers with external log rotation).
* **Performance profiling**: No timing or performance measurement features
  (focused on diagnostic messaging only).
* **Code introspection**: No automatic variable inspection or value printing
  like icecream's ``ic()`` without arguments (may be added in future versions
  if there is demand).
