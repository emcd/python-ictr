# ICTR v2 Migration Plan

This document tracks the migration of code and concepts from `python-icecream-truck` (v1) to `python-ictr` (v2).

**Last Updated**: 2025-11-02

## Migration Status Overview

### ✅ Already Migrated (Partially Adapted)

These files have been copied from ictruck to ictr and partially adapted for v2:

1. **`sources/ictr/configuration.py`** (from `ictruck/configuration.py`)
   - Status: ✅ Mostly complete, needs Sundae integration
   - Completed:
     - Renamed `VehicleConfiguration` → `DispatcherConfiguration`
     - Moved `Flavor` type to `flavors.py` (broke circular dependency)
     - Updated for v2 architecture
   - Remaining:
     - Add Sundae fields to `FlavorConfiguration` (color, emoji, label, stack)
     - Update default values after Sundae migration

2. **`sources/ictr/dispatchers.py`** (renamed from `vehicles.py`)
   - Status: ✅ Complete, needs testing
   - Completed:
     - ✅ Renamed from `vehicles.py`
     - ✅ Removed all `_icecream.IceCreamDebugger` references
     - ✅ Updated `Dispatcher` to create and cache `Reporter` instances
     - ✅ Updated printer factory integration for v2 Record-based pipeline
     - ✅ Removed `_calculate_ic_initargs`
     - ✅ Replaced `truck`/`Truck` references with `dispatcher`/`Dispatcher`
   - Note: `.inspect()` method **DEFERRED** - see decision log below

3. **`sources/ictr/exceptions.py`** (from `ictruck/exceptions.py`)
   - Status: ✅ Complete
   - Ported exceptions:
     - `ArgumentClassInvalidity` (TypeError)
     - `AttributeNondisplacement` (AttributeError)
     - `FlavorInavailability` (ValueError)
     - `ModuleInferenceFailure` (RuntimeError)
   - `Omniexception` base class updated to use `frigid.immut.exceptions.Omniexception`

4. **`sources/ictr/flavors.py`** (NEW - factored from configuration)
   - Status: ✅ Complete
   - Content:
     - `Flavor` type alias (moved from `configuration.py`)
     - Broke circular dependency between `configuration` and `printers`

5. **`sources/ictr/__/nomina.py`** (from `ictruck/__/nomina.py`)
   - Status: ✅ Complete
   - No changes needed

6. **`sources/ictr/__/imports.py`** (from `ictruck/__/imports.py`)
   - Status: ✅ Complete
   - Updated with necessary imports for v2

### 🔄 Needs Migration (Direct or Adapted)

#### Core Implementation Files

7. **`sources/ictr/printers.py`** (from `ictruck/printers.py`)
   - Status: ✅ Complete
   - Completed:
     - ✅ Updated `Printer` protocol with new signature: `(record, text=None)`
     - ✅ Added `provide_textualizer_control()` method to protocol
     - ✅ Created `SimplePrinter` class (replaces `_simple_print` function)
     - ✅ Created `TextualizerControl` class (replaces `FormatterControl`)
     - ✅ Kept decolorization logic (`_remove_ansi_c1_sequences`)
     - ✅ Kept colorama integration for Windows
   - Key insight: Printer can return `None` from `provide_textualizer_control()` to indicate it doesn't support text (e.g., for structured logging, database, JSON)

8. **`sources/ictr/__/miscellany.py`** (from `ictruck/__/miscellany.py`)
   - Status: ✅ Complete
   - Utility functions ported as needed

9. **`sources/ictr/__/validators.py`** (from `ictruck/__/validators.py`)
   - Status: ✅ Complete
   - Argument validation utilities ported

#### New Files for v2

10. **`sources/ictr/records.py`** (NEW)
    - Status: ✅ Complete
    - Completed:
      - ✅ `Record` dataclass (main record structure)
      - ✅ `RecordContent` base class
      - ✅ `MessageContent` dataclass (summary + details)
      - ✅ `MessageSummary` and `MessageDetail` type aliases
    - Note: InspectionContent deferred (see decision log)

10. **`sources/ictr/inspection.py`** (NEW)
    - Priority: HIGH
    - Content needed:
      - Integration with `executing` library
      - `inspect_call(*args, _frame=...)` function
      - Literal detection logic (ast.Constant, ast.JoinedStr)
      - Variable/expression name extraction
      - Frame depth handling for wrapper functions
    - Reference:
      - `.auxiliary/notes/original/executing.md`
      - `python-icecream-truck/.auxiliary/scribbles/inspect_prototype.py`

11. **`sources/ictr/textualizers.py`** (NEW, replaces formatters)
    - Status: 🔄 In progress
    - Priority: **NEXT - HIGH**
    - Completed:
      - ✅ Renamed from "formatters" to "textualizers"
      - ✅ `Textualizer` protocol defined
      - ✅ `TextualizerDefault` stub created
      - ✅ `PrefixEmitter` type aliases defined
    - Remaining:
      - ⏸️ Implement `TextualizerDefault.__call__()`
      - ⏸️ Implement prefix rendering (will use data from Sundae)
      - ⏸️ Implement body rendering
      - ⏸️ Implement frame composition (multiline, wrapping)
    - Key design decision: **Merge prefix generation into textualizer** (not separate)
    - References:
      - `ictruck/recipes/sundae.py` for prefix templates and interpolation
      - `.auxiliary/notes/original/ictr-v2-design.md` for formatting specs

12. **`sources/ictr/reporters.py`** (NEW, separate module)
    - Status: ✅ Complete
    - Completed:
      - ✅ `Reporter` class with v2 API
      - ✅ `__call__(summary, *details)` method (normal mode)
      - ✅ Pre-resolved configuration (active flag, flavor, textualizer, printer)
      - ✅ Conditional textualization based on `provide_textualizer_control()`
      - ✅ Clean integration with Record-based pipeline
    - Note: `.inspect(*variables)` method **DEFERRED** (see decision log)
    - Note: Exception autocapture for errorx/abortx **TODO**

#### Reference/Recipe Files (Adapt for Formatters)

13. **Migrate Sundae Recipe → `sources/ictr/standard/` subpackage**
    - Status: 🔄 Not started
    - Priority: **NEXT - HIGH**
    - Plan: Create `standard` subpackage with Sundae functionality
    - Content to migrate:
      - Pre-defined flavors (note, monition, error, errorx, abort, abortx, future, success)
      - Flavor specifications (color, emoji, label, stack)
      - Prefix template system with interpolants (flavor, timestamp, module, PID, thread)
      - Trace level color gradients
      - `Auxiliaries` pattern for dependency injection
      - `PrefixFormatControl` (integrate with TextualizerControl)
    - Structure:
      ```
      sources/ictr/standard/
        __init__.py
        flavors.py      # Pre-defined flavor specs
        textualizers.py # Sundae textualizer implementation
      ```
    - Integration points:
      - `FlavorConfiguration` gets sundae fields (color, emoji, label, stack)
      - Default textualizer uses Sundae prefix rendering
      - Can register standard flavors at module load
    - Reference: `ictruck/recipes/sundae.py`

14. **Review `ictruck/recipes/rich.py`**
    - Priority: LOW (mostly subset of Sundae)
    - Analysis: Rich recipe is mostly redundant with Sundae
    - Unique aspects to consider:
      - `Modes.Formatter` vs `Modes.Printer` - controls when Rich processes text
      - `ConsoleTextIoInvalidity` exception for stream validation
      - `produce_console_printer()` - uses console.print directly (has ANSI reprocessing caveats)
    - **Recommendation**: Focus on Sundae recipe. The Modes concept could be valuable as a configuration option but doesn't need a separate recipe
    - Everything else (rich.pretty_repr, console formatting, etc.) is already in Sundae

15. **Review `ictruck/recipes/logging.py`**
    - Priority: LOW
    - Purpose: Python logging integration patterns
    - May be useful for alternative printer implementations

#### Prototypes to Integrate

16. **Integrate inspection prototype**
    - Priority: HIGH
    - Source: `python-icecream-truck/.auxiliary/scribbles/inspect_prototype.py`
    - Destination: `sources/ictr/inspection.py`
    - Testing: Port tests from `test_driver.py` to main test suite

### 🚫 Not Migrating

These are v1-specific and replaced by v2 design:

- Direct icecream library dependency (replaced by executing)
- `IceCreamDebugger` instances (replaced by Reporter)
- Old two-stage formatting approach (replaced by Record-based pipeline)

## Current Status Summary

### ✅ Phase 1: Core Infrastructure - **COMPLETE**
- ✅ Configuration updated for v2
- ✅ Records module with Record and MessageContent
- ✅ Printers updated with v2 signatures
- ✅ Utilities migrated (__/miscellany, __/validators)
- ✅ Flavors module factored out

### ✅ Phase 2: Reporter & Dispatcher - **COMPLETE**
- ✅ Reporter class implemented
- ✅ Dispatcher updated to vend Reporters
- ✅ Record-based pipeline working
- ✅ Conditional textualization based on printer capability

### 🔄 Phase 3: Textualization - **IN PROGRESS**
Current priorities:
1. **Implement TextualizerDefault** (HIGH - NEXT)
   - Prefix rendering
   - Body rendering
   - Frame composition
2. **Migrate Sundae to `standard/` subpackage** (HIGH - NEXT)
   - Extract flavor definitions
   - Implement prefix templates with interpolation
   - Set up standard flavors registry

### ⏸️ Phase 4: Polish - **DEFERRED**
- Add exception/traceback formatting
- Port tests from prototypes
- Update README and documentation

## Key Design Differences to Remember

When adapting code, keep these v2 changes in mind:

1. **No icecream dependency**: Use `executing` directly
2. **Record-based pipeline**: Everything goes through Record objects
3. **Two content types**: MessageContent vs InspectionContent
4. **Reporter API**: `__call__(summary, *details)` and `.inspect(*variables)`
5. **Formatters operate on Records**: Signature is `Callable[[Record], str]`
6. **Printers receive Records**: Signature is `Callable[[str, Record], None]`
7. **Summary flexibility**: First arg in normal mode can be str | Exception
8. **No kwargs**: Both modes only accept positional args (for now)
9. **Exception autocapture**: Only for errorx/abortx when exception active
10. **Immutability**: Use `frigid.DataclassObject` for all data structures
11. **Vehicles → Dispatchers**: The main coordinating class is now called `Dispatcher` (vehicles.py will be renamed to dispatchers.py)
12. **Sundae by default**: Flavor fields (color, emoji, label, stack) are baseline, not optional recipe

## Files That Need Review

Before starting implementation, review these in detail:

- `python-icecream-truck/sources/ictruck/recipes/sundae.py` - Flavor configs
- `python-icecream-truck/.auxiliary/scribbles/inspect_prototype.py` - Working inspection
- `.auxiliary/notes/original/ictr-v2-design.md` - Complete v2 spec
- `.auxiliary/notes/original/record-design.md` - Record structure details
- `.auxiliary/notes/original/executing.md` - Inspection implementation guide

## Notes

- The current state suggests you've started by copying the base infrastructure (configuration, vehicles, exceptions, etc.)
- The next logical step is to add the new v2-specific modules (records, inspection, formatters)
- Then update the existing modules to remove icecream and use the new infrastructure
- Finally, integrate the inspection prototype and adapt the recipes for formatting

## Decision Log

### Decision 1: Vehicles → Dispatchers Rename
**Date**: 2025-11-01
**Decision**: Rename `vehicles.py` to `dispatchers.py`
**Rationale**: Better reflects the coordinator/dispatch role of the main class

### Decision 2: Flatten Sundae into Core
**Date**: 2025-11-01
**Decision**: Make Sundae features (color, emoji, label, stack) baseline FlavorConfiguration fields
**Rationale**: v2 design premise is "Sundae by default" - these should be core features, not optional

### Decision 3: Defer `.inspect()` Method Implementation
**Date**: 2025-11-01
**Decision**: Postpone implementation of `Reporter.inspect()` and `inspection.py` module
**Dependencies Avoided**: `asttokens` (not in stdlib, thought to be conflated with `ast` + `token`)
**Rationale**:
- F-string `{name=}` syntax provides equivalent functionality with zero dependencies
- Testing revealed both approaches show identical information (source code as-is)
- No significant value proposition for the added complexity and dependencies
- Can revisit later if `executing`/`asttokens` offer additional metadata worth having

**Comparison Analysis**: See `.auxiliary/scribbles/test_executing_direct.py`

**What Both Approaches Show**:
- Source expressions exactly as written: `server.config.host`
- No automatic qualification: shows `Path` not `pathlib.Path`
- Method calls with parens: `obj.method()`
- Complex chains: `registry['servers'][0].config.host`
- Arithmetic: `x + y`

**Only Difference**: Separator character (`=` vs `:`) and automatic extraction vs manual `{=}`

**Future Consideration**: If implementing later, investigate what additional metadata `executing`/`asttokens` can provide to justify the dependencies.

### Decision 4: Merge Prefix Generation into Textualizer
**Date**: 2025-11-02
**Decision**: Prefix rendering is part of textualizer, not a separate PrefixEmitter
**Rationale**:
- In v1, separation was forced by IceCreamDebugger's structure (external constraint)
- In v2, textualizer owns the entire message frame (prefix + body)
- Better cohesion: prefix and body interact (wrapping, alignment, multiline)
- Simpler architecture: one component, clear responsibility
- More flexible: holistic formatting decisions

**Implementation**:
- `Textualizer._render_prefix()` - internal method for prefix
- `FlavorConfiguration` stores prefix **data** (template, colors, etc.), not callables
- Sundae prefix logic becomes part of standard textualizer

### Decision 5: Printer Opt-Out of Textualization
**Date**: 2025-11-02
**Decision**: Printer can return `None` from `provide_textualizer_control()` to skip textualization
**Rationale**:
- Supports structured logging (JSON, database, metrics) efficiently
- Avoids expensive formatting when not needed
- Per-flavor control via configuration
- Clean contract: printer receives both `text` and `record`, uses what it needs

**Implementation**:
- `Printer.provide_textualizer_control()` returns `Optional[TextualizerControl]`
- `None` = skip textualization (structured output)
- `TextualizerControl(...)` = enable textualization (text output)
- Reporter checks return value before calling textualizer

## Questions to Resolve

Before implementing, clarify:

1. ✅ **RESOLVED**: Should `Reporter` be in separate `reporters.py` or merged?
   - **Decision pending**: Will decide during implementation. Likely merge into dispatchers.py for cohesion.

2. Should formatters be one file or split by type?

3. ✅ **RESOLVED**: Do we want to preserve recipe structure or flatten into core?
   - **Decision**: Flatten Sundae into core as baseline. Sundae fields (color, emoji, label, stack) will be standard FlavorConfiguration fields.

4. ✅ **RESOLVED**: Implement `.inspect()` method with executing?
   - **Decision**: Defer for now. F-strings provide equivalent value without dependencies.

5. Should tests be migrated incrementally or after core completion?

## Rich vs Sundae Recipe Analysis

After detailed comparison of both recipes, **Sundae is the comprehensive solution** and Rich is mostly a subset:

### What Sundae Provides
- Complete prefix template system with interpolants (flavor, module_qname, timestamp, process_id, thread_id, thread_name)
- FlavorSpecification with color, emoji, label, and stack fields
- Pre-defined flavors (note, monition, error, errorx, abort, abortx, future, success) with aliases
- Trace level color gradients (grey85 → grey50)
- Auxiliaries pattern for dependency injection (exc_info_discoverer, pid_discoverer, thread_discoverer, time_formatter)
- PrefixFormatControl for fine-grained customization
- Both formatters AND prefix emitters in one recipe
- Stack trace auto-capture for errorx/abortx flavors

### What Rich Provides (Unique)
- `Modes.Formatter` vs `Modes.Printer` - timing control for Rich processing
  - Formatter mode: Rich processes during format stage (safer)
  - Printer mode: Rich processes during print stage (riskier, may reprocess ANSI codes)
- `ConsoleTextIoInvalidity` exception for stream validation
- `produce_console_printer()` using direct console.print (with documented caveats)
- Simple `produce_pretty_formatter()` wrapper around rich.pretty_repr

### Recommendation for v2
**Focus migration on Sundae recipe** with these adaptations:
- Flatten Sundae features into baseline FlavorConfiguration
- Consider adding a Mode-like configuration option if we want timing control
- Use rich.pretty_repr as default value formatter (from Rich recipe)
- Consider ConsoleTextIoInvalidity if stream validation is needed

**Skip separate Rich recipe migration** - its functionality is either:
- Already in Sundae (most of it)
- Simple wrappers we can incorporate directly (pretty_repr)
- Edge cases with caveats we probably don't want (console.print as printer)
