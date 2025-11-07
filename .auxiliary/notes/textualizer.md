# Textualizer Implementation Design

**Last Updated**: 2025-11-06

This document captures the design decisions, rationale, and implementation details for the textualizer system in ictr v2.

## Overview

Textualizers are responsible for converting `Record` objects into formatted
text strings suitable for display on text terminals or log files. The
textualizer owns the entire message frame composition, including prefix
generation and body rendering.

## Architecture Decision: Prefix Integration

**Decision**: Merge prefix generation into the textualizer (not a separate component).

**Rationale**:
- In v1, separation was forced by `IceCreamDebugger`'s structure (external constraint)
- In v2, textualizer owns the entire message frame (prefix + body)
- Better cohesion: prefix and body interact (wrapping, alignment, multiline)
- Simpler architecture: one component, clear responsibility
- More flexible: holistic formatting decisions

**Implementation**:
- `Textualizer._render_prefix()` - internal method for prefix rendering
- `FlavorConfiguration` stores prefix **data** (template, colors, etc.), not callables
- Sundae prefix logic becomes part of standard textualizer in `sources/ictr/standard/`

## TextualizerDefault - Simple Implementation

The default textualizer provides straightforward text rendering with minimal dependencies. Uses ANSI-stripping for width calculation and optional `wcwidth` for Unicode support.

### Design Principles

1. **Minimal dependencies**: `wcwidth` (optional, for Unicode width), `textwrap` (stdlib)
2. **ANSI-aware**: Strips ANSI escape sequences for accurate visual width calculation
3. **Configurable behavior**: Enum-based configuration for precise control
4. **Graceful degradation**: Handles edge cases (no terminal width, very narrow terminals)

### Implementation Status

**Current** (2025-11-06):
- ✅ Configuration structure (`TextualizerConfiguration` + `TextualizerDefault`)
- ✅ `PrefixEmission` dataclass (text + visual width)
- ✅ Prefix rendering with emission metadata
- ✅ Summary rendering (initial line, core extraction)
- 🚧 Summary subsequent lines (wrapping logic) - in progress
- 🚧 Details rendering - TODO
- 🚧 Exception group handling - TODO
- 🚧 Visual width calculation utility - TODO

### Configuration Structure

Configuration extracted into separate `TextualizerConfiguration` dataclass:

```python
@__.immut.dataclass
class TextualizerConfiguration:
    ''' Configuration for textualizer behavior. '''

    # Column constraints
    columns_constraint: ColumnsConstraints = ColumnsConstraints.Continue
    columns_count: Optional[int] = None

    # Prefix and indentation
    base_prefix: str = ''

    # Detail formatting
    detail_prefix: str = ''
    details_separator: str = '\n\n'
    details_max: Optional[int] = None  # Truncation limit

    # Exception formatting
    exception_format: str = '[{name}] {message}'

    # Wrapping behavior
    incision_boundary: IncisionBoundaries = IncisionBoundaries.Wordsplits
    prefix_incision_ratio: float = 0.3

@__.immut.dataclass
class TextualizerDefault( Textualizer ):
    ''' Simple textualizer with minimal dependencies. '''

    configuration: TextualizerConfiguration = __.dcls.field(
        default_factory = TextualizerConfiguration )
    prefix_emitter: PrefixEmitterUnion = 'ictr| '
```

### Configuration Enums

**`ColumnsConstraints`** - How to handle column width limits:
- `Continue` - Ignore width, output on single lines (no wrapping)
- `Complect` - Fold/wrap text to fit within width
- `Truncate` - Cut text at width boundary

**`IncisionBoundaries`** - Where to break lines when wrapping:
- `Anywhere` - Break at any character (hard wrap)
- `Wordsplits` - Break at word boundaries (default)
- `Whitespace` - Break only at whitespace

### Key Attributes

**`prefix_emitter: PrefixEmitterUnion`**
- String literal or callable that produces prefix
- Callable signature: `(control: TextualizerControl, record: Record) -> str`
- Much better than original `(mname: str, flavor: Flavor)` - full context access

**`prefix_incision_ratio: float`**
- Fraction of width (0.0-1.0) - if prefix exceeds this, put summary on new line
- Default: `0.3` (30% of width)
- Better than `combined_overflow_threshold` - more intuitive

**`exception_format: str`**
- Template string with `{name}` and `{message}` placeholders
- Default: `'[{name}] {message}'`
- Flexible: `'{message}'` (untyped), `'{name}: {message}'` (Python-style), etc.
- Much better than `exception_include_type: bool`

**`details_separator: str`**
- Separator between summary and first detail, and between subsequent details
- Default: `'\n\n'` (blank line)
- Intentionally consistent (not different separator for first vs subsequent)

### Visual Width Calculation

**Decision**: Use regex-based ANSI stripping + optional `wcwidth` for Unicode.

**Implementation approach**:
- Regex pattern to strip ANSI escape sequences: `\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])`
- Then measure remaining text with `len()` or `wcwidth.wcswidth()` if available
- No Rich dependency for default textualizer (save for `standard/` subpackage)

**Benefits**:
- Handles ANSI color codes correctly (common in prefixes)
- Lightweight `wcwidth` package (single file, no dependencies) handles Unicode width
- No external dependencies if `wcwidth` unavailable (falls back to simple `len()`)

**Known edge cases**:
- CSI ED/EL sequences (clear display/line): Matched by regex but may have unusual semantics if embedded mid-string (very rare in logging)
- Without `wcwidth`: Emoji and wide characters counted as single width (acceptable fallback)

**Utility function** (to be implemented):
```python
import re as _re

_ANSI_ESCAPE_PATTERN = _re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def _calculate_visual_width(text: str) -> int:
    """Calculate visual width excluding ANSI sequences.

    Uses wcwidth if available for proper Unicode width handling.
    Falls back to len() for simple character counting.
    """
    stripped = _ANSI_ESCAPE_PATTERN.sub('', text)
    try:
        import wcwidth
        width = wcwidth.wcswidth(stripped)
        return width if width >= 0 else len(stripped)
    except ImportError:
        return len(stripped)
```

### Exception Group Handling

**Decision**: Handle `ExceptionGroup` expansion at the **textualizer level** (Option B).

**Rationale**:
- **Principle of Least Surprise**: Explicitly converting exceptions into details at Reporter level would be surprising
- **Flexibility**: Textualizers and structured printers choose their own rendering strategy
- **Utility availability**: We provide helper functions for common expansion patterns
- **Structured printer control**: JSON/database printers can handle groups differently than text printers

#### Rendering Strategy for TextualizerDefault

When `MessageSummary` is a `BaseExceptionGroup`:

1. **Summary line**: Render the group itself with count
   - Format: `"{ExceptionType}: {message} ({count} exceptions)"`
   - Example: `"ExceptionGroup: validation errors (3 exceptions)"`

2. **Group exceptions as implicit details**: Render each sub-exception before user-provided details
   - Preserves logical order: group members first, then additional context
   - Format each: `"{ExceptionType}: {message}"`
   - No tracebacks for sub-exceptions (avoid verbosity)

3. **Nested groups**: Preserve nesting structure with indentation
   - Shows hierarchical relationships
   - Prevents information loss (each group's message preserved)
   - Format: Indent nested group members with 2 additional spaces

4. **User details**: Render after all group exceptions
   - Clear separation: what came from the exception vs what user added

#### Example Output

```python
try:
    raise ExceptionGroup("outer", [
        ValueError("error 1"),
        ExceptionGroup("inner", [
            KeyError("error 2a"),
            TypeError("error 2b"),
        ]),
        RuntimeError("error 3"),
    ])
except ExceptionGroup as eg:
    reporter(eg, "Additional context", "More info")
```

**Rendered output**:
```
ictr| ExceptionGroup: outer (3 exceptions)
      ValueError: error 1
      ExceptionGroup: inner (2 exceptions)
        KeyError: error 2a
        TypeError: error 2b
      RuntimeError: error 3

      Additional context

      More info
```

#### Utility Function for Callers

For callers who want explicit control over exception group expansion:

```python
def expand_exception_group(
    group: BaseExceptionGroup,
    flatten: bool = False,
) -> tuple[str, tuple[str, ...]]:
    """Expands exception group into summary and detail strings.

    Args:
        group: The exception group to expand.
        flatten: If True, flatten nested groups completely.
                 If False, preserve nesting structure.

    Returns:
        Tuple of (summary_text, details_tuple).

    Example:
        summary, details = expand_exception_group(eg)
        reporter(summary, *details)
    """
    ...
```

This allows callers to pre-process exception groups if they want different behavior than the textualizer's default.

### Current Implementation Structure

The implementation in `sources/ictr/textualizers.py` follows this structure:

```python
def __call__(
    self, control: _printers.TextualizerControl, record: _records.Record
) -> str:
    """Renders a record as formatted text."""
    configuration = self.configuration

    # Render prefix with visual width metadata
    prefix = self._render_prefix(control, record)

    # Render summary (initial + subsequent lines)
    summary_initial = self._render_summary_initial(
        configuration, prefix, record.content.summary)
    summary_subsequent = self._render_summary_subsequent(
        configuration, prefix, record.content.summary)

    # Render details (TODO)
    details = self._render_details(
        configuration, prefix, record.content.details)

    # Combine with separator
    return configuration.details_separator.join((
        summary_initial, *summary_subsequent, *details))
```

**Key implementation features**:
- `PrefixEmission` dataclass captures both text and visual width
- Prefix emission happens once, metadata reused for indentation decisions
- Summary split into initial (first line) and subsequent (wrapped lines)
- Configuration separation allows easy sharing/reuse

### Edge Cases

**Empty details tuple**
- Render summary only, no detail separator lines
- Output: Just prefix + summary

**Empty summary string**
- Render blank prefix line
- Continue with details if provided
- Output: `"ictr| \n      detail1\n\n      detail2"`

**No columns_count and no fallback_width**
- Disable wrapping completely
- Output everything on single lines (may exceed terminal width)

**Very narrow terminal** (columns_count < prefix length)
- Wrap even the prefix if necessary
- Place summary on separate line (no indent)
- Details also get no indent (terminal too narrow for it)

**Exception with empty message**
- If `exception_include_type=True`: Show just type name
- If `exception_include_type=False`: Show empty string (or use `repr()`?)

**ExceptionGroup with no exceptions**
- Treat as regular exception, no detail expansion
- Output: `"ExceptionGroup: message"`

## Standard Textualizer (Sundae Port)

The standard textualizer in `sources/ictr/standard/textualizers.py` will provide:

- **Rich integration**: Uses `rich.console.Console` for rendering
- **Proper visual width**: ANSI codes excluded from width calculations
- **Color support**: Full color palette with gradients for trace levels
- **Template-based prefixes**: Interpolation with timestamp, PID, thread, module
- **Proper Unicode handling**: Emoji, combining characters, wide characters

See `.auxiliary/notes/migration.md` for details on Sundae migration plan.

## Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Architecture** | | |
| Prefix location | Merged into textualizer | Better cohesion, simpler architecture |
| Configuration structure | Separate `TextualizerConfiguration` dataclass | Reusable, composable, clean separation |
| **Width Calculation** | | |
| Default approach | Regex ANSI strip + optional wcwidth | Handles common case (ANSI), lightweight |
| Standard approach | Rich visual width | Full Unicode support (emoji, wide chars) |
| **Exception Handling** | | |
| Exception groups | Handle in textualizer (Option B) | Least surprise, flexibility for renderers |
| Nested groups | Preserve with indentation | Information preservation |
| Group member order | Before user details | Logical ordering |
| Sub-exception traces | Suppressed | Avoid excessive verbosity |
| Exception format | Template string (`{name}`, `{message}`) | Flexible, customizable |
| **Wrapping/Layout** | | |
| Wrapping control | `ColumnsConstraints` enum (Continue/Complect/Truncate) | Precise control |
| Incision boundaries | `IncisionBoundaries` enum (Anywhere/Wordsplits/Whitespace) | Fine-grained control |
| Prefix overflow | `prefix_incision_ratio` (float) | Intuitive (30% = prefix too large) |
| Detail truncation | At textualizer level (`details_max`) | Intelligent handling vs mid-frame cuts |
| Detail marker | `detail_prefix` (first line only) | Clean continuation lines |
| Separator consistency | Same between all sections | Predictable, simple |

## Next Steps

**Immediate priorities** (in `sources/ictr/textualizers.py`):

1. **Implement `_calculate_visual_width()` utility**
   - ANSI escape sequence stripping via regex
   - Optional wcwidth integration
   - Use in prefix rendering and width calculations

2. **Complete `_render_summary_subsequent()`**
   - Wrapping logic based on `ColumnsConstraints` and `IncisionBoundaries`
   - Respect `prefix_incision_ratio` for overflow detection
   - Handle continuation line indentation

3. **Implement `_render_details()`**
   - Detail prefix application (first line only)
   - Wrapping with proper indentation
   - Truncation if `details_max` specified

4. **Add exception group support**
   - Detect `BaseExceptionGroup` in summary
   - Extract group members with nesting preservation
   - Format using `exception_format` template
   - Integrate with user details

5. **Edge case handling and testing**
   - Empty summary/details
   - Very narrow terminals
   - ANSI codes in various positions
   - Unicode characters with wcwidth

**Future work**:
- Sundae migration to `sources/ictr/standard/` subpackage
- Rich-based textualizer with full Unicode support
- Template-based prefix interpolation
- Color gradients and styling
