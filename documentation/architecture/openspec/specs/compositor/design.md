# Compositor Design

## Prefix Integration

Prefix generation is merged into the compositor rather than being a separate
component. This provides better cohesion since prefix and body interact
(wrapping, alignment, multiline). The compositor owns the entire message
frame: introduction prefix + content body.

`FlavorConfiguration` stores prefix **data** (template, colors, etc.), not
callables. The standard prefix logic lives in `sources/ictr/standard/`.

## Conditional Rich Integration

Rich integration uses a conditional pattern within a single module rather than
separate subpackages:

- **Runtime detection**: `_ENRICH` flag set based on Rich import success
- **Function pairs**: `_prepare_*_plain()` and `_prepare_*_rich()` for
  divergent behavior
- **Dispatch pattern**: Module-level function assignment based on `_ENRICH`
- **Shared framing logic**: Prefix handling, wrapping, detail separation
  identical between modes

This approach maximizes code reuse (95% of framing logic is shared), keeps
related logic together for maintainability, and provides graceful degradation
when Rich is unavailable.

## Configuration

### Enums

**`ColumnsConstraints`** — How to handle column width limits:
- `Complect` — Fold/wrap text to fit within width
- `Exceed` — Overflow without wrapping

**`IncisionBoundaries`** — Where to break lines when wrapping:
- `Nowhere` — No line breaks
- `Whitespace` — Break at horizontal spaces and tabs
- `Wordsplits` — Break at hyphens + whitespace
- `Anywhere` — Break at any character

### Key Fields

**`prefix_incision_ratio: float`** — Fraction of width (0.0–1.0). If prefix
exceeds this ratio, the summary goes on a new line. Default: `0.3`.

**`exception_format: str`** — Template with `{name}` and `{message}`
placeholders. Default: `'[ {name} ] {message}'`. Flexible: `'{message}'`
(untyped), `'{name}: {message}'` (Python-style), etc.

**`details_separator: str`** — Separator between summary and details, and
between subsequent details. Default: `'\n\n'`.

## ANSI Handling

**Plain mode** (`not _ENRICH`): Strip ANSI from summary/details before
wrapping. Avoids wrapping complexity where naive wrapping breaks ANSI state.

**Rich mode** (`_ENRICH`): Preserve ANSI, use Rich's ANSI-aware wrapping.
Full styling support.

**Prefix ANSI**: Always preserved (stripped only for width calculation).

The upgrade path is simple: install Rich for ANSI in messages.

## Visual Width Calculation

Uses ANSI stripping + `wcwidth` for proper Unicode width calculation. Handles
wide characters (CJK, emoji), combining characters correctly. The
`_count_columns_visual` function reuses `_printers.remove_ansi_c1_sequences()`
for ANSI stripping and `wcwidth.wcswidth()` for width.

## Exception Group Handling

Exception groups (`BaseExceptionGroup`) are handled at the compositor level
(not the reporter level). This follows the principle of least surprise —
reporters don't implicitly convert exceptions into details.

### Rendering Strategy

1. **Summary line**: Render the group itself with count
   - Format: `"{ExceptionType}: {message} ({count} exceptions)"`
2. **Group exceptions as implicit details**: Each sub-exception rendered
   before user-provided details, preserving nesting with indentation
3. **User details**: Rendered after all group exceptions

### Example Output

```
ictr| ExceptionGroup: outer (3 exceptions)
      ValueError: error 1
      ExceptionGroup: inner (2 exceptions)
        KeyError: error 2a
        TypeError: error 2b
      RuntimeError: error 3

      Additional context
```

## Traceback Formatting

### Plain Mode

Custom compact formatting using `traceback.extract_tb()`:
- Walk traceback frames manually
- Format: location (file:line), function name, code line
- Truncate long paths from left: `"...file.py:123"`
- Handle chained exceptions (`__cause__`, `__context__`) recursively

### Rich Mode

Use `rich.traceback.Traceback.from_exception()` with `Console(width=N)`:
- Full width constraint support
- Intelligent wrapping preserves structure even at narrow widths
- Beautiful rendering with colors, boxes, syntax highlighting
- Capture output with `console.capture()`

### Inspection Stacks

For non-exception stack traces (inspection/debugging), manual `Trace`
construction works with Rich:
- Convert `traceback.extract_stack()` to Rich `Frame` objects
- Wrap in `Stack` → `Trace` → `Traceback`
- Same rendering as exceptions

## Edge Cases

- **Empty details tuple**: Render summary only, no detail separator
- **Empty summary string**: Render blank prefix line, continue with details
- **No columns_count**: Disable wrapping, single lines
- **Very narrow terminal** (columns_count < prefix length): Wrap prefix,
  summary on separate line
- **Exception with empty message**: Show type name only
- **ExceptionGroup with no exceptions**: Treat as regular exception
