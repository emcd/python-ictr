# Traceback Formatting Findings

**Date**: 2025-11-08
**Experiment**: `.auxiliary/scribbles/traceback_experiments.py`

## Summary

Experiments to determine best approach for formatting exception tracebacks with width constraints in ictr textualizers.

## Key Findings

### 1. stdlib `traceback` Module

**No width constraint support**:
- `traceback.format_exception()` - fixed width output
- `traceback.format_tb()` - fixed width output
- `TracebackException.format()` - fixed width output
- No width parameter in any stdlib traceback method

**Manual wrapping fails**:
```python
# Wrapping at 60 chars breaks structure completely
Traceback (most recent call last):
  File "/home/me/src/python-
  ictr/.auxiliary/scribbles/traceback_experiments.py", line
  37, in generate_nested_exception
```
File paths split across lines become unreadable.

**StackSummary gives frame-level access**:
```python
stack = traceback.extract_tb(exc_tb)
for frame in stack:
    print(f"File: {frame.filename}:{frame.lineno}")
    print(f"  Function: {frame.name}")
    print(f"  Code: {frame.line.strip()}")
```
But no built-in width control.

**extract_stack() works for non-exception stacks**:
```python
# For inspection/debugging without exceptions
stack = traceback.extract_stack()
```
Returns StackSummary with current call stack.

### 2. Rich `Traceback`

**DOES support width constraints**:
```python
console = rich.console.Console(width=60)
tb = rich.traceback.Traceback.from_exception(exc_type, exc_value, exc_tb)
console.print(tb)
```

**Wraps intelligently**, preserving structure even at narrow widths (40 cols):
```
╭─ Traceback (most recent call last) ──╮
│ /home/me/src/python-ictr/.auxiliary/ │
│ scribbles/traceback_experiments.py:3 │
│ 7 in generate_nested_exception       │
│                                      │
│    34 │   """Create a nested excepti │
│    35 │   try:                       │
│    36 │   │   try:                   │
│ ❱  37 │   │   │   1 / 0              │
```

**Can capture output** as string:
```python
import io
buffer = io.StringIO()
console = rich.console.Console(width=60, file=buffer, force_terminal=True)
console.print(tb)
output = buffer.getvalue()  # String with ANSI codes
```

**Exception-focused**:
- Rich `Traceback.extract()` requires exception (not None)
- Not designed for non-exception stack traces
- Stick with stdlib for inspection/debugging stacks

**Includes ANSI escape sequences**:
- Output contains colors, box-drawing characters
- Need to strip ANSI if using in plain mode
- Or use `console.capture()` which might be cleaner

### 3. Custom Formatting

**Full control** over width and layout:
```python
def format_compact_traceback(exc_type, exc_value, exc_tb, max_width=None):
    lines = []
    lines.append(f"{exc_type.__name__}: {exc_value}")

    tb = exc_tb
    while tb is not None:
        frame = tb.tb_frame
        filename = frame.f_code.co_filename
        lineno = tb.tb_lineno
        name = frame.f_code.co_name

        location = f"{filename}:{lineno} in {name}()"
        if max_width and len(location) > max_width:
            excess = len(location) - max_width + 3
            location = f"...{location[excess:]}"

        lines.append(f"  at {location}")
        tb = tb.tb_next

    # Handle chained exceptions
    if exc_value.__cause__:
        lines.append("\nCaused by:")
        lines.extend(format_compact_traceback(
            type(exc_value.__cause__),
            exc_value.__cause__,
            exc_value.__cause__.__traceback__,
            max_width))

    return lines
```

**Output** is compact and readable:
```
ValueError: Invalid calculation
  at ...raceback_experiments.py:39 in generate_nested_exception()

Caused by:
ZeroDivisionError: division by zero
  at ...raceback_experiments.py:37 in generate_nested_exception()
```

**Pros**:
- Maximum flexibility
- Width control precise
- Can choose what to show (locals, context lines, etc.)

**Cons**:
- More implementation work
- Need to handle all edge cases manually
- Chained exceptions require recursive handling

## Recommendations for ictr

### Plain Mode (no Rich)

**Use custom compact formatting**:
1. Walk traceback with `traceback.extract_tb(exc_tb)`
2. Format each frame manually with width constraints
3. Include: location (file:line), function name, line of code
4. Handle chained exceptions (`__cause__`, `__context__`)
5. Truncate long paths from left: `"...file.py:123"`

**Example structure**:
```
[ExceptionType] message
  at file.py:123 in function_name()
    code line here
  at other.py:456 in other_function()
    other code line
```

**For inspection stacks** (non-exception):
- Use `traceback.extract_stack()`
- Same formatting approach
- Mark as "Call stack" vs "Traceback"

### Rich Mode (with Rich)

**Use Rich Traceback directly**:
```python
console = _produce_rich_console(control, columns_count)
tb = rich.traceback.Traceback.from_exception(exc_type, exc_value, exc_tb)
with console.capture() as capture:
    console.print(tb)
text = capture.get()
return tuple(text.split('\n'))
```

**Benefits**:
- Beautiful rendering with colors, boxes
- Correct wrapping at any width
- Handles all exception types (groups, chained, etc.)
- Code context with syntax highlighting
- Local variables display (if enabled)

**For inspection stacks (unified approach!)**:
- **Manual Trace construction works!** (See `.auxiliary/scribbles/rich_stack_construction.py`)
- Convert `traceback.extract_stack()` StackSummary to Rich Frame objects
- Wrap in `Stack` → `Trace` → `Traceback` for unified rendering
- Solves bifurcation problem - same Rich rendering for exceptions and inspection

**Frame construction details**:
```python
# Frame is a dataclass with these fields:
Frame(
    filename: str,
    lineno: int,
    name: str,
    line: str = '',
    locals: Optional[Dict[str, rich.pretty.Node]] = None,
    last_instruction: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
)
```

**Example - converting stdlib stack to Rich**:
```python
from rich.traceback import Trace, Stack, Frame, Traceback

# Get stdlib stack
stack_summary = traceback.extract_stack()

# Convert to Rich frames
rich_frames = [
    Frame(
        filename=frame.filename,
        lineno=frame.lineno,
        name=frame.name,
        line=frame.line or ''
    )
    for frame in stack_summary
]

# Wrap and render
stack = Stack(exc_type="CallStack", exc_value="Inspection", frames=rich_frames)
trace = Trace(stacks=[stack])
tb = Traceback(trace=trace)
console.print(tb)  # Beautiful Rich rendering!
```

### Exception Groups

**Note**: `ExceptionGroup` available in Python 3.11+ or via `exceptiongroup` backport package for Python 3.10

With `exceptiongroup` backport:
- Can use `ExceptionGroup` with Python 3.10
- Does not add `except*` syntax (not needed for our use case)
- stdlib and Rich both handle groups correctly
- Custom formatter needs recursive group walking

### Local Variables Display

**Configuration option**: Should we expose `show_locals` parameter?

**Pros**:
- Very useful for debugging
- Rich renders locals beautifully with syntax highlighting
- Can help diagnose issues without debugger

**Cons**:
- Can be verbose, especially for large objects
- May expose sensitive data in logs
- Performance impact (serializing locals)

**Recommendation**: Add as optional parameter to TextualizerConfiguration
```python
class TextualizerConfiguration:
    # ...
    traceback_show_locals: bool = False
    traceback_max_frames: int = 20
```

## Implementation Strategy

### For `_prepare_exception_lines_plain()`

```python
def _prepare_exception_lines_plain(
    control: TextualizerControl,
    columns_count: Optional[int],
    exception: BaseException,
) -> tuple[str, ...]:
    '''Format exception with traceback for plain mode.'''

    lines: list[str] = []
    max_width = columns_count if columns_count else None

    # Walk traceback
    tb = exception.__traceback__
    if tb:
        stack = traceback.extract_tb(tb)
        for frame in stack:
            location = f"{frame.filename}:{frame.lineno} in {frame.name}()"

            # Truncate if needed
            if max_width and len(location) > max_width:
                excess = len(location) - max_width + 3
                location = f"...{location[excess:]}"

            lines.append(f"  at {location}")

            # Optionally include code line
            if frame.line:
                code = frame.line.strip()
                if max_width and len(code) > max_width - 4:
                    code = code[:max_width-7] + '...'
                lines.append(f"    {code}")

    # Exception message at end
    exc_type = type(exception).__name__
    exc_msg = str(exception)
    lines.append(f"{exc_type}: {exc_msg}")

    # Handle chained exceptions
    if exception.__cause__:
        lines.append("")
        lines.append("Caused by:")
        lines.extend(_prepare_exception_lines_plain(
            control, columns_count, exception.__cause__))
    elif exception.__context__ and not exception.__suppress_context__:
        lines.append("")
        lines.append("During handling of this exception:")
        lines.extend(_prepare_exception_lines_plain(
            control, columns_count, exception.__context__))

    return tuple(lines)
```

### For `_prepare_exception_lines_rich()`

```python
def _prepare_exception_lines_rich(
    control: TextualizerControl,
    columns_count: Optional[int],
    exception: BaseException,
    show_locals: bool = False,
    max_frames: int = 20,
) -> tuple[str, ...]:
    '''Format exception with traceback using Rich.'''

    console = _produce_rich_console(control, columns_count)

    tb = rich.traceback.Traceback.from_exception(
        type(exception), exception, exception.__traceback__,
        show_locals=show_locals,
        max_frames=max_frames,
    )

    with console.capture() as capture:
        console.print(tb)

    text = capture.get()
    return tuple(text.split('\n'))
```

### For inspection/debugging stacks (Rich mode)

```python
def _prepare_stack_lines_rich(
    control: TextualizerControl,
    columns_count: Optional[int],
    stack_summary: traceback.StackSummary,
    label: str = "Call Stack",
) -> tuple[str, ...]:
    '''Format non-exception stack using Rich for unified rendering.'''

    from rich.traceback import Trace, Stack, Frame, Traceback

    # Convert stdlib frames to Rich frames
    rich_frames = [
        Frame(
            filename=frame.filename,
            lineno=frame.lineno,
            name=frame.name,
            line=frame.line or ''
        )
        for frame in stack_summary
    ]

    # Wrap in Rich structures
    stack = Stack(
        exc_type=label,
        exc_value="Stack trace (no exception)",
        frames=rich_frames
    )
    trace = Trace(stacks=[stack])
    tb = Traceback(trace=trace)

    # Render
    console = _produce_rich_console(control, columns_count)
    with console.capture() as capture:
        console.print(tb)

    text = capture.get()
    return tuple(text.split('\n'))
```

## Questions Answered

**Q: Can stdlib traceback formatting respect width limits?**
A: No. No built-in support for width constraints.

**Q: How does Rich handle traceback rendering?**
A: Excellent support via `Console(width=N)`. Wraps intelligently, preserves structure.

**Q: Can we generate stack traces without exceptions (for inspection)?**
A: Yes, with `traceback.extract_stack()` in stdlib. Rich is exception-focused, so use stdlib for inspection.

**Q: How do exception groups render in both approaches?**
A: Both stdlib and Rich handle groups (Python 3.11+). Rich adds visual hierarchy. Need Python 3.11+ for `ExceptionGroup`.

## Addressing Key Concerns

### 1. ExceptionGroup Backport

**Good news**: The `exceptiongroup` package provides `ExceptionGroup` for Python 3.10!
- Install: `pip install exceptiongroup`
- Usage: `from exceptiongroup import ExceptionGroup`
- Does not modify Python syntax (no `except*` blocks)
- We don't need `except*` for our use case
- Both stdlib and Rich handle groups correctly with backport

**Recommendation**: Add `exceptiongroup` as dependency for Python <3.11

### 2. Unified Rich Rendering for All Stack Traces

**Solved!** Manual `Trace` construction works perfectly (see experiments).

**Benefits of unified approach**:
- Same beautiful Rich rendering for exceptions AND inspection
- No bifurcation - one code path for Rich mode
- Consistent visual appearance across all stack traces
- Width-aware wrapping for both use cases

**Implementation**:
```python
# For exceptions - use built-in extraction
tb = rich.traceback.Traceback.from_exception(exc_type, exc_value, exc_tb)

# For inspection - manual construction
stack_summary = traceback.extract_stack()
rich_frames = [Frame(frame.filename, frame.lineno, frame.name, frame.line or '')
               for frame in stack_summary]
stack = Stack(exc_type="CallStack", exc_value="Inspection", frames=rich_frames)
trace = Trace(stacks=[stack])
tb = rich.traceback.Traceback(trace=trace)

# Both render the same way!
console.print(tb)
```

### 3. Local Variables Configuration

**Recommendation**: Yes, expose as configuration option.

**Rationale**:
- Very useful for debugging production issues
- Rich renders locals beautifully with proper formatting
- Performance impact is acceptable for debugging scenarios
- Security concern mitigated by making it opt-in (default: False)

**Proposed configuration**:
```python
class TextualizerConfiguration:
    # ...existing fields...

    # Traceback configuration
    traceback_show_locals: bool = False
    traceback_max_frames: int = 20
    traceback_show_context: bool = True  # Show code lines around error
```

**Usage control**:
- `errorx`/`abortx` flavors: Maybe enable locals by default
- `note`/`info` flavors: Keep disabled
- User can override per-flavor or globally

## Next Steps

1. Add `exceptiongroup` to dependencies (Python <3.11)
2. Implement `_prepare_exception_lines_plain()` with custom compact formatting
3. Implement `_prepare_exception_lines_rich()` using Rich Traceback extraction
4. Implement `_prepare_stack_lines_rich()` for unified inspection rendering
5. Add traceback configuration to `TextualizerConfiguration`
6. Test with various exception types (chained, nested, groups)
7. Test manual Trace construction for inspection use cases
8. Performance test with `show_locals=True` for large objects
