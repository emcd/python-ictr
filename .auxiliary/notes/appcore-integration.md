# ICTR Renderables Integration

## Overview

This document tracks the design and remaining work for `ictr` renderables integration with `appcore`.

**Goal**: Enable objects to control their rendering through protocols, supporting CLI display needs while keeping `ictr` focused on terminal/log output.

**Status**: Phase 2 in progress. Protocols implemented, now designing presentation dispatch system.

---

## Current Status

### ✅ Completed

**Phase 1 - Linearizer Refactoring**:
- `LinearizerConfiguration` and `LinearizerState` implemented
- `CompositorState` refactored to compose `LinearizerState`
- Linearizers exported publicly from `ictr.standard`

**Phase 2 - Protocols**:
- ✅ `DictionaryRenderable` protocol with default `render_as_dictionary()`
- ✅ `JsonRenderable` protocol with default `render_as_json()`
- ✅ `MarkdownRenderable` protocol with `render_as_markdown(linearizer=...)`
- ✅ Default markdown renderer (`_render_as_markdown()`) with Rich integration
- ✅ Moved renderables to `ictr.standard` (concrete implementations)

**Resolved Design Decisions**:
- `MarkdownRenderable.render_as_markdown()` takes `LinearizerState` (not separate params)
- Markdown syntax always emitted; colorization handled by Rich at render time
- 2-space indentation for nested markdown structures

---

## Architecture: PresentationConfiguration

### Problem Statement

During linearization, objects may support multiple renderable protocols (e.g., both `MarkdownRenderable` and `JsonRenderable`). We need:

1. A way to specify preferred presentation mode via `LinearizerState`
2. Extensibility for future formats (TOML, RST, Djot, etc.) without enum changes
3. Per-renderer configuration (e.g., JSON `compact`, `indent`)

### Solution: Strategy Pattern with Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                      LinearizerConfiguration                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              presentation: PresentationConfiguration     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PresentationConfiguration (ABC)                │
│  ┌──────────────────────┐  ┌──────────────────────────────┐     │
│  │ matches(obj) -> bool │  │ render(obj, auxdata) -> lines│     │
│  └──────────────────────┘  └──────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
           ▲                    ▲                    ▲
           │                    │                    │
┌──────────┴───────┐ ┌─────────┴────────┐ ┌────────┴─────────┐
│ PlaintextPresent │ │ MarkdownPresent  │ │   JsonPresent    │
│   Configuration  │ │  Configuration   │ │  Configuration   │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ (default)        │ │                  │ │ compact: bool    │
│                  │ │                  │ │ indent: int      │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ matches:         │ │ matches:         │ │ matches:         │
│  PlaintextRender │ │  MarkdownRender  │ │  JsonRenderable  │
│  or fallback     │ │  or fallback     │ │  or fallback     │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ render:          │ │ render:          │ │ render:          │
│  linearize_omni  │ │  render_as_md()  │ │  render_as_json()│
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### Class Hierarchy

```python
class PresentationConfiguration( __.immut.DataclassObject, __.abc.ABC ):
    '''Base configuration for presentation-specific rendering.'''

    @__.abc.abstractmethod
    def matches( self, obj: object ) -> bool:
        '''Check if object supports this presentation mode.'''
        ...

    @__.abc.abstractmethod
    def render(
        self, obj: object, auxdata: LinearizerState
    ) -> tuple[ str, ... ]:
        '''Render object using this presentation mode.

        Returns tuple of lines. Falls back to default linearization
        if object doesn't support the specific protocol.
        '''
        ...


class PlaintextPresentationConfiguration( PresentationConfiguration ):
    '''Default presentation using standard linearization.'''

    def matches( self, obj: object ) -> bool:
        # Could check for PlaintextRenderable if we add it later
        return True  # Always matches as fallback

    def render(
        self, obj: object, auxdata: LinearizerState
    ) -> tuple[ str, ... ]:
        # Check for PlaintextRenderable first (future)
        # if isinstance( obj, PlaintextRenderable ):
        #     text = obj.render_as_plaintext()
        #     return tuple( text.split( '\n' ) )
        return linearize_omni( auxdata, obj, auxdata.columns_max )


class JsonPresentationConfiguration( PresentationConfiguration ):
    '''JSON presentation with formatting options.'''

    compact: bool = False
    indent: int = 2

    def matches( self, obj: object ) -> bool:
        return isinstance( obj, JsonRenderable )

    def render(
        self, obj: object, auxdata: LinearizerState
    ) -> tuple[ str, ... ]:
        if isinstance( obj, JsonRenderable ):
            text = obj.render_as_json(
                compact = self.compact, indent = self.indent )
            return tuple( text.split( '\n' ) )
        # Fallback to default linearization
        return linearize_omni( auxdata, obj, auxdata.columns_max )


class MarkdownPresentationConfiguration( PresentationConfiguration ):
    '''Markdown presentation with Rich rendering support.'''

    def matches( self, obj: object ) -> bool:
        return isinstance( obj, MarkdownRenderable )

    def render(
        self, obj: object, auxdata: LinearizerState
    ) -> tuple[ str, ... ]:
        if isinstance( obj, MarkdownRenderable ):
            text = obj.render_as_markdown( linearizer = auxdata )
            return tuple( text.split( '\n' ) )
        # Fallback to default linearization
        return linearize_omni( auxdata, obj, auxdata.columns_max )
```

### Integration with LinearizerConfiguration

```python
class LinearizerConfiguration( __.immut.DataclassObject ):
    '''Behaviors for standard textual linearizer.'''

    # ... existing fields ...

    presentation: PresentationConfiguration = __.dcls.field(
        default_factory = PlaintextPresentationConfiguration )
```

### Linearizer Integration

```python
def linearize_omni(
    auxdata: LinearizerState,
    entity: object,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    # Check if presentation config handles this object
    presentation = auxdata.configuration.presentation
    if presentation.matches( entity ):
        return presentation.render( entity, auxdata )

    # Existing fallback chain
    if auxdata.colorize:
        return linearize_omni_rich( auxdata, entity, columns_max )
    return linearize_omni_plain( auxdata, entity, columns_max )
```

---

## Remaining Implementation

1. **Implement `PresentationConfiguration` base class**
   - Location: `ictr/standard/core.py`
   - ABC with `matches()` and `render()` methods

2. **Implement presentation subclasses**
   - `PlaintextPresentationConfiguration` (default)
   - `MarkdownPresentationConfiguration`
   - `JsonPresentationConfiguration`

3. **Update `LinearizerConfiguration`**
   - Add `presentation` field with default

4. **Update `linearize_omni()`**
   - Check presentation config before type-based dispatch

5. **Add public `linearize()` convenience function**
   - Simple wrapper with sensible defaults

---

## Appcore Integration Pattern

With PresentationConfiguration, appcore can select presentation mode:

```python
# In appcore CLI code

async def display(
    obj: DictionaryRenderable,
    display_options: DisplayOptions,
    exits: AsyncExitStack,
) -> None:
    # Select presentation configuration based on user choice
    match display_options.presentation:
        case Presentations.Json:
            presentation = ictr.standard.JsonPresentationConfiguration(
                compact = display_options.compact,
                indent = display_options.indent )
        case Presentations.Markdown:
            presentation = ictr.standard.MarkdownPresentationConfiguration()
        case _:
            presentation = ictr.standard.PlaintextPresentationConfiguration()

    # Create linearizer with presentation config
    config = ictr.standard.LinearizerConfiguration( presentation = presentation )
    control = printer.provide_textualization_control()
    auxdata = ictr.standard.LinearizerState.from_configuration( config, control )

    # Render
    lines = ictr.standard.linearize_omni( auxdata, obj )
    text = '\n'.join( lines )

    stream.write( text )
    stream.write( '\n' )
```

---

## Quick Reference

### Protocol Resolution Order

1. **Presentation config**: `presentation.matches(obj)` → `presentation.render(obj, auxdata)`
2. **String**: Direct text linearization
3. **Exception**: Traceback rendering
4. **Other objects**: Pretty-print fallback

### Renderable Protocols

| Protocol | Method | Purpose |
|----------|--------|---------|
| `DictionaryRenderable` | `render_as_dictionary()` | Base for serialization |
| `JsonRenderable` | `render_as_json(compact, indent)` | JSON with options |
| `MarkdownRenderable` | `render_as_markdown(linearizer)` | Markdown with Rich |
| `PlaintextRenderable` | `render_as_plaintext()` | (Future) Plain text |

### File Locations

| Component | Location |
|-----------|----------|
| Renderable protocols | `ictr/standard/renderables.py` |
| PresentationConfiguration | `ictr/standard/core.py` |
| Linearizers | `ictr/standard/linearizers.py` |
