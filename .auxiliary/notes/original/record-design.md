# LogRecord Design

## Overview

The LogRecord is the central data structure that flows through the ictr logging pipeline. It carries all information needed for formatting and output.

## Architecture

```
User Call → Reporter → LogRecord (raw data) → Formatter → String → Printer → Output
```

The record contains **raw, unformatted data**. Formatting happens as a separate stage.

## Record Structure

### Content Types

Records support different content types via a union:

```python
class RecordContent(__.immut.DataclassObject):
    """Base class for record content."""
    pass

class MessageContent(RecordContent):
    """Normal logging mode - arguments without inspection.

    Example: ictr('info')('Server started', 'on port 8080')
    """
    summary: str | Exception
    details: tuple[Any, ...]

class InspectionContent(RecordContent):
    """Inspection mode - arguments with extracted variable names.

    Example: ictr('debug').inspect(x, y, result)
    Produces: [('x', 42), ('y', 'hello'), ('result', {...})]
    """
    inspections: list[tuple[str | None, Any]]
    # name is None for literals, str for variables/expressions, '???' for unresolvable
```

### Main Record Class

```python
class Record(__.immut.DataclassObject):
    """Complete record passed through formatting pipeline.

    Immutable data structure carrying all context needed for formatting.
    """

    # Identity - who and what flavor
    module_name: str
    flavor: Flavor  # int | str

    # Content - varies by mode
    content: RecordContent  # MessageContent | InspectionContent

    # Context - when and where
    timestamp: datetime  # Captured at record creation
    frame: FrameType
    exc_info: Optional[ExceptionInfo] = None  # Auto-captured for errorx/abortx

    # Configuration - resolved for this specific record
    flavor_config: FlavorConfiguration
```

**Note on exc_info**: Storing frame references may impact garbage collection. If this becomes an issue, we can store minimal exception info (type, message, formatted traceback) instead of full `sys.exc_info()` tuple.

## Pipeline Flow

### 1. Record Creation (in Reporter)

**Normal mode** (`Reporter.__call__`):
```python
def __call__(self, summary: str | Exception, *details) -> None:
    if not self.enabled:
        return

    record = Record(
        module_name=self.module_name,
        flavor=self.flavor,
        content=MessageContent(summary=summary, details=details),
        timestamp=datetime.now(),
        frame=inspect.currentframe().f_back,
        exc_info=self._capture_exception_if_needed(),
        flavor_config=self.config,
    )
    self._emit(record)
```

**Inspection mode** (`Reporter.inspect`):
```python
def inspect(self, *variables) -> None:
    if not self.enabled:
        return

    # Extract variable names using executing
    frame = inspect.currentframe().f_back
    inspections = inspect_call(*variables, _frame=frame)

    record = Record(
        module_name=self.module_name,
        flavor=self.flavor,
        content=InspectionContent(inspections=inspections),
        timestamp=datetime.now(),
        frame=frame,
        exc_info=self._capture_exception_if_needed(),
        flavor_config=self.config,
    )
    self._emit(record)
```

### 2. Formatting (Formatter)

Formatter signature:
```python
Formatter: TypeAlias = Callable[[Record], str]
```

**Polymorphic approach** (delegates to content types):

```python
class RecordContent(__.immut.DataclassObject):
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
        # Format with "name: value" pairs
        # Return formatted body
        ...
```

Formatter delegates to content:

```python
def format_record(record: Record) -> str:
    config = record.flavor_config

    # Emit prefix
    if isinstance(config.prefix_emitter, str):
        prefix = config.prefix_emitter
    else:
        prefix = config.prefix_emitter(record.module_name, record.flavor)

    # Delegate body formatting to content (polymorphism)
    body = record.content.format_body(value_formatter, config)

    # Append stack trace if present (for errorx/abortx)
    # Formatting is formatter's responsibility - may use rich.traceback
    if record.exc_info and record.exc_info[0]:
        body += "\n" + format_traceback(record.exc_info)

    # Append frame context if configured
    if config.include_context:
        body += "\n" + format_context(record.frame)

    return f"{prefix}{body}"
```

### 3. Output (Printer)

Printer signature:
```python
Printer: TypeAlias = Callable[[str, LogRecord], None]
```

Example printer:
```python
def simple_printer(text: str, record: LogRecord) -> None:
    """Simple printer that outputs to stderr."""
    print(text, file=sys.stderr)
```

The printer receives both the formatted string AND the record, in case it needs metadata (timestamp, module, flavor, etc.) for routing or filtering.

## Factory Pattern

### Formatter Factory

Current signature in icecream-truck:
```python
FormatterFactory: TypeAlias = Callable[[FormatterControl, str, Flavor], Formatter]
```

New signature:
```python
FormatterFactory: TypeAlias = Callable[[FormatterControl], Formatter]
# Where Formatter = Callable[[LogRecord], str]
```

The formatter factory produces a formatter that operates on records. Module name and flavor come from the record itself, not as factory parameters.

### Printer Factory

Current signature:
```python
PrinterFactory: TypeAlias = Callable[[str, Flavor], Printer]
```

New signature stays similar but printer changes:
```python
PrinterFactory: TypeAlias = Callable[[str, Flavor], Printer]
# Where Printer = Callable[[str, LogRecord], None]
```

Or we could simplify:
```python
PrinterFactory: TypeAlias = Callable[[], Printer]
```

Since the printer gets the record, it has access to module name and flavor at call time.

## Configuration Changes

### FlavorConfiguration

Current:
```python
@dataclass
class FlavorConfiguration:
    formatter_factory: Optional[FormatterFactory] = None
    include_context: Optional[bool] = None
    prefix_emitter: Optional[PrefixEmitterUnion] = None
```

Stays mostly the same, but we clarify that formatter_factory produces a formatter that operates on LogRecords.

### VehicleConfiguration / ModuleConfiguration

These stay the same - they're about configuring how records get created and formatted, not about the record structure itself.

## Benefits of This Design

1. **Type Safety**: Content union provides type-safe distinction between modes.

2. **Clean Separation**: Record creation, formatting, and output are separate stages.

3. **Testability**: Easy to test each stage independently:
   - Test record creation
   - Test formatters with mock records
   - Test printers with mock strings/records

4. **Extensibility**: Easy to add new content types:
   - `ExceptionContent` (for stack traces)
   - `StructuredContent` (pure key-value, no args)
   - `BenchmarkContent` (timing info)

5. **Multiple Outputs**: Same record can be formatted multiple ways:
   - Human-readable text
   - JSON
   - Structured logs
   - Binary format

6. **Filtering**: Could add filter layer that operates on raw records before formatting.

## Resolved Questions

### Q1: Should timestamp be captured at record creation or Reporter creation?

**Resolved**: Record creation (more accurate).

### Q2: Should FlavorConfiguration be in the record?

**Resolved**: Yes - it's the **resolved** configuration for this specific record. Makes formatting easier since formatter has everything it needs.

### Q3: What about exception info for errorx/abortx flavors?

**Resolved**: Add `exc_info` to Record. Stack-enabled flavors (errorx, abortx) automatically capture when creating record if exception is active.

**Concern**: Storing frame references in `exc_info` may impact garbage collection. If problematic, can store minimal exception info (type, message, formatted traceback string) instead of full `sys.exc_info()` tuple.

## Next Steps

1. Prototype LogRecord class with content types
2. Update formatter signature to work with records
3. Test formatting with both MessageContent and InspectionContent
4. Design filter layer (if needed)
5. Update configuration hierarchy to reflect new signatures
