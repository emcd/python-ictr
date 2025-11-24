# Terminal Width Detection

**Date**: 2025-12-13

## Question

How should we detect terminal width when a TTY is attached? Should we use:
1. Signal handler for `SIGWINCH` with cached value?
2. Computed property that checks on every access?
3. Hybrid with lazy cache and expiry?

## Analysis

### Option 1: Signal Handler (`SIGWINCH`)

**Pros**:
- Immediate response to terminal resize
- Updates cached value automatically
- Good for long-running processes that continuously output

**Cons**:
- Signal handlers are global/process-wide (hard to scope)
- Race conditions if handler fires during output
- Complexity: need thread-safe cache invalidation
- **Not portable to Windows** (no `SIGWINCH`)
- Overkill for typical logging use cases

**When it matters**:
- Interactive TUI applications
- Long-running daemons with continuous output
- Real-time monitoring tools

### Option 2: Computed Property (Check on Access)

**Pros**:
- Simple, no global state
- Thread-safe by default (each call is independent)
- Portable (works on Windows)
- Always accurate at time of use
- No race conditions

**Cons**:
- Slight overhead on every access (syscall each time)
- Could be inefficient if accessed in tight loops

**When it matters**:
- Typical logging/debugging libraries (like ictr!)
- Batch processing
- CLI tools

### Option 3: Lazy Cached Property (Hybrid)

**Pros**:
- Cache for performance
- Refresh on explicit invalidation or time-based expiry
- No signal complexity
- Still simple

**Cons**:
- Might be stale for a bit
- Need expiry policy (time-based? access-count?)

## Recommendation for ictr

**Use a computed property** (Option 2) with an **optional cached value override**.

### Rationale

1. **ictr is a logging/debugging library**, not a TUI. Users call it intermittently, not in tight loops.

2. **Terminal resizes are rare** during the lifetime of a single log message - the window from "construct control" to "render message" is milliseconds.

3. **Simplicity wins**: No signals, no threads, no races, no platform issues.

4. **Performance is fine**: `shutil.get_terminal_size()` is a single `ioctl` syscall (~microseconds). Not a bottleneck.

5. **Let users opt into caching** if they want: `TextualizerControl(columns_count=80)` explicitly sets a fixed width.

### Implementation

Python's `shutil.get_terminal_size()` handles terminal width detection cleanly without needing `termios`:

```python
import os
import shutil

def get_tty_width(fd: int = 1) -> int | None:
    """Get terminal width for file descriptor (0=stdin, 1=stdout, 2=stderr).

    Returns:
        Terminal width in columns, or None if not a TTY.
    """
    if not os.isatty(fd):
        return None

    try:
        size = shutil.get_terminal_size(fd)
        return size.columns
    except (AttributeError, ValueError, OSError):
        return None
```

**Key points**:
- `shutil.get_terminal_size()` handles `TIOCGWINSZ` ioctl internally
- Works on Unix and Windows
- Pass `fd` argument to query specific streams (stdout vs stderr)
- Gracefully returns `None` for non-TTY streams
- No need for `termios` or `fcntl` unless you need to *set* terminal properties

### Suggested API Design

```python
@dataclass
class TextualizerControl:
    stream: io.TextIOBase
    charset: str | None = None
    colorize: bool = True
    _columns_count_override: int | None = None  # Private, explicit cache

    @property
    def columns_count(self) -> int | None:
        """Terminal width in columns, or None if not a TTY.

        Checks terminal size each time unless explicitly overridden.
        """
        if self._columns_count_override is not None:
            return self._columns_count_override

        if not hasattr(self.stream, 'fileno'):
            return None

        try:
            if not os.isatty(self.stream.fileno()):
                return None
            size = shutil.get_terminal_size(self.stream.fileno())
            return size.columns
        except (AttributeError, ValueError, OSError):
            return None
```

### Usage Examples

```python
# Normal usage - checks every time (fresh)
control = TextualizerControl(sys.stdout)
width = control.columns_count  # Checks TTY on each access

# Explicit override for testing or fixed-width contexts
control = TextualizerControl(sys.stdout, _columns_count_override=80)
width = control.columns_count  # Returns 80, no syscall

# Long-running processes can snapshot at creation if desired
snapshot_width = shutil.get_terminal_size().columns if sys.stdout.isatty() else None
control = TextualizerControl(sys.stdout, _columns_count_override=snapshot_width)
```

## When You'd Want SIGWINCH

If ictr ever grows an **interactive mode** (like a TUI for filtering/exploring logs), *then* add `SIGWINCH`. But for the current use case? YAGNI.

**Exception**: If building a **long-running daemon** that logs continuously over hours/days, users might appreciate resize handling. But even then, make it opt-in:

```python
# Hypothetical future API
with Reporter.auto_resize_terminal():
    # Within this context, SIGWINCH handler is active
    ...
```

## Decision

**Property-based, no signal handler.** Simple, correct, fast enough. Can always add `SIGWINCH` later if users request it.
