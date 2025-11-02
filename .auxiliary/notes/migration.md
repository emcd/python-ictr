# ICTR v2 Migration Plan

This document tracks the migration of code and concepts from `python-icecream-truck` (v1) to `python-ictr` (v2).

**Last Updated**: 2025-11-01

## Migration Status Overview

### ✅ Already Migrated (Partially Adapted)

These files have been copied from ictruck to ictr and partially adapted for v2:

1. **`sources/ictr/configuration.py`** (from `ictruck/configuration.py`)
   - Status: Partially adapted
   - Changes needed:
     - Remove `_icecream` references (lines 155, 167)
     - Update `FormatterControl` to match v2 design (needs columns_total, columns_after_prefix, prefer_compact, depth_max, length_max)
     - Update `Formatter` signature from `Callable[[Any], str]` to `Callable[[Record], str]`
     - Add `Record` and `RecordContent` classes (MessageContent, InspectionContent)
     - Update `FlavorConfiguration` to add sundae fields (color, emoji, label, stack)
     - Rename `VehicleConfiguration` to `DispatcherConfiguration` (partially done)
     - Update factory signatures to match v2 design

2. **`sources/ictr/dispatchers.py`** (renamed from `vehicles.py`)
   - Status: ✅ Renamed, partially adapted
   - Changes needed:
     - Remove all `_icecream.IceCreamDebugger` references
     - Implement `Reporter` class with `__call__(summary, *details)` method
     - Update `Dispatcher` to create and cache `Reporter` instances instead of IceCreamDebugger
     - Update printer factory integration to pass Record to printers
     - Remove `_calculate_ic_initargs` and replace with Reporter initialization
   - Note: `.inspect()` method **DEFERRED** - see decision log below

3. **`sources/ictr/exceptions.py`** (from `ictruck/exceptions.py`)
   - Status: ✅ Complete
   - Ported exceptions:
     - `ArgumentClassInvalidity` (TypeError)
     - `AttributeNondisplacement` (AttributeError)
     - `FlavorInavailability` (ValueError)
     - `ModuleInferenceFailure` (RuntimeError)
   - `Omniexception` base class updated to use `frigid.immut.exceptions.Omniexception`

4. **`sources/ictr/__/nomina.py`** (from `ictruck/__/nomina.py`)
   - Status: Appears complete
   - Changes needed: Review and confirm completeness

5. **`sources/ictr/__/imports.py`** (from `ictruck/__/imports.py`)
   - Status: Partially adapted (missing many imports from v1)
   - Changes needed:
     - Add missing standard library imports (see v1 for full list)
     - May need to add `executing` and `asttokens` imports

### 🔄 Needs Migration (Direct or Adapted)

#### Core Implementation Files

6. **`sources/ictr/printers.py`** (from `ictruck/printers.py`)
   - Priority: HIGH
   - Status: Not started
   - Adaptation needed:
     - Update `Printer` signature from `Callable[[str], None]` to `Callable[[str, Record], None]`
     - Keep decolorization logic (`_remove_ansi_c1_sequences`, `_simple_print`)
     - Keep colorama integration for Windows
     - Review if printer needs Record for routing/metadata decisions

7. **`sources/ictr/__/miscellany.py`** (from `ictruck/__/miscellany.py`)
   - Priority: MEDIUM
   - Status: Not started
   - Adaptation needed: Minimal, mainly `install_builtin_safely` utility
   - Note: Current ictr lacks this utility but dispatchers.py may reference it

8. **`sources/ictr/__/validators.py`** (from `ictruck/__/validators.py`)
   - Priority: MEDIUM
   - Status: Not started
   - Adaptation needed: Minimal, used for argument validation
   - Note: dispatchers.py references `_validate_arguments`

#### New Files for v2

9. **`sources/ictr/records.py`** (NEW)
   - Priority: HIGH
   - Content needed:
     - `Record` dataclass (main record structure)
     - `RecordContent` base class
     - `MessageContent` dataclass (summary + details)
     - `InspectionContent` dataclass (inspections with names)
     - Polymorphic `format_body()` methods on content types
   - Reference: `.auxiliary/notes/original/record-design.md`

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

11. **`sources/ictr/formatters.py`** (NEW, adapted from recipes)
    - Priority: HIGH
    - Content needed:
      - Default formatter implementation
      - Value formatting utilities (pretty-print for complex types)
      - Prefix emission logic (templates with interpolants)
      - Rich formatting integration
      - Exception/traceback formatting
      - Context frame formatting
    - References to adapt from:
      - `ictruck/recipes/sundae.py` (prefix templates, emoji, colors)
      - `ictruck/recipes/rich.py` (rich formatting)
      - Design: `.auxiliary/notes/original/ictr-v2-design.md` sections on formatting

12. **`sources/ictr/reporters.py`** (NEW or merge into dispatchers.py)
    - Priority: HIGH
    - Status: In progress (user implementing)
    - Content needed:
      - `Reporter` class with proper v2 API
      - `__call__(summary, *details)` method (normal mode)
      - Pre-resolved configuration storage
      - Pre-calculated enabled flag
      - Exception autocapture for errorx/abortx
    - Note: `.inspect(*variables)` method **DEFERRED** (see decision log)
    - Decision: Likely to merge into dispatchers.py for cohesion

#### Reference/Recipe Files (Adapt for Formatters)

13. **Review `ictruck/recipes/sundae.py`**
    - Priority: MEDIUM
    - Purpose: Extract prefix templates, flavor definitions, emoji/color configs
    - Content to adapt:
      - Pre-defined flavors (note, monition, error, errorx, abort, abortx, future, success)
      - Prefix template system with interpolants
      - Emoji and color configurations
      - Style definitions

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

## Migration Priorities

### Phase 1: Core Infrastructure (BLOCKING)
Must be done before any functionality works:

1. Complete `configuration.py` updates (remove icecream, add Record)
2. Create `records.py` with Record and content classes
3. Create `inspection.py` from prototype
4. Migrate `printers.py` with updated signatures
5. Migrate `__/miscellany.py` and `__/validators.py`

### Phase 2: Reporter Implementation (HIGH PRIORITY)
Core v2 functionality:

6. Create/update `Reporter` class in `vehicles.py`
7. Update `Dispatcher` to vend Reporters
8. Integrate inspection into Reporter.inspect()
9. Implement Record creation in both Reporter modes

### Phase 3: Formatting (HIGH PRIORITY)
Make output readable:

10. Create `formatters.py` with basic formatter
11. Adapt prefix templates from sundae recipe
12. Add rich formatting support
13. Implement polymorphic content formatting

### Phase 4: Polish (MEDIUM PRIORITY)
Complete the system:

14. Add pre-defined flavors (sundae-style)
15. Add exception/traceback formatting
16. Port tests from prototypes
17. Update README and documentation

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
