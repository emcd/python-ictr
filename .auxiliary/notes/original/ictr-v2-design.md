# ICTR v2 Design Specification

## Overview

This document captures the core design decisions for ictr v2, a logging replacement with inspection capabilities built on the `executing` library.

## Architecture Overview

```
User Code → Dispatcher → Reporter → Record → Formatter → String → Printer → Output
```

### Components

- **Dispatcher**: Central coordinator that vends Reporter instances. One Dispatcher per application.
- **Reporter**: Flavor-specific logger for a module. Vended by Dispatcher, cached per (module, flavor).
- **Record**: Immutable data structure carrying logging context through the pipeline.
- **Formatter**: Converts Record to string (rich/colorized). Configured per module/flavor.
- **Printer**: Outputs formatted string to destination, decolorizing if needed. Configured per application.

## Record Design

### Content Types

Records have mode-specific content:

```python
@dataclass
class RecordContent:
    """Base for content types."""
    pass

@dataclass
class MessageContent(RecordContent):
    """Normal reporting mode - no inspection.

    Signature: (summary, *details)
    - summary: Main message (str or Exception)
    - details: Additional context values (formatted as literals)
    """
    summary: str | Exception
    details: tuple[Any, ...]

@dataclass
class InspectionContent(RecordContent):
    """Inspection mode - with variable names extracted.

    Signature: (*variables)
    - variables: Inspected with names extracted via executing
    """
    inspections: list[tuple[str | None, Any]]
    # name is None for literals, str for variables/expressions, '???' for unresolvable
```

### Main Record Class

```python
class Record(__.immut.DataclassObject):
    """Immutable record passed through formatting pipeline.

    Uses __.immut.DataclassObject from frigid library for deep immutability.
    """

    # Identity
    module_name: str
    flavor: Flavor  # int | str

    # Content (mode-specific)
    content: RecordContent  # MessageContent | InspectionContent

    # Context
    timestamp: datetime
    frame: FrameType
    exc_info: Optional[ExceptionInfo] = None  # Auto-captured for errorx/abortx

    # Resolved configuration (cached from Reporter)
    flavor_config: FlavorConfiguration
```

**Design decisions:**
- **Immutable**: Uses `__.immut.DataclassObject` for frozen dataclass
- **No structured_data**: Keep API simple, no kwargs for extra data
- **No interpolation**: Users should use f-strings for template formatting
- **Exception autocapture**: Only for errorx/abortx flavors, only if exception is active

## Reporter API

### Reporter Class

```python
class Reporter(__.immut.DataclassObject):
    """Reporter for a specific (module, flavor) pair.

    Created by Dispatcher and cached. Contains pre-resolved configuration
    and baked-in formatter/printer instances.
    """

    module_name: str
    flavor: Flavor
    dispatcher: Dispatcher  # Reference back to parent Dispatcher
    formatter: Formatter  # Baked in at creation
    printer: Printer  # Baked in at creation
    config: FlavorConfiguration  # Pre-resolved at Reporter creation
    enabled: bool  # Pre-calculated at Reporter creation

    def __call__(self, summary: str | Exception, *details) -> None:
        """Normal reporting mode - format summary and details without inspection.

        Args:
            summary: Main message (string) or exception
            *details: Additional context values (formatted as literals)

        Example:
            ictr('info')('Server started', 'Port 8080', 'IPv4')
            # Output: INFO| 'Server started', 'Port 8080', 'IPv4'

            ictr('error')(exception, 'During startup')
            # Output: ERROR| ValueError: ..., 'During startup'
        """

    def inspect(self, *variables) -> None:
        """Inspection mode - extract variable names and format with values.

        Args:
            *variables: Variables/expressions to inspect

        Example:
            ictr('debug').inspect(x, y, result)
            # Output: DEBUG| x: 42, y: 'hello', result: {...}
        """
```

**Design decisions:**
- **No kwargs**: Methods accept only positional args (no keyword arguments)
- **Normal mode signature**: `(summary, *details)` - summary is special
- **Summary flexibility**: Can be string or Exception
- **Inspection signature**: `(*variables)` - all args inspected equally

### Example Usage

```python
# Installation
from ictr import install
install(trace_levels=2, active_flavors={'success', 'error'})

# Normal reporting
ictr('info')('Server started')
# Output: INFO| 'Server started'

ictr('info')('Connection accepted', client_ip, port)
# Output: INFO| 'Connection accepted', '192.168.1.1', 8080

# Exception reporting
try:
    process_data()
except ValueError as e:
    ictr('error')(e, 'During data processing')
# Output: ERROR| ValueError: invalid data, 'During data processing'

# Inspection
result = compute(x, y)
ictr('debug').inspect(x, y, result)
# Output: DEBUG| x: 42, y: 'hello', result: {...}

# Trace depths with indentation
ictr(0)('Starting')
ictr(1)('Processing', count)
# Output: TRACE0| 'Starting'
#         TRACE1|   'Processing', 5
```

## Formatting Pipeline

### FormatterControl

Context about output constraints passed to formatter factories:

```python
class FormatterControl(__.immut.DataclassObject):
    """Context about output constraints.

    Formatters produce rich/colorized output. Printers handle decolorization
    if target doesn't support it (e.g., not a TTY, NO_COLOR set).
    """

    # Display constraints
    columns_total: Optional[int] = None        # Total terminal width (if detectable)
    columns_after_prefix: Optional[int] = None # Space left after prefix

    # Formatting preferences
    prefer_compact: bool = False      # Use compact vs. expanded format
    depth_max: Optional[int] = None   # Maximum depth for nested structures
    length_max: Optional[int] = None  # Maximum length before truncation
```

The Dispatcher populates this based on output target constraints.

### Formatter Signature

```python
Formatter: TypeAlias = Callable[[Record], str]
FormatterFactory: TypeAlias = Callable[[FormatterControl], Formatter]
```

Formatters receive a Record and return formatted string. The Record contains all needed context (module, flavor, content, config).

### Formatter Implementation Approach

Formatters receive a Record and return a formatted string. The string may contain
rich markup or ANSI color codes - printers handle decolorization if needed.

**Polymorphic approach** (recommended):

Content types implement their own formatting:

```python
class RecordContent:
    """Base for content types with polymorphic formatting."""

    def format_body(self, value_formatter: Callable, config: FlavorConfiguration) -> str:
        """Format the content body. Subclasses implement."""
        raise NotImplementedError

class MessageContent(RecordContent):
    summary: str | Exception
    details: tuple[Any, ...]

    def format_body(self, value_formatter, config) -> str:
        # Format summary (Exception or string)
        # Format details as literals
        # Return formatted body
        ...

class InspectionContent(RecordContent):
    inspections: list[tuple[str | None, Any]]

    def format_body(self, value_formatter, config) -> str:
        # Format with variable names
        # Return formatted body with "name: value" pairs
        ...
```

Then formatters delegate to content:

```python
def format_record(record: Record) -> str:
    config = record.flavor_config

    # Emit prefix
    prefix = emit_prefix(config, record.module_name, record.flavor)

    # Delegate body formatting to content
    body = record.content.format_body(value_formatter, config)

    # Append stack trace if present (for errorx/abortx)
    if record.exc_info and record.exc_info[0]:
        body += "\n" + format_traceback(record.exc_info)

    # Append frame context if configured
    if config.include_context:
        body += "\n" + format_context(record.frame)

    return f"{prefix}{body}"
```

**Key principles:**
- Formatters produce rich/colorized output
- Content types handle their own body formatting (polymorphism)
- Printers handle decolorization (not formatters)
- Summary and details formatted differently in MessageContent
- Inspections show "name: value" format in InspectionContent

### Printer Signature

```python
Printer: TypeAlias = Callable[[str, Record], None]
PrinterFactory: TypeAlias = Callable[[str, Flavor], Printer]
```

Printers receive both the formatted string AND the record (for metadata like timestamp, module, flavor if needed for routing).

## Reporter Caching and Configuration

### Dispatcher Responsibilities

```python
class Dispatcher:
    """Central coordinator that vends Reporter instances."""

    _reporters: dict[tuple[str, Flavor], Reporter]
    _reporters_lock: Lock

    # Configuration (immutable after initialization)
    active_flavors: ActiveFlavorsRegistry
    trace_levels: TraceLevelsRegistry
    generalcfg: VehicleConfiguration
    modulecfgs: ModulesConfigurationsRegistry
    formatter_factory: FormatterFactory
    printer_factory: PrinterFactory

    def __call__(self, flavor: Flavor, *, module_name: Optional[str] = None) -> Reporter:
        """Vend a Reporter for the given flavor.

        Creates Reporter with formatter and printer baked in.
        Reporters are cached - same (module, flavor) returns same instance.

        Similar to ictruck v1 pattern:
        - Calls formatter_factory(control, module_name, flavor)
        - Calls printer_factory(module_name, flavor)
        - Creates Reporter with formatter/printer attached
        - Caches and returns Reporter
        """
```

**Design decisions:**
- **Configuration immutable**: After Dispatcher initialization, config doesn't change
- **Reporter caching**: Same (module, flavor) returns cached instance
- **Pre-resolved config**: Configuration resolved once at Reporter creation, stored in Reporter
- **Pre-calculated enabled**: Whether flavor is enabled computed once at Reporter creation

### Exception Autocapture

For `errorx` and `abortx` flavors:

```python
def _capture_exception_if_needed(self) -> Optional[ExceptionInfo]:
    """Capture exception info for errorx/abortx flavors."""
    if self.flavor in ('errorx', 'abortx'):
        exc = sys.exc_info()
        if exc[0] is not None:  # Exception is active
            return exc
    return None
```

**Decision**: Only capture if (1) flavor is errorx/abortx AND (2) exception is currently active.

## Configuration Hierarchy

### Preserved from Icecream Truck

The three-level configuration hierarchy is maintained:

1. **VehicleConfiguration** (Truck-level, global defaults)
2. **ModuleConfiguration** (Per-module or per-package)
3. **FlavorConfiguration** (Per-flavor, most specific)

### FlavorConfiguration

Enhanced with fields from sundae recipe:

```python
class FlavorConfiguration(__.immut.DataclassObject):
    """Per-flavor configuration."""

    # Formatting
    formatter_factory: Optional[FormatterFactory] = None

    # Prefix
    prefix_emitter: Optional[PrefixEmitterUnion] = None
    include_context: Optional[bool] = None

    # Visual (from sundae)
    color: Optional[str] = None      # Color name for prefix
    emoji: Optional[str] = None      # Emoji for prefix
    label: Optional[str] = None      # Text label for flavor
    stack: bool = False              # Auto-capture stack traces
```

## Deferred Features

Features explicitly deferred to later versions:

1. **Filtering layer**: Record filters for suppression/rate-limiting
2. **Structured data (kwargs)**: Extra key-value data beyond args
3. **Template interpolation**: Custom string templating (use f-strings instead)
4. **Method kwargs**: Options to control formatting behavior

These can be added later without breaking the core API.

## Dependencies

New dependencies for v2:

- `executing` - AST introspection for variable name extraction
- `asttokens` - Required by executing for source text extraction

Both should be added to project dependencies.

## Migration from Icecream Truck v1

### What Transfers

- Configuration hierarchy (VehicleConfiguration → ModuleConfiguration → FlavorConfiguration)
- Module registry and registration pattern
- Active flavors and trace levels registries
- Environment variable parsing
- Truck concept and module inference
- Factory pattern for formatters and printers

### What Changes

- **No icecream dependency**: Direct `executing` integration
- **Record-based pipeline**: Formatters work on Records, not raw values
- **Inspection via .inspect()**: Opt-in method, not default behavior
- **Reporter two-call pattern**: `truck(flavor).inspect(args)` or `truck(flavor)(summary, *details)`
- **Summary + details signature**: Normal mode has special first arg

### Breaking Changes

Since this is a new project (ictr, not icecream-truck v2), breaking changes are acceptable. The API is fundamentally different:

**Old**:
```python
ictr(1)('Starting process')  # Always inspects
```

**New**:
```python
ictr(1)('Starting process')        # Normal mode - no inspection
ictr(1).inspect(process_state)     # Inspection mode - explicit
```

## Implementation Decisions

### Formatter and Printer Coupling

**Decision**: Dispatcher creates Reporter instances with formatter and printer baked in, similar to how ictruck Truck creates IceCreamDebugger instances.

Pattern from ictruck v1:
```python
# Dispatcher calls factories when creating Reporter
formatter = formatter_factory(control, module_name, flavor)
printer = printer_factory(module_name, flavor)

reporter = Reporter(
    module_name=module_name,
    flavor=flavor,
    dispatcher=self,
    formatter=formatter,  # Baked in
    printer=printer,      # Baked in
    config=resolved_config,
    enabled=enabled,
)
```

Reporters are cached with formatter/printer already attached. No need for `get_formatter()` or `get_printer()` methods.

### Long Argument Lists

**Decision**: Spread across multiple lines or Rich panels. Formatters handle layout based on FormatterControl.columns_total and FormatterControl.length_max.

### Stack Trace Formatting

**Decision**: Formatting is formatter's responsibility. Default formatter may use `rich.traceback` for pretty printing. This is configuration-driven, not hardcoded.

### Printer Decolorization

**Decision**: Each printer decides how to handle formatted input (minimal coupling).

- Color support detection: Same as ictruck (check TTY, NO_COLOR environment variable)
- ANSI stripping: Regex for CSI/OSC sequences (same as ictruck)
- Per-printer decision: Printer inspects its target and decolorizes if needed

Example from ictruck:
```python
def _simple_print(text: str, target: TextIOBase, force_color = False) -> None:
    if not force_color and not target.isatty():
        print(_remove_ansi_c1_sequences(text), file=target)
        return
    print(text, file=target)
```

### Caching

**Decision**: Don't optimize prematurely. Reporters are cached (with formatters/printers baked in), but we won't cache intermediate results initially. Can optimize later if needed.

## Summary of Design Decisions

### Core Decisions

- ✅ Record is central data structure (immutable via `__.immut.DataclassObject`)
- ✅ Two content types: MessageContent (summary + details) and InspectionContent (inspected vars)
- ✅ No structured_data field - keep API simple
- ✅ No interpolation - users use f-strings
- ✅ No kwargs on reporter methods (for now)
- ✅ Normal mode: `(summary, *details)` - summary can be string or Exception
- ✅ Inspection mode: `(*variables)` - all inspected equally
- ✅ Exception autocapture: Only for errorx/abortx when exception is active
- ✅ Reporter caching: Cache instances with pre-resolved config
- ✅ FormatterControl: Rich with terminal info (colors, columns, unicode, etc.)
- ✅ Filtering layer: Deferred to later
- ✅ Prefix rendering: Part of formatter, not separate stage

### Migration Decisions

- ✅ New project: ictr, not icecream-truck v2
- ✅ Preserve: Configuration hierarchy, module registry, factory pattern
- ✅ Replace: Icecream dependency, inspection mechanism, API shape
- ✅ Backronym: "Inspection-Capable Trace Reporters" (or just "ictr")

## Next Steps

1. Create new `ictr` repository
2. Set up project structure (sources/ictr/, tests/, etc.)
3. Implement Record and content types
4. Port configuration hierarchy from icecream-truck
5. Implement Reporter with both modes
6. Implement basic formatters and printers
7. Test with execution prototype insights
8. Add sundae-style default flavors
9. Write comprehensive examples and documentation
