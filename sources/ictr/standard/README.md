# ictr.standard

Standard flavors, printers, and textualizers for ictr.

## Modules

- `flavors.py` — Standard flavor specifications (note, error, success, etc.)
- `printers.py` — Default printer with ANSI handling and TTY detection
- `compositors.py` — Compositor factories for record-to-text transformation
- `introducers.py` — Prefix generation with interpolation support
- `linearizers.py` — Content-to-lines conversion for messages and exceptions
- `core.py` — Shared data structures (Auxiliaries, Style, enums)
- `presentations.py` — Presentation strategies (Plaintext, JSON, Markdown)
- `renderables.py` — Renderable protocols (Dictionary, JSON, Markdown)

## Rich Integration

The standard subpackage automatically detects and uses the Rich library when
available. When Rich is not installed, it falls back to plain text formatting.

- **Colorization**: ANSI sequences are preserved for TTY output, stripped for
  non-TTY targets. Respects `NO_COLOR` environment variable.
- **Column constraints**: `ColumnsConstraints` enum controls wrapping behavior
  (`Complect` for fold/wrap, `Exceed` for overflow).
- **Incision boundaries**: `IncisionBoundaries` enum controls where line breaks
  occur (`Wordsplits`, `Whitespace`, `Anywhere`).

## Auxiliaries

The `Auxiliaries` dataclass provides injectable dependencies for testing:

- `pid_discoverer` — Returns current process ID
- `thread_discoverer` — Returns current thread
- `time_formatter` — Formats current time

Tests can inject mock implementations for deterministic output.

## Presentations

Presentations are external strategy objects for rendering content in different
formats:

- `PlaintextPresentation` — Default fallback, always matches
- `JsonPresentation` — JSON rendering with compact/indent options
- `MarkdownPresentation` — Markdown rendering with Rich support

Presentations are orthogonal to `LinearizerConfiguration` — they can be
swapped dynamically without reconfiguring the linearizer.
