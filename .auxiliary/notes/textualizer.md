# Textualizer Implementation Design

**Last Updated**: 2025-11-08

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

## Conditional Rich Integration Architecture

**Decision**: Use conditional Rich integration within single textualizer module rather than separate subpackage.

**Implementation approach**:
- Runtime detection: `_ENRICH` flag set based on Rich import success
- Function pairs: `_prepare_*_plain()` and `_prepare_*_rich()` for divergent behavior
- Dispatch pattern: Module-level function assignment based on `_ENRICH`
- Shared framing logic: Prefix handling, wrapping, detail separation identical between modes

**Rationale**:
- **Code reuse**: Framing logic (95% of code) shared between plain/rich modes
- **Maintainability**: Related logic stays together, changes visible side-by-side
- **Clear separation**: Function pairs make behavioral differences obvious
- **Graceful degradation**: Plain mode works without Rich dependency
- **Simple upgrade**: Installing Rich automatically enables enhanced rendering

**Alternative considered (rejected)**: Separate `sources/ictr/standard/` subpackage
- ❌ Would require duplicating or awkwardly importing framing logic
- ❌ Makes related code harder to maintain in sync
- ❌ Unclear boundary between "default" and "standard" textualizers

## TextualizerDefault - Unified Implementation

The default textualizer provides text rendering with automatic Rich integration when available. Plain mode strips ANSI and uses stdlib; Rich mode preserves ANSI and handles complex rendering.

### Design Principles

1. **Minimal required dependencies**: `wcwidth` (Unicode width), `textwrap` (stdlib)
2. **Optional Rich**: Auto-detected, enables enhanced rendering when available
3. **ANSI handling**: Stripped in plain mode, preserved in Rich mode
4. **Configurable behavior**: Enum-based configuration for precise control
5. **Graceful degradation**: Handles edge cases (no terminal width, very narrow terminals)

### Implementation Status

**Current** (2025-11-08):
- ✅ Configuration structure (`TextualizerConfiguration` + `TextualizerDefault`)
- ✅ `PrefixEmission` dataclass (text + visual width)
- ✅ Prefix rendering with emission metadata
- ✅ Summary rendering (initial line, core extraction)
- ✅ Visual width calculation (`_count_columns_visual` using wcwidth)
- ✅ Conditional Rich integration (`_ENRICH` flag, function pairs)
- ✅ Text wrapping (`_complect_text` using textwrap)
- 🚧 ANSI stripping in plain mode - needs integration
- 🚧 Summary subsequent lines (exception/object rendering) - in progress
- 🚧 Details rendering - TODO
- 🚧 Exception group handling - TODO
- 🚧 Truncate mode with visual width - TODO

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

**Implementation**: ANSI stripping + `wcwidth` (required dependency).

**Current implementation** (`_count_columns_visual`):
- Reuses existing `_printers.remove_ansi_c1_sequences()` for ANSI stripping
- Uses `wcwidth.wcswidth()` for proper Unicode width calculation
- Handles wide characters (CJK, emoji), combining characters correctly

**Known edge cases**:
- CSI ED/EL sequences: Matched by ANSI regex but may have unusual semantics if embedded mid-string (very rare in logging, typically used for terminal animations)

### ANSI Handling Strategy

**Decision**: Strip ANSI from message content in plain mode, preserve in Rich mode.

**Rationale**:
- **Avoids wrapping complexity**: Naive wrapping breaks ANSI state (colors bleed or disappear)
- **Clean separation**: Plain mode = plain text, Rich mode = full styling support
- **Clear upgrade path**: Users wanting ANSI in messages install Rich
- **Predictable behavior**: Mode determines capability, no surprises

**Implementation**:
- Plain mode (`not _ENRICH`): Strip ANSI from summary/details before wrapping
- Rich mode (`_ENRICH`): Preserve ANSI, use Rich's ANSI-aware wrapping
- Prefix ANSI: Always preserved (stripped only for width calculation)

See `.auxiliary/notes/snippets.md` for implementation code.

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
| Rich integration | Conditional within single module | Code reuse, maintainability, graceful degradation |
| Subpackage approach | Rejected | Would duplicate framing logic |
| **Width Calculation** | | |
| Implementation | ANSI strip + wcwidth (required) | Accurate, handles Unicode/wide chars |
| ANSI in prefix | Preserved (stripped for width only) | Visual appeal without breaking layout |
| **ANSI in Message Content** | | |
| Plain mode | Strip ANSI from summary/details | Avoids wrapping complexity |
| Rich mode | Preserve ANSI, use Rich wrapping | Full styling support |
| Upgrade path | Install Rich for ANSI in messages | Clear, simple |
| **Exception Handling** | | |
| Exception groups | Handle in textualizer (Option B) | Least surprise, flexibility for renderers |
| Nested groups | Preserve with indentation | Information preservation |
| Group member order | Before user details | Logical ordering |
| Sub-exception traces | Suppressed | Avoid excessive verbosity |
| Exception format | Template string (`{name}`, `{message}`) | Flexible, customizable |
| **Wrapping/Layout** | | |
| Wrapping control | `ColumnsConstraints` enum (Continue/Complect/Truncate) | Precise control |
| Incision boundaries | `IncisionBoundaries` enum (Nowhere/Whitespace/Wordsplits/Anywhere) | Fine-grained control |
| Prefix overflow | `prefix_incision_ratio` (float) | Intuitive (30% = prefix too large) |
| Truncate mode | Keep with visual width handling | Useful for fixed-width contexts |
| Detail marker | `detail_prefix` (first line only) | Clean continuation lines |
| Separator consistency | Same between all sections | Predictable, simple |

## Traceback Formatting

**Experiments**: See `.auxiliary/scribbles/traceback_experiments.py` and `traceback_findings.md`

### Key Findings

**stdlib limitations**:
- No built-in width constraint support in any traceback method
- Manual wrapping breaks structure (file paths split mid-line)
- `StackSummary` provides frame-level access but no width control
- `extract_stack()` works for non-exception stacks (inspection)

**Rich capabilities**:
- Full width constraint support via `Console(width=N)`
- Intelligent wrapping preserves structure even at narrow widths
- Can capture output as string with `console.capture()`
- Exception-focused (not designed for non-exception stacks)
- Output includes ANSI escape sequences

### Implementation Strategy

**Plain mode**: Custom compact formatting
- Walk traceback with `traceback.extract_tb()`
- Format frames manually: location, function, code line
- Truncate long paths from left: `"...file.py:123"`
- Handle chained exceptions recursively
- Width control via character counting/truncation

**Rich mode**: Use Rich Traceback
- Create `Traceback.from_exception()` with exception info
- Render via `Console` with width constraint
- Capture output with `console.capture()`
- Split into lines for integration
- Beautiful rendering with colors, boxes, syntax highlighting

See `.auxiliary/notes/snippets.md` for implementation code examples.

## Next Steps

**Immediate priorities** (in `sources/ictr/textualizers.py`):

1. **Integrate ANSI stripping in plain mode**
   - Add stripping to `_render_summary_core()` when `not _ENRICH`
   - Strip from details before wrapping

2. **Implement `_truncate_visual()` utility**
   - Handle wide characters with wcwidth
   - Add ellipsis indicator when truncating
   - Use for `ColumnsConstraints.Truncate` mode

3. **Complete `_render_summary_subsequent()`**
   - Exception rendering: call `_prepare_exception_lines_plain/rich`
   - Object rendering: call `_prepare_object_lines_plain/rich`
   - Prepend base_prefix and detail indent to each line

4. **Implement `_prepare_exception_lines_plain()`**
   - Walk traceback frames with `traceback.extract_tb()`
   - Format with width constraints (truncate paths if needed)
   - Handle chained exceptions (`__cause__`, `__context__`)

5. **Implement `_render_details()`**
   - Detail prefix application (first line only)
   - Wrapping based on `ColumnsConstraints` and `IncisionBoundaries`
   - Truncation if `details_max` specified
   - Proper indentation alignment

6. **Add exception group support**
   - Detect `BaseExceptionGroup` in summary
   - Extract group members with nesting preservation
   - Format using `exception_format` template
   - Integrate with user details

7. **Set up dispatch pattern**
   - Module-level function assignment based on `_ENRICH`
   - Clean call sites without runtime checks

**Testing priorities**:
- Various terminal widths (40, 60, 80, 120, unlimited)
- ANSI codes in prefix, summary, details
- Unicode characters (wide chars, emoji, combining chars)
- Exceptions (chained, nested, groups)
- Empty values, edge cases
