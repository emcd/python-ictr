# ICTR v2 Project Outline

**Package Name**: `ictr` (lowercase)
**Default Builtin**: `ictr`
**Backronym**: *Introspective Configurable Trace Reporting*

## Core Premises

### What We're Trying to Accomplish

1. **True logging replacement** - Not a debugging-only tool, but a production-ready logging system with optional introspection superpowers.

2. **Inspection via `executing`** - Direct integration with `executing` library (no icecream dependency) to automatically extract variable names and values.

3. **Flavor-based categorization** - Move beyond severity levels to semantic categories (success, future, io, audit, etc.) while still supporting numeric trace depths.

4. **Zero boilerplate** - Module inference eliminates `getLogger(__name__)` in every file. Just use the builtin.

5. **Library-friendly isolation** - Libraries can register their own configurations without stepping on application settings or each other.

6. **Sundae by default** - Rich formatting, emoji support, colored prefixes, and flexible templates should be built-in, not a recipe.

## Key Decisions

### Architecture

- **New separate project** - Not v2 of icecream-truck. Different branding, different target audience.
- **No icecream dependency** - Build inspection directly on `executing`.
- **Two-call pattern preserved** - `ictr(flavor)(args)` for maximum flexibility with arbitrary flavors.
- **Reporter object with methods** - First call returns reporter, second call is `__call__` or `.inspect()` method.
- **LogRecord layer** - Add record objects for filtering, routing, and transformation.
- **Factory separation** - Application controls printers (where), modules control formatters (what).

### API Shape

```python
# Installation
from ictr import install
install(trace_levels=2, active_flavors={'success', 'future', 'io'})

# Usage (module inferred)
ictr('info')('Server started', port=8080)          # Standard logging
ictr('success').inspect(user, session)             # Inspection mode
ictr(1)(state)                                     # Trace depth
ictr('io')('Query done', rows=count, ms=elapsed)   # Structured data

# Module registration (libraries)
from ictr import register_module
register_module(flavors={'internal': FlavorConfiguration(...)})
```

### Reporter Object

```python
class Reporter:
    """Returned by ictr(flavor) call."""

    def __call__(self, *args, **kwargs) -> None:
        """Standard logging/output mode.

        - If args are expressions/literals, format them
        - kwargs become structured data
        """

    def inspect(self, *args, **kwargs) -> None:
        """Inspection mode - uses executing to introspect.

        - Uses executing to extract variable names for args
        - kwargs still structured data
        """
```

### Record Design

**Note**: This section is superseded by ictr-v2-design.md. See that document for current design.

```python
class Record(__.immut.DataclassObject):
    """Context object passed through the logging pipeline."""

    # Identity
    module_name: str
    flavor: Flavor  # int | str

    # Content (varies by mode)
    content: RecordContent  # MessageContent | InspectionContent

    # Context
    timestamp: datetime  # Captured at record creation
    frame: FrameType
    exc_info: Optional[ExceptionInfo] = None  # Auto-captured for errorx/abortx

    # Configuration (resolved for this record)
    flavor_config: FlavorConfiguration
```

### Flavor System

**Pre-defined flavors** (from sundae):
- `note` (ℹ️, blue) - alias: `n`
- `monition` (⚠️, yellow) - alias: `m`
- `error` (❌, red) - alias: `e`
- `errorx` (❌, red, +stack) - alias: `ex`
- `abort` (💥, bright_red) - alias: `a`
- `abortx` (💥, bright_red, +stack) - alias: `ax`
- `future` (🔮, magenta) - alias: `f`
- `success` (✅, green) - alias: `s`

**Trace depths**: 0-9 with gradient colors (🔎, grey85→grey50) and indentation.

**Custom flavors**: Users can define their own with `FlavorConfiguration`.

### Prefix Template System

Support rich templates with interpolants:
- `{flavor}` - Decorated flavor label
- `{module_qname}` - Module qualified name
- `{timestamp}` - Current time (configurable format)
- `{process_id}` - OS process ID
- `{thread_id}` - Thread ID
- `{thread_name}` - Thread name

Default: `"{flavor}| "`
Verbose: `"{timestamp} [{module_qname}] {flavor}| "`

## Transferable from Icecream Truck

### Keep As-Is

1. **Configuration hierarchy** (`VehicleConfiguration` → `ModuleConfiguration` → `FlavorConfiguration`)
2. **Module registry** (`ModulesConfigurationsRegistry`)
3. **Active flavors registry** (per-module activation control)
4. **Trace levels registry** (per-module depth control)
5. **Factory pattern** (`printer_factory`, `formatter_factory`, `prefix_emitter`)
6. **Module inference** (`_discover_invoker_module_name()`)
7. **Environment variable parsing** (`active_flavors_from_environment`, `trace_levels_from_environment`)
8. **Truck class structure** (the vehicle abstraction)

### Adapt/Enhance

1. **FlavorConfiguration** - Add fields from sundae:
   - `color: str | None`
   - `emoji: str | None`
   - `label: str | None`
   - `stack: bool` (for exception traces)

2. **PrefixEmitter** - Enhance to support templates with interpolants (sundae's approach).

3. **FormatterControl** - Add sundae's prefix formatting controls:
   - `colorize: bool`
   - `label_as: PrefixLabelPresentations`
   - `styles: dict[str, Style]`
   - `template: str`
   - `ts_format: str`

4. **Auxiliaries** - Adopt sundae's dependency injection for:
   - `exc_info_discoverer`
   - `pid_discoverer`
   - `thread_discoverer`
   - `time_formatter`

### Replace/Remove

1. **IceCreamDebugger instances** - Replace with our own inspection implementation using `executing`.
2. **Two-stage formatting** - Current system uses icecream's formatter. We need our own that handles inspection + formatting.

## Architecture Components

**Note**: See ictr-v2-design.md for current architecture decisions.

### Core Modules

```
ictr/
├── __init__.py           # Public API
├── configuration.py      # Config hierarchy (mostly from ictruck)
├── dispatchers.py        # Dispatcher (renamed from Truck), Reporter classes
├── records.py            # Record class with content types (new)
├── inspection.py         # executing integration (new)
├── formatting.py         # Formatters and prefix rendering (from sundae)
├── printers.py           # Printer factories (from ictruck)
├── exceptions.py         # Exception types (from ictruck)
└── _typedecls/           # Type declarations (from ictruck)
```

### Inspection Implementation

Key challenge: Use `executing` to extract variable names from call site.

```python
def inspect_call(frame: FrameType) -> list[tuple[str, Any]]:
    """Extract variable names and values from calling frame."""
    source = executing.Source.executing(frame)
    # Parse AST to get argument expressions
    # Match expressions to values in frame.f_locals
    # Return list of (name, value) pairs
```

### Formatter Pipeline

```
LogRecord → Formatter → String → Printer → Output
```

Where:
- **LogRecord** carries all context
- **Formatter** converts to string (inspects variables, applies rich formatting, renders prefix)
- **Printer** outputs to destination (stderr, file, logger, etc.)

### Default Behavior

Out of the box (no configuration):
- Sundae-style formatting with rich
- All flavors available but disabled
- `trace_levels=-1` (all traces disabled)
- `active_flavors={}` (no string flavors enabled)
- Output to stderr with color detection

Users must explicitly enable via `install(trace_levels=..., active_flavors=...)` or environment variables.

## Open Questions

1. **Should `.inspect()` use executing unconditionally?** Or should it fall back to regular formatting if executing fails?

2. **How to handle mixed literal + variable args?** E.g., `ictr('io').inspect('Reading', filename)` - should 'Reading' stay literal and only filename get inspected?

3. **Should regular `__call__` ever use inspection?** Or is it strictly for literals/expressions without names?

4. **Exception handling for stack flavors** - Should `errorx`/`abortx` automatically capture exception info, or require an exception to be active?

5. **Performance** - Should we cache `executing.Source` instances per module to avoid re-parsing?

6. **Filtering layer** - Do we need `FilterFactory` or is enable/disable via active_flavors/trace_levels sufficient?

## Next Steps

1. Design the `LogRecord` class in detail
2. Prototype `executing` integration for variable inspection
3. Design the Reporter class with `__call__` vs `.inspect()` semantics
4. Map out the formatter pipeline
5. Identify which code can be directly copied vs. needs adaptation
6. Create new project structure and begin implementation

## Naming Alternatives

If "Introspective Configurable Trace Reporting" doesn't resonate:

- **Inspection-Capable Trace Reporting** (more literal)
- **Intelligent Configurable Trace Reporter** (emphasizes smart behavior)
- **Introspective Code Tracer/Reporting** (emphasizes code analysis)
- **Inspection, Configuration, Traces, Reporting** (just list the features)

Or we could lean into the metaphor and not have it be an acronym at all - just call it "Ictr" as a word/name.
