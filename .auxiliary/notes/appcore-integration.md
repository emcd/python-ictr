# ICTR Renderables Integration - Remaining Work

## Overview

This document tracks remaining work for `ictr` renderables integration with `appcore`.

**Goal**: Enable objects to control their rendering through protocols, supporting CLI display needs while keeping `ictr` focused on terminal/log output.

**Status**: Phase 1 complete (linearizers refactored and exported). Phase 2 in progress (protocols partially implemented, pending appcore validation).

## Current Status

### ✅ Completed (as of 1.0a1)

**Phase 1 - Linearizer Refactoring**:
- `LinearizerConfiguration` and `LinearizerState` implemented
- `CompositorState` refactored to compose `LinearizerState`
- Linearizers exported publicly from `ictr.standard`

**Phase 2 - Protocols (Partial)**:
- ✅ `DictionaryRenderable` protocol implemented in `ictr/renderables.py`
- ✅ `MarkdownRenderable` protocol skeleton implemented (signature under review)

---

## Remaining Work

### Open Questions for Appcore Validation

1. **MarkdownRenderable signature**: Should it take `LinearizerState` instead of `colorize` and `columns_max`?
   - Current: `render_as_markdown(colorize: bool, columns_max: Absential[int])`
   - Proposed: `render_as_markdown(auxdata: Absential[LinearizerState])`
   - Benefits: Access to incision boundaries, full configuration, consistency with linearizer APIs

2. **JsonRenderable necessity**: Do we need this as a protocol, or can appcore just use `DictionaryRenderable` + `json.dumps()`?

3. **Default Markdown renderer**: Should `colorize` parameter affect Markdown syntax (`**bold**`) or only terminal rendering?
   - Decision: Emit clean Markdown always, let consumer handle rendering

### Pending Implementation

1. **Implement `_dictionary_to_markdown()` default renderer**
   - Location: `ictr/renderables.py`
   - Pattern: Convert dict to bullet list with nested structures

2. **Add `JsonTextualizer` class** (if needed after appcore validation)
   - Location: TBD (`ictr/textualizers.py` or `ictr/standard/compositors.py`)
   - See design spec below

3. **Update linearizers for protocol support**
   - Location: `ictr/standard/linearizers.py`
   - Add protocol checks to `linearize_omni_plain()` and `linearize_omni_rich()`

4. **Add public `linearize()` convenience function**
   - Location: `ictr/__init__.py` or `ictr/standard/__init__.py`
   - Simple wrapper around linearizer with sensible defaults

## Design Specs for Pending Items

### `JsonTextualizer` (If Needed)

Textualizer producing JSON-formatted output for structured logging.

**Key behaviors**:
- Serialize `Record` objects to JSON
- Use protocol resolution: `render_as_json()` → `render_as_dictionary()` → dataclass introspection → repr()
- Support compact and pretty-printed modes

**Location**: TBD after appcore validation
- Option A: `ictr/textualizers.py` (alongside other textualizers)
- Option B: `ictr/standard/compositors.py` (as a compositor variant)

## Appcore Integration Patterns

### Reusable ICTR Components

| Component | Purpose | Usage in Appcore |
|-----------|---------|------------------|
| `DictionaryRenderable` | Base serialization protocol | Result objects inherit for JSON/TOML export |
| `MarkdownRenderable` | Structured markdown output | CLI display with Rich rendering |
| `linearize()` | Object → text lines | Plain text output mode |
| `LinearizerState` | Linearization context | Configuration for markdown/plain rendering |
| `standard.Printer` | Stream output | Terminal/file output with color detection |

### Example Display Pattern

```python
# In appcore CLI code

async def display(
    obj: DictionaryRenderable,
    display_options: DisplayOptions,
    exits: AsyncExitStack,
) -> None:
    stream = await display_options.provide_stream( exits )

    match display_options.presentation:
        case Presentations.Json:
            text = json.dumps( obj.render_as_dictionary( ), indent = 2 )
        case Presentations.Toml:
            text = tomli_w.dumps( obj.render_as_dictionary( ) )
        case Presentations.Markdown:
            # Option A: Simple signature
            text = obj.render_as_markdown( )
            # Option B: With LinearizerState
            # state = LinearizerState.from_configuration( ... )
            # text = obj.render_as_markdown( auxdata = state )
        case Presentations.Plain:
            lines = ictr.linearize( obj )
            text = '\n'.join( lines )

    stream.write( text )
    stream.write( '\n' )
```

### Appcore-Specific Extensions

Appcore can extend `ictr` protocols for format-specific needs:

```python
# In appcore

class TomlRenderable( ictr.DictionaryRenderable, __.typx.Protocol ):
    '''Objects providing TOML serialization.'''

    def render_as_toml( self ) -> str:
        '''Returns TOML string representation.'''
        return tomli_w.dumps( self.render_as_dictionary( ) )
```

---

## Quick Reference

### Protocol Resolution Order

When serializing objects, use this fallback chain:

1. **Explicit protocol**: Check `isinstance(obj, DictionaryRenderable)` → call `render_as_dictionary()`
2. **Dataclass introspection**: Check `dataclasses.is_dataclass(obj)` → extract fields (exclude `_` prefix)
3. **Basic types**: `str`, `int`, `float`, `bool`, `None` → pass through
4. **Collections**: `Sequence`, `Mapping` → recursively serialize elements
5. **Fallback**: `repr(obj)` for unknown types

See `ictr/renderables.py:_serialize_value()` for implementation.

---

## Next Steps

1. **Validate from appcore**: Implement display logic in appcore CLI to validate design decisions
2. **Refine signatures**: Update `MarkdownRenderable` based on real usage patterns
3. **Complete implementation**: Finish remaining items after validation
4. **Archive this document**: Move to historical notes once work is complete
