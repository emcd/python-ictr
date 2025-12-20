# ICTR Renderables Integration

## Overview

This document tracks the design and remaining work for `ictr` renderables integration with `appcore`.

**Goal**: Enable objects to control their rendering through protocols, supporting CLI display needs while keeping `ictr` focused on terminal/log output.

**Status**: Phase 2 complete. Protocols and presentations implemented.

---

## Current Status

### ✅ Completed

**Phase 1 - Linearizer Refactoring**:
- `LinearizerConfiguration` and `LinearizerState` implemented
- `CompositorState` refactored to compose `LinearizerState`
- Linearizers exported publicly from `ictr.standard`

**Phase 2 - Protocols and Presentations**:
- ✅ `DictionaryRenderable` protocol with default `render_as_dictionary()`
- ✅ `JsonRenderable` protocol with default `render_as_json(auxdata, *, compact, indent)`
- ✅ `MarkdownRenderable` protocol with `render_as_markdown(auxdata)`
- ✅ Default markdown renderer (`_render_as_markdown()`) with Rich integration
- ✅ Moved renderables to `ictr.standard` (concrete implementations)
- ✅ `Presentation` protocol with `is_renderable()`, `render()`, `linearize()` methods
- ✅ `PlaintextPresentation`, `JsonPresentation`, `MarkdownPresentation` implementations
- ✅ Refactored `core.py` to separate concerns into component-specific modules

**Resolved Design Decisions**:
- `MarkdownRenderable.render_as_markdown()` takes `LinearizerState` positional-only (not keyword `linearizer=`)
- `JsonRenderable.render_as_json()` takes `LinearizerState` positional-only, plus `compact`/`indent` keywords
- Markdown syntax always emitted; colorization handled by Rich at render time
- 2-space indentation for nested markdown structures
- **Presentations are external to `LinearizerConfiguration`** - kept orthogonal for flexibility

---

## Architecture: Presentations

### Problem Statement

Objects may support multiple renderable protocols (e.g., both `MarkdownRenderable` and `JsonRenderable`). We need:

1. A way to select which presentation format to use
2. Extensibility for future formats (TOML, RST, Djot, etc.) without enum changes
3. Per-renderer configuration (e.g., JSON `compact`, `indent`)

### Solution: External Strategy Pattern

Presentations are kept external to `LinearizerConfiguration` to maintain orthogonal concerns:

```
┌────────────────────────────────────────────────────────────┐
│                    Presentation (Protocol)                  │
│  ┌────────────────────┐  ┌──────────────────────────┐      │
│  │ is_renderable(obj) │  │ render(auxdata, obj)     │      │
│  │     -> bool        │  │     -> str               │      │
│  └────────────────────┘  │ linearize(auxdata, obj)  │      │
│                          │     -> tuple[str, ...]   │      │
│                          └──────────────────────────┘      │
└────────────────────────────────────────────────────────────┘
           ▲                    ▲                    ▲
           │                    │                    │
┌──────────┴──────┐  ┌─────────┴─────────┐  ┌──────┴────────┐
│   Plaintext     │  │    Markdown       │  │     Json      │
│  Presentation   │  │   Presentation    │  │ Presentation  │
├─────────────────┤  ├───────────────────┤  ├───────────────┤
│ (fallback)      │  │                   │  │ compact: bool │
│                 │  │                   │  │ indent: int   │
├─────────────────┤  ├───────────────────┤  ├───────────────┤
│ is_renderable:  │  │ is_renderable:    │  │is_renderable: │
│  always True    │  │  MarkdownRender   │  │ JsonRenderable│
├─────────────────┤  ├───────────────────┤  ├───────────────┤
│ linearize:      │  │ render:           │  │ render:       │
│  linearize_omni │  │  render_as_md()   │  │render_as_json │
└─────────────────┘  └───────────────────┘  └───────────────┘
```

### Implementation

```python
# In ictr/standard/presentations.py

@__.typx.runtime_checkable
class Presentation( __.immut.DataclassProtocol, __.typx.Protocol ):
    '''Abstract base for presentations.'''

    @__.abc.abstractmethod
    def is_renderable( self, entity: object ) -> bool:
        '''Does object support this presentation mode?'''
        raise NotImplementedError

    def linearize(
        self, auxdata: LinearizerState, entity: object
    ) -> tuple[ str, ... ]:
        '''Produces contiguous lines of text to render.'''
        return tuple( self.render( auxdata, entity ).split( '\n' ) )

    @__.abc.abstractmethod
    def render(
        self, auxdata: LinearizerState, entity: object
    ) -> str:
        '''Renders object via its protocol implementation.'''
        raise NotImplementedError


class PlaintextPresentation( Presentation ):
    '''Default presentation via standard linearization.'''

    def is_renderable( self, entity: object ) -> bool:
        return True  # Always matches as fallback

    def linearize(
        self, auxdata: LinearizerState, entity: object
    ) -> tuple[ str, ... ]:
        # Optimized to avoid string split
        return linearize_omni( auxdata, entity, auxdata.columns_max )

    def render(
        self, auxdata: LinearizerState, entity: object
    ) -> str:
        return '\n'.join( self.linearize( auxdata, entity ) )


class JsonPresentation( Presentation ):
    '''JSON presentation with configuration.'''

    compact: bool = False
    indent: int = 2

    def is_renderable( self, entity: object ) -> bool:
        return isinstance( entity, (JsonRenderable, JsonRenderableDataclass) )

    def render(
        self, auxdata: LinearizerState, entity: object
    ) -> str:
        if isinstance( entity, (JsonRenderable, JsonRenderableDataclass) ):
            return entity.render_as_json(
                auxdata, compact = self.compact, indent = self.indent )
        raise NotImplementedError


class MarkdownPresentation( Presentation ):
    '''Markdown presentation with Rich rendering support.'''

    def is_renderable( self, entity: object ) -> bool:
        return isinstance( entity, (MarkdownRenderable, MarkdownRenderableDataclass) )

    def render(
        self, auxdata: LinearizerState, entity: object
    ) -> str:
        if isinstance( entity, (MarkdownRenderable, MarkdownRenderableDataclass) ):
            return entity.render_as_markdown( auxdata )
        raise NotImplementedError
```

---

## Future Enhancements

1. **Add `PlaintextRenderable` protocol** (optional)
   - Would allow objects to provide custom plaintext rendering
   - `PlaintextPresentation.linearize()` would check for this before `linearize_omni()`

2. **Add public `linearize()` convenience function** (optional)
   - Simple wrapper with sensible defaults for one-off linearization
   - Could live in `ictr.standard.__init__` or `ictr.__init__`

3. **Export presentations from `ictr.standard`** (if needed)
   - Currently in `presentations.py` but not exported
   - May want to add `from .presentations import *` to `ictr/standard/__init__.py`

---

## Appcore Integration Pattern

Presentations are created and used externally to `LinearizerState`:

```python
# In appcore CLI code

async def display(
    obj: DictionaryRenderable,
    display_options: DisplayOptions,
    stream: __.typx.TextIO,
    printer: ictr.Printer,
) -> None:
    # Select presentation based on user choice
    match display_options.presentation:
        case Presentations.Json:
            presentation = ictr.standard.JsonPresentation(
                compact = display_options.compact,
                indent = display_options.indent )
        case Presentations.Markdown:
            presentation = ictr.standard.MarkdownPresentation( )
        case _:
            presentation = ictr.standard.PlaintextPresentation( )

    # Create linearizer state (independent of presentation)
    config = ictr.standard.LinearizerConfiguration( )
    control = printer.provide_textualization_control( )
    auxdata = ictr.standard.LinearizerState.from_configuration( config, control )

    # Render using selected presentation
    text = presentation.render( auxdata, obj )

    stream.write( text )
    stream.write( '\n' )
```

### Key Benefits of External Approach

1. **Orthogonal concerns**: Linearization config and presentation selection are independent
2. **No cyclic imports**: `presentations.py` can import `linearizers.py` without issues
3. **Flexibility**: Can switch presentations dynamically without reconfiguring linearizer
4. **Simplicity**: Clear separation makes code easier to understand and maintain

---

## Quick Reference

### Usage Pattern

```python
# 1. Create presentation (with optional config)
presentation = JsonPresentation( compact = True )

# 2. Create linearizer state
auxdata = LinearizerState.from_configuration( config, control )

# 3. Render object
text = presentation.render( auxdata, obj )
```

### Renderable Protocols

| Protocol | Method Signature | Purpose |
|----------|------------------|---------|
| `DictionaryRenderable` | `render_as_dictionary() -> dict` | Base for serialization |
| `JsonRenderable` | `render_as_json(auxdata, *, compact, indent) -> str` | JSON with options |
| `MarkdownRenderable` | `render_as_markdown(auxdata) -> str` | Markdown with Rich |
| `PlaintextRenderable` | `render_as_plaintext() -> str` | (Future) Plain text |

### Presentation Classes

| Class | Config Fields | Checks For |
|-------|---------------|------------|
| `PlaintextPresentation` | (none) | Always matches (fallback) |
| `JsonPresentation` | `compact: bool`, `indent: int` | `JsonRenderable`, `JsonRenderableDataclass` |
| `MarkdownPresentation` | (none) | `MarkdownRenderable`, `MarkdownRenderableDataclass` |

### File Locations

| Component | Location |
|-----------|----------|
| Renderable protocols and defaults | `ictr/standard/renderables.py` |
| Presentation protocol and classes | `ictr/standard/presentations.py` |
| Linearizer config and state | `ictr/standard/linearizers.py` |
| Compositor config and state | `ictr/standard/compositors.py` |
| Introducer config and state | `ictr/standard/introducers.py` |
| Shared enums and utilities | `ictr/standard/core.py` |
