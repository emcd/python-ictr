# Textualizer Implementation Design

**Last Updated**: 2025-11-03

This document captures the design decisions, rationale, and implementation details for the textualizer system in ictr v2.

## Overview

Textualizers are responsible for converting `Record` objects into formatted text strings suitable for display on text terminals or log files. The textualizer owns the entire message frame composition, including prefix generation and body rendering.

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

The default textualizer provides straightforward text rendering without external dependencies (beyond stdlib). It makes simplifying assumptions suitable for basic use cases.

### Design Principles

1. **Minimal dependencies**: No third-party packages (textwrap from stdlib is fine)
2. **ASCII-focused**: Assumes "unadorned" ASCII text in messages for width calculations
3. **Configurable behavior**: Attributes control wrapping, spacing, and formatting details
4. **Graceful degradation**: Handles edge cases (no terminal width, very narrow terminals, etc.)

### Configuration Attributes

```python
class TextualizerDefault( Textualizer ):
    ''' Simple textualizer for basic text output. '''

    prefix_emitter: PrefixEmitterUnion = 'ictr| '

    # Wrapping behavior
    wrap_text: bool = True
    wrap_at_words: bool = True  # True = word boundaries, False = hard wrap

    # Spacing and separators
    detail_separator: str = '\n\n'  # Between each detail
    detail_marker: str = ''  # Optional prefix for details (e.g., '• ', '- ')

    # Overflow handling
    combined_overflow_threshold: float = 0.8  # Fraction of width triggering separation

    # Exception formatting
    exception_include_type: bool = True  # "ValueError: msg" vs just "msg"

    # Truncation
    max_detail_lines: Optional[int] = None  # Truncate long details (None = no limit)

    # Fallback behavior
    fallback_width: Optional[int] = None  # Width when columns_count is None
```

#### Attribute Details

**`prefix_emitter: PrefixEmitterUnion`**
- String literal or callable that produces prefix
- Default: `'ictr| '`
- Callable signature: `(mname: str, flavor: Flavor) -> str`
- Allows customization without subclassing

**`wrap_text: bool`**
- Master switch for wrapping behavior
- `True` (default): Wrap text to fit terminal width
- `False`: Output everything on single lines regardless of width
- Useful for logs that will be post-processed or piped

**`wrap_at_words: bool`**
- Controls word-boundary vs character-boundary wrapping
- `True` (default): Uses `textwrap` module for clean breaks
- `False`: Simple string slicing, faster but can break mid-word

**`detail_separator: str`**
- How to separate multiple details
- Default: `'\n\n'` (blank line between details)
- Alternatives: `'\n'` (compact), `'\n---\n'` (visual divider)

**`detail_marker: str`**
- Prepended to first line of each detail (after indent)
- Default: `''` (no marker, clean look)
- Examples: `'• '`, `'- '`, `'→ '` for bulleted lists
- Applied to first line only, not to wrapped continuation lines

**`combined_overflow_threshold: float`**
- Fraction of terminal width (0.0 to 1.0)
- If `len(prefix) + len(summary) > width * threshold`, put summary on new line
- Default: `0.8` (leaves breathing room)
- `1.0`: Only separate when they literally don't fit together
- Prevents cramped appearance when prefix+summary are close to width limit

**`exception_include_type: bool`**
- When `MessageSummary` is an `Exception`:
  - `True` (default): `"ValueError: invalid input"`
  - `False`: `"invalid input"`
- Most users expect to see exception type

**`max_detail_lines: Optional[int]`**
- Maximum lines to render per detail
- `None` (default): No truncation
- Protects against accidentally logging huge objects
- Truncation happens at textualizer level (can insert "... truncated" message)
- Printer-level truncation would be awkward (mid-frame cuts)

**`fallback_width: Optional[int]`**
- Width to assume when `control.columns_count is None`
- `None` (default): Don't wrap, output as single lines
- Numeric values (80, 120, etc.): Assume this width for wrapping
- Useful for non-TTY contexts where readable output still desired

### Visual Width Calculation

For the simple/default implementation, we use **character count** rather than true visual width. This means:

- ANSI color codes are counted in the length (not ideal but acceptable for default)
- Unicode combining characters not handled specially
- Emoji and wide characters treated as single width

**Rationale**: Keeps implementation simple and avoids dependencies. The `standard` subpackage textualizer (Sundae port) will handle this properly using Rich's width calculation or dedicated libraries.

**Known limitation**: If prefix contains ANSI codes, indentation may be slightly off-center. Acceptable for default implementation.

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

### Implementation Sketch

```python
def __call__(
    self, control: _printers.TextualizerControl, record: _records.Record
) -> str:
    """Renders a record as formatted text."""
    content = record.content

    # Determine effective width
    width = control.columns_count or self.fallback_width

    # Render prefix
    prefix = self._render_prefix(record)
    prefix_len = len(prefix)  # Character count (simple implementation)

    # Handle exception groups
    if isinstance(content.summary, BaseExceptionGroup):
        summary_text = self._render_exception_group_summary(content.summary)
        group_details = self._extract_exception_group_details(content.summary)
        all_details = group_details + list(content.details)
    else:
        summary_text = self._render_summary(content.summary)
        all_details = list(content.details)

    # Check if we need to separate prefix and summary
    needs_separation = False
    if width and self.wrap_text:
        combined_len = prefix_len + len(summary_text)
        threshold_len = int(width * self.combined_overflow_threshold)
        needs_separation = combined_len > threshold_len

    # Render summary lines
    if needs_separation:
        # Summary on new line, no indent
        summary_lines = self._wrap_text_lines(
            summary_text, width, '', ''
        )
        lines = [prefix] + summary_lines
    else:
        # Summary continues after prefix
        indent = ' ' * prefix_len
        summary_lines = self._wrap_text_lines(
            summary_text, width, prefix, indent
        )
        lines = summary_lines

    # Render details
    for detail in all_details:
        # Apply detail marker to first line only
        detail_text = (
            self.detail_marker + detail if self.detail_marker else detail
        )
        indent_str = ' ' * prefix_len

        # Wrap detail
        detail_lines = self._wrap_text_lines(
            detail_text, width, indent_str, indent_str
        )

        # Truncate if needed
        if self.max_detail_lines and len(detail_lines) > self.max_detail_lines:
            detail_lines = detail_lines[:self.max_detail_lines]
            detail_lines.append(
                indent_str + f"... ({len(detail_lines) - self.max_detail_lines} more lines truncated)"
            )

        # Add separator before detail
        if self.detail_separator:
            lines.append('')  # Blank line (if separator includes \n\n)
        lines.extend(detail_lines)

    return '\n'.join(lines)


def _render_prefix(self, record: _records.Record) -> str:
    """Renders the prefix for this record."""
    if isinstance(self.prefix_emitter, str):
        return self.prefix_emitter
    # Callable prefix emitter
    return self.prefix_emitter(record.address, record.flavor)


def _render_summary(self, summary: _records.MessageSummary) -> str:
    """Converts summary (str or Exception) to display text."""
    if isinstance(summary, BaseExceptionGroup):
        # Should not reach here (handled in __call__)
        return self._render_exception_group_summary(summary)
    elif isinstance(summary, Exception):
        if self.exception_include_type:
            exc_type = type(summary).__name__
            exc_msg = str(summary)
            return f"{exc_type}: {exc_msg}" if exc_msg else exc_type
        else:
            return str(summary)
    return summary


def _render_exception_group_summary(
    self, group: BaseExceptionGroup
) -> str:
    """Renders summary line for exception group."""
    exc_type = type(group).__name__
    message = str(group.message) if hasattr(group, 'message') else str(group)
    count = len(group.exceptions)
    plural = "exception" if count == 1 else "exceptions"
    return f"{exc_type}: {message} ({count} {plural})"


def _extract_exception_group_details(
    self,
    group: BaseExceptionGroup,
    indent_level: int = 0,
) -> list[str]:
    """Extracts exception group members as detail strings.

    Preserves nesting structure through indentation.
    Recursively processes nested exception groups.
    """
    details = []
    indent = '  ' * indent_level  # 2 spaces per nesting level

    for exc in group.exceptions:
        if isinstance(exc, BaseExceptionGroup):
            # Nested group: render summary and recurse
            exc_type = type(exc).__name__
            message = str(exc.message) if hasattr(exc, 'message') else str(exc)
            count = len(exc.exceptions)
            plural = "exception" if count == 1 else "exceptions"
            details.append(f"{indent}{exc_type}: {message} ({count} {plural})")

            # Recursively extract nested exceptions
            nested = self._extract_exception_group_details(exc, indent_level + 1)
            details.extend(nested)
        else:
            # Regular exception: render as detail
            exc_type = type(exc).__name__
            exc_msg = str(exc)
            detail = f"{indent}{exc_type}: {exc_msg}" if exc_msg else f"{indent}{exc_type}"
            details.append(detail)

    return details


def _wrap_text_lines(
    self,
    text: str,
    width: Optional[int],
    initial_indent: str,
    subsequent_indent: str,
) -> list[str]:
    """Wraps text into lines, respecting width and indentation.

    Args:
        text: The text to wrap.
        width: Maximum line width (None = no wrapping).
        initial_indent: Indent for first line.
        subsequent_indent: Indent for continuation lines.

    Returns:
        List of wrapped lines (including indentation).
    """
    if not self.wrap_text or width is None:
        return [initial_indent + text]

    if self.wrap_at_words:
        import textwrap
        return textwrap.wrap(
            text,
            width=width,
            initial_indent=initial_indent,
            subsequent_indent=subsequent_indent,
            break_long_words=False,
            break_on_hyphens=False,
        )
    else:
        # Simple hard wrap at character boundary
        lines = []
        remaining = text
        first = True

        while remaining:
            indent = initial_indent if first else subsequent_indent
            available = width - len(indent)

            if available <= 0:
                # Pathological case: indent longer than width
                # Take at least 1 character to avoid infinite loop
                chunk_size = max(1, width - len(indent))
                lines.append(indent + remaining[:chunk_size])
                remaining = remaining[chunk_size:]
            else:
                lines.append(indent + remaining[:available])
                remaining = remaining[available:]

            first = False

        return lines if lines else [initial_indent]
```

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
| Prefix location | Merged into textualizer | Better cohesion, simpler architecture |
| Exception groups | Handle in textualizer (Option B) | Least surprise, flexibility for different renderers |
| Nested groups | Preserve with indentation | Information preservation over pure readability |
| Group member order | Before user details | Logical: group contents first, then context |
| Sub-exception traces | Suppressed | Avoid excessive verbosity |
| Width calculation (default) | Character count | Simple, no dependencies |
| Width calculation (standard) | Visual width via Rich | Accurate, handles ANSI/Unicode |
| Detail truncation | At textualizer level | Intelligent handling vs awkward mid-frame cuts |
| `combined_overflow_threshold` | Float (fraction) | Flexible across terminal sizes |
| `detail_marker` application | First line only | Clean continuation line appearance |
| `wrap_text` scope | Both summary and details | Consistent behavior, simpler config |

## Open Questions

1. Should `exception_include_type=False` for empty exception messages show `repr()` or empty string?
2. Do we want a `verbose` mode that includes more metadata (timestamp, module, etc.) even in default textualizer?
3. Should very narrow terminals (< 40 cols?) trigger a different rendering strategy entirely?

## Implementation Phases

1. **Phase 1**: Basic rendering without exception groups
   - Prefix rendering
   - Summary wrapping with overflow detection
   - Detail rendering with separators
   - Test with various terminal widths

2. **Phase 2**: Exception group support
   - Summary rendering for groups
   - Detail extraction with nesting
   - Integration with user details
   - Edge case handling

3. **Phase 3**: Truncation and polish
   - `max_detail_lines` implementation
   - Edge case handling (empty values, narrow terminals)
   - Performance optimization if needed

4. **Phase 4**: Sundae migration (separate effort)
   - `sources/ictr/standard/` subpackage
   - Rich-based textualizer
   - Template interpolation
   - Color gradients and styling
