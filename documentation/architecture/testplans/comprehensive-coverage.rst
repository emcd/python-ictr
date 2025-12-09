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
Test Plan: Comprehensive Coverage for ictr Package
*******************************************************************************

Executive Summary
===============================================================================

This plan outlines the testing strategy to increase coverage from 37% to 100%
for the ictr package. The strategy follows a layered approach: first creating
user-facing examples with doctests to demonstrate common usage patterns, then
implementing systematic pytest coverage for edge cases, error paths, and
internal functionality.

Current State
-------------------------------------------------------------------------------

- **Current coverage**: 37% (503 of 905 lines uncovered)
- **Major coverage gaps**:

  - Dispatchers (24% coverage, 161 uncovered lines)
  - Standard linearizers (11% coverage, 84 uncovered lines)
  - Standard compositors (10% coverage, 81 uncovered lines)
  - Standard introducers (14% coverage, 56 uncovered lines)

- **Well-covered modules**:

  - Core data structures (records, flavors: 100%)
  - Package imports (__/__init__.py, __/nomina.py: 100%)

Testing Philosophy
-------------------------------------------------------------------------------

**Examples-First Approach**:

1. Create practical examples in ``documentation/examples/`` demonstrating
   typical usage patterns
2. Include doctests in examples to validate functionality
3. Examples naturally exercise the "happy path" through the system
4. Focus pytest tests on edge cases and error conditions not covered by examples

**Systematic Coverage**:

- Follow project testing principles (dependency injection, no monkey-patching)
- Respect immutability constraints
- Use in-memory testing where possible (pyfakefs for filesystem operations)
- Capture output for assertions rather than testing against stderr directly

Coverage Analysis by Module
===============================================================================

Phase 1: Documentation Examples (Doctest Coverage)
-------------------------------------------------------------------------------

Create example documents that will naturally exercise core functionality:

**examples/quickstart.rst** (maps to REQ-001, REQ-002, REQ-012)
  Basic usage: install_builtin, simple flavors, basic messages

  - Exercises: Dispatcher.__init__, basic reporter creation, note/error flavors
  - Covers: Standard flavor definitions, basic message flow, printer defaults

**examples/flavors.rst** (maps to REQ-004, REQ-005, REQ-008)
  Standard message categories and aliases

  - Exercises: All standard flavors (note, monition, error, errorx, abort,
    abortx, future, success, advice)
  - Covers: Exception capture for errorx/abortx, flavor specifications
  - Demonstrates: Single-letter aliases

**examples/trace-levels.rst** (maps to REQ-006, REQ-007)
  Hierarchical debugging with trace levels

  - Exercises: Numeric trace levels 0-9, indentation logic, depth filtering
  - Covers: Trace level reporters, introducer formatting for levels
  - Demonstrates: max_trace_level configuration

**examples/exceptions.rst** (maps to REQ-008, REQ-009)
  Exception handling and tracebacks

  - Exercises: errorx/abortx automatic exception capture, traceback rendering
  - Covers: Plain and Rich exception formatting, stack trace generation
  - Demonstrates: Exception within except blocks

**examples/library-integration.rst** (maps to REQ-010, REQ-011)
  Library-friendly module configuration

  - Exercises: register_module, configuration hierarchy, per-module settings
  - Covers: Configuration inheritance, address-based routing
  - Demonstrates: Library/application coexistence

**examples/rich-formatting.rst** (maps to REQ-016)
  Rich library integration

  - Exercises: Rich detection, colorized output, graceful fallback
  - Covers: Rich compositor, Rich console creation, plain fallback
  - Demonstrates: Optional Rich features

**examples/custom-formatting.rst** (maps to REQ-017, REQ-018)
  Extension points and customization

  - Exercises: Custom compositors, custom printers, factory patterns
  - Covers: Compositor protocol, printer protocol, factory injection
  - Demonstrates: File output, custom introducers

Expected Doctest Coverage Impact
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples will naturally cover:

- Dispatcher initialization and basic routing (~50% of dispatcher gaps)
- Standard flavor usage (most of standard/flavors.py)
- Basic compositor flow (introduction + content rendering)
- Common printer usage (stderr default)
- Configuration creation and application
- Happy-path linearizers (plain text, simple exceptions)

Remaining for pytest:

- Error handling paths
- Edge cases (empty messages, None values, malformed configurations)
- Concurrent access patterns
- Rich unavailable scenarios
- Complex exception chaining
- Width constraint handling
- Internal utility functions

Phase 2: Core Component Unit Tests (pytest)
-------------------------------------------------------------------------------

Test Module Numbering Scheme
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on architectural layering and existing numbering:

- **000-099**: Package infrastructure (already exists: test_000_package.py,
  test_010_base.py)
- **100-199**: Core data structures and protocols

  - test_100_records.py (Record, MessageContent)
  - test_110_flavors.py (FlavorSpecification, flavor_specifications_standard)
  - test_120_configuration.py (Configuration dataclasses, hierarchy logic)
  - test_130_exceptions.py (Package exception hierarchy)

- **200-299**: Protocols and interfaces

  - test_200_compositors.py (Compositor protocol, base factory)
  - test_210_printers.py (Printer protocol, base factory)

- **300-399**: Core layer implementations

  - test_300_reporters.py (Reporter message handling)
  - test_310_inspection.py (Stack frame inspection for module addressing)

- **400-499**: Dispatcher layer

  - test_400_dispatchers.py (Dispatcher routing, registration, builtins)

- **500-699**: Standard recipe implementations

  - test_500_standard_core.py (CompositorConfiguration, state management)
  - test_510_standard_flavors.py (Standard flavor definitions, aliases)
  - test_520_standard_introducers.py (Introduction formatting logic)
  - test_530_standard_linearizers.py (Content-to-lines conversion)
  - test_540_standard_compositors.py (Complete composition flow)
  - test_550_standard_printers.py (Stderr and custom output)

- **700-799**: Integration tests

  - test_700_integration_basic.py (End-to-end message flow)
  - test_710_integration_exceptions.py (Exception capture and rendering)
  - test_720_integration_hierarchy.py (Configuration inheritance)
  - test_730_integration_concurrency.py (Thread-safe operation)

Test Module: test_100_records.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/records.py`` (100% covered, but edge
cases needed)

**Coverage goal**: Validate edge cases not covered by examples

Basic functionality tests (000-099)
  Test 000: Record creation with all fields
  Test 010: MessageContent with summary only
  Test 020: MessageContent with summary and details

Record component tests (100-199)
  Test 100: Record with empty content
  Test 110: Record with None flavor
  Test 120: Record timestamp generation
  Test 130: Record immutability validation

MessageContent component tests (200-299)
  Test 200: MessageContent with various detail types (str, int, dict, object)
  Test 210: MessageContent with BaseException as summary
  Test 220: MessageContent with empty details tuple
  Test 230: MessageContent immutability validation

Test Module: test_110_flavors.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/flavors.py`` (100% covered, but needs
validation)

**Coverage goal**: Validate flavor specifications and standard definitions

Basic functionality tests (000-099)
  Test 000: FlavorSpecification basic creation
  Test 010: flavor_specifications_standard keys present

FlavorSpecification component tests (100-199)
  Test 100: FlavorSpecification with all optional fields
  Test 110: FlavorSpecification immutability
  Test 120: FlavorSpecification default values

Standard flavors validation (200-299)
  Test 200: Verify all standard flavors present (note, monition, error,
           errorx, abort, abortx, future, success, advice)
  Test 210: Verify single-letter aliases (n, m, e, a, f, s, v)
  Test 220: Validate exception-capturing flavors (errorx, abortx have enable_exceptions)

Test Module: test_120_configuration.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/configuration.py`` (49% coverage,
61-78 uncovered)

**Uncovered lines**: 61-78 (configuration creation and validation logic)

Basic functionality tests (000-099)
  Test 000: AddressConfiguration with minimal settings
  Test 010: FlavorConfiguration with defaults
  Test 020: Configuration hierarchy basics

AddressConfiguration tests (100-199)
  Test 100: AddressConfiguration with all fields specified
  Test 110: AddressConfiguration with per-flavor overrides
  Test 120: AddressConfiguration inheritance from parent
  Test 130: AddressConfiguration with custom printer_factory
  Test 140: AddressConfiguration with custom compositor_factory
  Test 150: AddressConfiguration immutability

FlavorConfiguration tests (200-299)
  Test 200: FlavorConfiguration with custom compositor_factory
  Test 210: FlavorConfiguration override behavior
  Test 220: FlavorConfiguration immutability

Configuration hierarchy tests (300-399)
  Test 300: Global configuration inheritance
  Test 310: Package configuration inheritance from global
  Test 320: Module configuration inheritance from package
  Test 330: Subpackage configuration inheritance
  Test 340: Override behavior at each hierarchy level

Test Module: test_130_exceptions.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/exceptions.py`` (65% coverage,
39-42, 50, 58, 66, 73, 82, 89 uncovered)

**Uncovered lines**: Exception __init__ methods and __str__ methods

Basic functionality tests (000-099)
  Test 000: Base exception hierarchy (Omniexception, Omnierror)
  Test 010: Exception names follow nomenclature conventions

Exception instantiation tests (100-199)
  Test 100: ArgumentClassInvalidity creation and message
  Test 110: ArgumentValueInvalidity creation and message
  Test 120: ContentMisclassification creation and message
  Test 130: ControlAttributeAbsence creation and message
  Test 140: DispatcherInstallationConflict creation and message
  Test 150: ModuleInspectionFailure creation and message

Exception behavior tests (200-299)
  Test 200: Exceptions inherit from appropriate base classes
  Test 210: Exception messages are properly formatted
  Test 220: Exception repr and str methods

Test Module: test_200_compositors.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/textualizers.py`` (60% coverage,
41, 55, 75-89 uncovered)

**Uncovered lines**: Factory functions and protocol defaults

Basic functionality tests (000-099)
  Test 000: Compositor protocol basic usage
  Test 010: TextualizationControl basic functionality

Factory function tests (100-199)
  Test 100: produce_compositor_factory_default with string introducer
  Test 110: produce_compositor_factory_default with callable introducer
  Test 120: produce_compositor_factory_default with configuration

TextualizationControl tests (200-299)
  Test 200: TextualizationControl with printer providing columns_max
  Test 210: TextualizationControl with printer not providing columns_max
  Test 220: TextualizationControl caching behavior

Printer interaction tests (300-399)
  Test 300: Printer with columns_max attribute
  Test 310: Printer without columns_max attribute
  Test 320: Printer with callable columns_max

Test Module: test_210_printers.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/printers.py`` (51% coverage,
75-76, 85, 92, 107-108, 114-115, 122-132, 146-153 uncovered)

**Uncovered lines**: Factory functions and auxiliary utilities

Basic functionality tests (000-099)
  Test 000: Printer protocol basic usage
  Test 010: produce_printer_factory_default returns callable

Factory function tests (100-199)
  Test 100: produce_printer_factory_default creates printer
  Test 110: produce_printer_factory_default with custom file
  Test 120: produce_printer_factory_default with custom print function

Printer implementation tests (200-299)
  Test 200: StandardPrinter prints to stderr
  Test 210: StandardPrinter with custom file
  Test 220: StandardPrinter columns_max calculation (terminal width detection)
  Test 230: StandardPrinter columns_max with non-terminal file
  Test 240: StandardPrinter columns_max fallback

Terminal width detection tests (300-399)
  Test 300: _calculate_columns_max with terminal file
  Test 310: _calculate_columns_max with non-terminal file
  Test 320: _calculate_columns_max with shutil.get_terminal_size success
  Test 330: _calculate_columns_max with shutil.get_terminal_size failure
  Test 340: _calculate_columns_max fallback to default

Test Module: test_300_reporters.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/reporters.py`` (55% coverage,
48-55 uncovered)

**Uncovered lines**: Reporter __call__ method and message processing

Basic functionality tests (000-099)
  Test 000: Reporter creation with minimal configuration
  Test 010: Reporter active state

Reporter.__call__ tests (100-199)
  Test 100: Reporter processes message with summary only
  Test 110: Reporter processes message with summary and details
  Test 120: Reporter processes message with multiple details
  Test 130: Reporter inactive does not process message
  Test 140: Reporter packages arguments into MessageContent
  Test 150: Reporter creates Record with timestamp
  Test 160: Reporter invokes compositor
  Test 170: Reporter invokes printer

Message flow tests (200-299)
  Test 200: End-to-end message flow through reporter
  Test 210: Reporter with custom compositor
  Test 220: Reporter with custom printer
  Test 230: Reporter captures output for assertion

Test Module: test_310_inspection.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/inspection.py`` (75% coverage,
44-46 uncovered)

**Uncovered lines**: Edge cases in module address discovery

Basic functionality tests (000-099)
  Test 000: discover_address from simple stack
  Test 010: discover_address with nested calls

discover_address tests (100-199)
  Test 100: discover_address identifies calling module
  Test 110: discover_address handles __main__ module
  Test 120: discover_address handles package __init__
  Test 130: discover_address handles subpackage modules
  Test 140: discover_address with missing frame information

Edge case tests (200-299)
  Test 200: discover_address from interactive interpreter
  Test 210: discover_address from exec context
  Test 220: discover_address error handling

Test Module: test_400_dispatchers.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/dispatchers.py`` (24% coverage,
major coverage gaps)

**Uncovered lines**: 97, 184-211, 222-232, 247-253, 383-396, 407-420,
440-447, 463-476, 496-514, 523-538, 547-556, 563-571, 577-581, 586, 593-604,
608-610, 616-625, 631-650, 656-659

Basic functionality tests (000-099)
  Test 000: Dispatcher creation with default configuration
  Test 010: Dispatcher.__getattr__ for flavor name
  Test 020: Dispatcher.__getitem__ for trace level

AddressesConfigurationsRegistry tests (100-199)
  Test 100: Registry initialization with self address
  Test 110: Registry update with new addresses
  Test 120: Registry accretive behavior (no overwrites)
  Test 130: Registry validation of address configurations

Omniflavor tests (200-299)
  Test 200: Omniflavor.Instance matches any flavor
  Test 210: Omniflavor vs specific flavor set behavior

ActiveFlavors registry tests (300-399)
  Test 300: Default active flavors (all standard flavors)
  Test 310: Per-address active flavors
  Test 320: Active flavors hierarchy inheritance
  Test 330: Omniflavor as active flavors value

Dispatcher.__getattr__ tests (400-499)
  Test 400: __getattr__ for standard flavor name
  Test 410: __getattr__ for single-letter alias
  Test 420: __getattr__ creates and caches reporter
  Test 430: __getattr__ returns same reporter on subsequent calls
  Test 440: __getattr__ with invalid flavor name raises exception
  Test 450: __getattr__ respects active flavors configuration
  Test 460: __getattr__ inactive flavor returns inactive reporter

Dispatcher.__getitem__ tests (500-599)
  Test 500: __getitem__ for valid trace level (0-9)
  Test 510: __getitem__ creates and caches reporter
  Test 520: __getitem__ returns same reporter on subsequent calls
  Test 530: __getitem__ with invalid trace level raises exception
  Test 540: __getitem__ respects max_trace_level configuration
  Test 550: __getitem__ above max_trace_level returns inactive reporter

Reporter creation and caching tests (600-699)
  Test 600: Reporter cache behavior for flavors
  Test 610: Reporter cache behavior for trace levels
  Test 620: Reporter configuration from address hierarchy
  Test 630: Reporter compositor from configuration
  Test 640: Reporter printer from configuration

Builtins installation tests (700-799)
  Test 700: install_builtin with default name
  Test 710: install_builtin with custom name
  Test 720: install_builtin conflict detection
  Test 730: install_builtin preserves existing modules configurations
  Test 740: install_builtin thread-safe initialization
  Test 750: install_builtin with custom configuration

Module registration tests (800-899)
  Test 800: register_module with default address discovery
  Test 810: register_module with explicit address
  Test 820: register_module configuration preservation
  Test 830: register_module before install_builtin
  Test 840: register_module after install_builtin
  Test 850: register_module thread-safe registration

Configuration hierarchy tests (900-999)
  Test 900: Global configuration inheritance
  Test 910: Package configuration inheritance
  Test 920: Module configuration inheritance
  Test 930: Subpackage configuration inheritance
  Test 940: Per-flavor configuration override
  Test 950: Compositor factory inheritance
  Test 960: Printer factory inheritance

Test Module: test_500_standard_core.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/standard/core.py`` (77% coverage,
108, 112-120, 194-195, 291-297 uncovered)

**Uncovered lines**: CompositorConfiguration edge cases, state management

Basic functionality tests (000-099)
  Test 000: CompositorConfiguration with defaults
  Test 010: CompositorState creation

CompositorConfiguration tests (100-199)
  Test 100: CompositorConfiguration with all fields specified
  Test 110: CompositorConfiguration with custom details_separator
  Test 120: CompositorConfiguration with custom prefixes
  Test 130: CompositorConfiguration with ExceptionsConfiguration
  Test 140: CompositorConfiguration immutability

ExceptionsConfiguration tests (200-299)
  Test 200: ExceptionsConfiguration with enable_stacktraces
  Test 210: ExceptionsConfiguration.discover() finds active exception
  Test 220: ExceptionsConfiguration.discover() returns None when no exception
  Test 230: ExceptionsConfiguration.interpolate() formats exception message

CompositorState tests (300-399)
  Test 300: CompositorState.from_configuration with Rich available
  Test 310: CompositorState.from_configuration with Rich unavailable
  Test 320: CompositorState.from_configuration with columns_max
  Test 330: CompositorState.from_configuration without columns_max

Rich integration tests (400-499)
  Test 400: Rich console creation
  Test 410: Rich console with custom columns_max
  Test 420: Rich fallback when import fails
  Test 430: produce_rich_console helper function

Test Module: test_510_standard_flavors.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/standard/flavors.py`` (18% coverage,
40-65, 71 uncovered)

**Uncovered lines**: Flavor production functions

Basic functionality tests (000-099)
  Test 000: produce_flavors_standard returns dictionary
  Test 010: Standard flavors include all required categories

produce_flavors_standard tests (100-199)
  Test 100: Produced flavors include note, monition, error, abort, future,
           success, advice
  Test 110: Produced flavors include errorx, abortx with exception capture
  Test 120: Produced flavors have correct specifications
  Test 130: Produced flavors with Rich integration
  Test 140: Produced flavors without Rich (plain fallback)

Flavor specification tests (200-299)
  Test 200: Each standard flavor has label
  Test 210: Exception-capturing flavors (errorx, abortx) configured correctly
  Test 220: Flavor emoji present when Rich available
  Test 230: Flavor colors present when Rich available
  Test 240: Plain fallback formatting

Alias tests (300-399)
  Test 300: Single-letter aliases map correctly
  Test 310: Alias 'n' maps to 'note'
  Test 320: Alias 'e' maps to 'error'
  Test 330: Alias 'a' maps to 'abort'
  Test 340: All aliases functional

Test Module: test_520_standard_introducers.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/standard/introducers.py`` (14% coverage,
43-50, 56-72, 79-95, 106-119, 127-138 uncovered)

**Uncovered lines**: All introducer functions

Basic functionality tests (000-099)
  Test 000: produce_introducer_for_flavor returns callable
  Test 010: produce_introducer_for_tracelevel returns callable

produce_introducer_for_flavor tests (100-199)
  Test 100: Introducer with flavor specification (label, emoji, color)
  Test 110: Introducer without flavor specification
  Test 120: Introducer with Rich formatting enabled
  Test 130: Introducer with Rich formatting disabled
  Test 140: Introducer with custom label
  Test 150: Introducer with emoji only
  Test 160: Introducer with color only

produce_introducer_for_tracelevel tests (200-299)
  Test 200: Introducer for trace level 0 (no indentation)
  Test 210: Introducer for trace level 5 (10 spaces indentation)
  Test 220: Introducer for trace level 9 (18 spaces indentation)
  Test 230: Introducer with Rich formatting enabled
  Test 240: Introducer with Rich formatting disabled
  Test 250: Introducer indentation calculation

Format tests (300-399)
  Test 300: Introduction string format for flavors
  Test 310: Introduction string format for trace levels
  Test 320: Introduction with columns_max constraint
  Test 330: Introduction string length validation

Test Module: test_530_standard_linearizers.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/standard/linearizers.py`` (11% coverage,
major gaps)

**Uncovered lines**: 33-41, 50-59, 68-71, 79-82, 90-92, 100-104, 112-116,
124-157, 165-177, 185-196, 208-221

Basic functionality tests (000-099)
  Test 000: linearize_omni dispatches to correct linearizer
  Test 010: linearize_object_plain basic usage
  Test 020: linearize_exception_plain basic usage

linearize_object_plain tests (100-199)
  Test 100: Simple object (int, str, bool)
  Test 110: Complex object (dict, list)
  Test 120: Custom object with __repr__
  Test 130: Object with columns_max constraint
  Test 140: Object with absent columns_max
  Test 150: Multi-line object representation

linearize_object_rich tests (200-299)
  Test 200: Simple object with Rich formatting
  Test 210: Complex object with Rich formatting
  Test 220: Rich pretty print with colors
  Test 230: Rich with columns_max constraint
  Test 240: Rich fallback to plain if unavailable

linearize_exception_plain tests (300-399)
  Test 300: Basic exception with message
  Test 310: Exception with stack trace enabled
  Test 320: Exception with stack trace disabled
  Test 330: Exception with columns_max constraint
  Test 340: Exception message interpolation

linearize_exception_rich tests (400-499)
  Test 400: Exception with Rich Traceback formatting
  Test 410: Exception with Rich colors and styling
  Test 420: Exception with stack trace enabled
  Test 430: Exception with stack trace disabled
  Test 440: Rich exception with columns_max constraint

linearize_stacktrace_plain tests (500-599)
  Test 500: Stack trace with multiple frames
  Test 510: Stack trace with file path, line number, code snippet
  Test 520: Stack trace with columns_max wrapping
  Test 530: Stack trace formatting consistency

linearize_stacktrace_rich tests (600-699)
  Test 600: Rich stack trace with syntax highlighting
  Test 610: Rich stack trace with colors
  Test 620: Rich stack trace with columns_max
  Test 630: Rich stack trace frame formatting

linearize_string tests (700-799)
  Test 700: Single-line string
  Test 710: Multi-line string
  Test 720: Empty string
  Test 730: String with columns_max wrapping
  Test 740: String split into lines

Exception chaining tests (800-899)
  Test 800: Exception with __cause__ (TODO in code)
  Test 810: Exception with __context__ (TODO in code)
  Test 820: Exception groups (TODO in code)
  Test 830: Nested exception chaining

Test Module: test_540_standard_compositors.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/standard/compositors.py`` (10% coverage,
major gaps)

**Uncovered lines**: 50-70, 74-97, 103-107, 113-149, 155-167, 176-182

Basic functionality tests (000-099)
  Test 000: Compositor with default configuration
  Test 010: Compositor.__call__ basic flow

Compositor.__call__ tests (100-199)
  Test 100: Compose MessageContent with summary only
  Test 110: Compose MessageContent with summary and details
  Test 120: Compose MessageContent with multiple details
  Test 130: Compose with string introducer
  Test 140: Compose with callable introducer
  Test 150: Compose with exception detail
  Test 160: Compose with ContentMisclassification for invalid content type

_render_summary tests (200-299)
  Test 200: Render summary with introduction prefix
  Test 210: Render summary with multi-line content
  Test 220: Render summary with columns_max constraint
  Test 230: Render summary with line prefix for continuation
  Test 240: Render BaseException summary triggers exception discovery
  Test 250: Render non-exception summary

_render_detail tests (300-399)
  Test 300: Render detail with initial prefix
  Test 310: Render detail with subsequent prefix
  Test 320: Render detail with multi-line content
  Test 330: Render detail with columns_max constraint
  Test 340: Render detail line prefix for continuation
  Test 350: Render exception detail
  Test 360: Render object detail

_render_lines tests (400-499)
  Test 400: Render lines with initial prefix
  Test 410: Render lines with subsequent prefix
  Test 420: Render lines with line prefix
  Test 430: Render empty lines
  Test 440: Render single line
  Test 450: Render multiple lines with proper indentation

Integration tests (500-599)
  Test 500: Complete message flow with all components
  Test 510: Introduction + summary + multiple details
  Test 520: Exception discovery and rendering
  Test 530: Details separator application
  Test 540: Complex nested details

Test Module: test_550_standard_printers.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Module under test**: ``sources/ictr/standard/printers.py`` (37% coverage,
40-43, 48-55 uncovered)

**Uncovered lines**: Printer factory and implementation

Basic functionality tests (000-099)
  Test 000: produce_printer_factory returns callable
  Test 010: Factory creates printer

produce_printer_factory tests (100-199)
  Test 100: Factory with default arguments
  Test 110: Factory with custom print function
  Test 120: Factory creates printer instance
  Test 130: Printer from factory has correct attributes

Printer implementation tests (200-299)
  Test 200: Printer prints to stderr
  Test 210: Printer with custom print function
  Test 220: Printer output capture for assertion
  Test 230: Printer columns_max from StandardPrinter

Integration tests (300-399)
  Test 300: Printer used in complete message flow
  Test 310: Printer with captured output
  Test 320: Printer with custom file object

Phase 3: Integration Tests
-------------------------------------------------------------------------------

Test Module: test_700_integration_basic.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

End-to-end message flow tests
  Test 000: Simple message from install to output

  Test 100: Message with flavor selection

  Test 200: Message with trace level

  Test 300: Message with multiple details

  Test 400: Message flow through all layers (dispatcher, reporter, compositor, printer)

Test Module: test_710_integration_exceptions.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exception capture and rendering tests
  Test 000: errorx captures exception in except block
  Test 100: abortx captures exception in except block
  Test 200: Exception with full stack trace
  Test 300: Exception rendering in plain mode
  Test 400: Exception rendering in Rich mode
  Test 500: Exception without enable_exceptions (error, abort)

Test Module: test_720_integration_hierarchy.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration hierarchy tests
  Test 000: Global configuration applies to all modules
  Test 100: Package configuration inherits from global
  Test 200: Module configuration inherits from package
  Test 300: Subpackage configuration chain
  Test 400: Per-flavor overrides at each level
  Test 500: Compositor factory inheritance
  Test 600: Printer factory inheritance
  Test 700: Active flavors inheritance

Test Module: test_730_integration_concurrency.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thread-safe operation tests
  Test 000: Concurrent message emission from multiple threads
  Test 100: Concurrent reporter creation
  Test 200: Concurrent module registration
  Test 300: install_builtin mutex protection
  Test 400: register_module mutex protection

Implementation Notes
===============================================================================

Dependencies Requiring Injection
-------------------------------------------------------------------------------

**Time and timestamp mocking**:
  For deterministic tests of Record timestamp generation, inject time function
  via configuration or test helpers

**Terminal width detection**:
  For testing columns_max calculation, inject mock for shutil.get_terminal_size
  or use printers with explicit columns_max

**Rich library availability**:
  Test both Rich-available and Rich-unavailable scenarios by controlling import
  path or using test-specific compositor configurations

**Stack frame inspection**:
  For testing discover_address, create controlled call stacks via test helper
  functions rather than attempting to mock inspect.currentframe

Output Capture for Assertions
-------------------------------------------------------------------------------

**Preferred pattern**: Use custom printer with io.StringIO capture::

    from io import StringIO

    def test_message_output():
        capture = StringIO()
        printer_factory = lambda ctrl: lambda text: capture.write(text)
        dispatcher = Dispatcher(
            addresses_configurations = {...},
            printer_factory = printer_factory
        )
        dispatcher.note('test message')
        assert 'test message' in capture.getvalue()

**Avoid**: Direct stderr capture or subprocess execution for output testing

Filesystem Operations
-------------------------------------------------------------------------------

Not extensively required for this package. Configuration loading from files
would use pyfakefs if implemented.

Test Data Organization (tests/data/)
-------------------------------------------------------------------------------

**tests/data/snapshots/**: Expected output snapshots for regression testing

- plain_flavor_outputs/ (expected plain text for each flavor)
- rich_flavor_outputs/ (expected Rich formatted output)
- exception_tracebacks/ (expected exception rendering)
- trace_level_indentation/ (expected indentation patterns)

**tests/data/mocks/**: Mock data for structured test input

- sample_configurations.py (various configuration scenarios)
- sample_exceptions.py (exception instances for testing)

Third-Party Testing Patterns to Research
-------------------------------------------------------------------------------

**Rich library testing**:

  - How Rich tests console output capture
  - Mock console patterns for testing Rich rendering
  - Snapshot testing for Rich formatted output

**Threading patterns**:

  - Thread-safe initialization testing patterns
  - Mutex-protected operations validation
  - Race condition detection strategies

Anti-Patterns to Avoid
-------------------------------------------------------------------------------

**NEVER test against real external sites**: Not applicable (no network I/O)

**NEVER monkey-patch internal code**: Respect immutability constraints; use
dependency injection

**NEVER use excessive mocking**: Test real object interactions; mock only at
system boundaries

**NEVER use bare except**: Catch specific exceptions in tests

**NEVER test implementation details**: Test behavior via public API

Areas Requiring Immutability Constraint Considerations
-------------------------------------------------------------------------------

**Dataclass immutability**: All configuration objects use frozen dataclasses

- Cannot monkey-patch attributes for testing
- Must use constructor injection for test variations
- Create new instances rather than mutating existing ones

**Accretive dictionaries**: Registries cannot be modified after initial update

- Cannot remove entries for cleanup
- Tests must use fresh dispatcher instances
- Integration tests may need test-specific address namespacing

**Reporter caching**: Dispatchers cache reporter instances

- Cannot replace reporters after creation
- Tests must create new dispatchers for configuration variations
- Cache behavior itself needs testing

**Mutex-protected initialization**: Global state initialization uses locks

- Cannot easily reset global state between tests
- builtins installation creates persistent side effects
- Tests using install_builtin should use unique builtin names

Private Functions/Methods Not Testable via Public API
-------------------------------------------------------------------------------

**sources/ictr/dispatchers.py**:

  - ``_provide_active_flavors_default()``: Called during initialization,
    testable via dispatcher creation
  - Internal registry initialization: Testable via dispatcher behavior

**sources/ictr/standard/compositors.py**:

  - ``_render_detail()``: Private but exercised via Compositor.__call__
  - ``_render_summary()``: Private but exercised via Compositor.__call__
  - ``_render_lines()``: Private but exercised via _render_detail and
    _render_summary

**sources/ictr/printers.py**:

  - ``_calculate_columns_max()``: Private but exercised via StandardPrinter.columns_max
  - Terminal width detection: Testable via StandardPrinter with various file types

**Assessment**: All private functions are exercised via public API. No
architectural changes needed.

Success Metrics
===============================================================================

Target Coverage
-------------------------------------------------------------------------------

- **Line coverage**: 100% (905 lines)
- **Branch coverage**: 95%+ (account for defensive branches that may be
  untestable)

Specific Gaps to Close
-------------------------------------------------------------------------------

**High Priority** (most uncovered lines):

1. sources/ictr/dispatchers.py: 161 uncovered → 0 uncovered
2. sources/ictr/standard/linearizers.py: 84 uncovered → 0 uncovered
3. sources/ictr/standard/compositors.py: 81 uncovered → 0 uncovered
4. sources/ictr/standard/introducers.py: 56 uncovered → 0 uncovered

**Medium Priority**:

5. sources/ictr/printers.py: 23 uncovered → 0-5 uncovered (terminal width
   detection edge cases)
6. sources/ictr/standard/core.py: 17 uncovered → 0 uncovered
7. sources/ictr/standard/flavors.py: 19 uncovered → 0 uncovered

**Low Priority** (already high coverage, edge case validation):

8. sources/ictr/__/validators.py: 6 uncovered → 0 uncovered
9. sources/ictr/configuration.py: 12 uncovered → 0 uncovered
10. sources/ictr/exceptions.py: 9 uncovered → 0 uncovered

Validation Criteria
-------------------------------------------------------------------------------

- All PRD requirements (REQ-001 through REQ-018) have test coverage
- All standard flavors exercised in examples and tests
- Exception capture functionality validated in multiple scenarios
- Configuration hierarchy inheritance tested at all levels
- Thread-safe operations validated via concurrency tests
- Examples run successfully as doctests
- Integration tests demonstrate end-to-end functionality

Estimated Complexity and Implementation Priority
===============================================================================

Phase 1: Examples with Doctests (1-2 weeks)
-------------------------------------------------------------------------------

**Priority**: HIGHEST - Provides user documentation and baseline coverage

**Estimated effort**: 7 example documents with embedded doctests

**Deliverables**:

- examples/quickstart.rst
- examples/flavors.rst
- examples/trace-levels.rst
- examples/exceptions.rst
- examples/library-integration.rst
- examples/rich-formatting.rst
- examples/custom-formatting.rst

**Expected coverage increase**: 37% → 60-65%

Phase 2: Core Component Unit Tests (2-3 weeks)
-------------------------------------------------------------------------------

**Priority**: HIGH - Closes coverage gaps systematically

**Estimated effort**: 15 test modules covering layers 100-699

**Deliverables**: All test_1XX through test_6XX modules

**Expected coverage increase**: 60-65% → 90-95%

Phase 3: Integration Tests (1 week)
-------------------------------------------------------------------------------

**Priority**: MEDIUM - Validates system behavior

**Estimated effort**: 4 integration test modules (test_7XX)

**Deliverables**: All test_7XX modules

**Expected coverage increase**: 90-95% → 95-100%

Phase 4: Edge Case Refinement (1 week)
-------------------------------------------------------------------------------

**Priority**: LOW - Achieves final coverage goals

**Estimated effort**: Identified gap closure and edge case validation

**Expected coverage increase**: 95-100% → 100%

Total Estimated Timeline: 5-7 weeks

Potential Challenges and Special Considerations
===============================================================================

Challenges
-------------------------------------------------------------------------------

**Rich library optional dependency**:

  - Must test both Rich-available and Rich-unavailable scenarios
  - Rich rendering is non-deterministic (terminal width, color support)
  - Snapshot testing may be fragile for Rich output

**Terminal width detection**:

  - Platform-specific behavior
  - Not all file objects support terminal queries
  - Fallback logic has multiple branches

**Exception traceback rendering**:

  - Python version differences in traceback format
  - Rich Traceback rendering may differ across Rich versions
  - Exception chaining and groups (TODO in code) not fully implemented

**Thread-safe initialization**:

  - Race conditions difficult to reproduce reliably
  - Mutex testing requires careful orchestration
  - Global state cleanup between tests challenging

**Immutability constraints**:

  - Cannot monkey-patch for testing
  - Requires architectural discipline in test design
  - May need more verbose test setup code

Special Considerations
-------------------------------------------------------------------------------

**Doctest vs pytest trade-offs**:

  - Doctests validate examples and documentation
  - Doctests less suitable for complex assertions
  - Pytest provides better error reporting and debugging
  - Use both complementarily

**Output capture patterns**:

  - Prefer io.StringIO over sys.stderr capture
  - Custom printer factories enable clean assertions
  - Avoid subprocess execution for output testing

**Example maintenance**:

  - Keep examples in sync with code changes
  - Run doctests in CI to catch regressions
  - Update examples when API evolves

**Test data organization**:

  - Use snapshots for regression testing
  - Store expected outputs for comparison
  - Version snapshot data with code changes

**Coverage tooling**:

  - Use coverage.py with branch coverage enabled
  - Generate HTML coverage reports for visual analysis
  - Track coverage trends over time

Pushback Recommendations
===============================================================================

Based on coverage analysis, the architecture is generally testable via public
API with dependency injection. However, some improvements could enhance
testability:

Minor Enhancements (Optional)
-------------------------------------------------------------------------------

**Expose time injection for Record timestamp**:

  Currently timestamp is generated via direct time.time() call. Consider adding
  optional time_factory parameter to configuration for deterministic testing.

**Provide terminal width injection point**:

  The _calculate_columns_max function directly calls shutil.get_terminal_size.
  Consider allowing terminal_size_factory in printer configuration.

**Rich import fallback testing**:

  Current Rich detection happens at import time. Consider lazy import pattern
  or injection point to facilitate testing both scenarios.

Architectural Strengths
-------------------------------------------------------------------------------

**Excellent separation of concerns**: Layered architecture enables testing each
layer independently

**Immutability benefits**: Thread-safe by design, no surprising mutations

**Protocol-based design**: Easy to create test doubles for protocols

**Factory pattern**: Enables dependency injection without tight coupling

**Configuration hierarchy**: Well-designed inheritance model testable at each
level

No Blocking Issues Identified
-------------------------------------------------------------------------------

All functionality is testable via public API with appropriate test design. The
immutability constraints are features, not bugs, and tests can work within them.
