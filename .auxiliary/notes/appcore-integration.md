# ICTR Rendering Protocols and Linearizer Refactoring

## Overview

This document captures the design for extending `ictr` with:

1. **Renderable protocols** — allowing objects to control their representation in various formats
2. **Linearizer refactoring** — exposing linearization as a public API for use by `appcore` and other consumers
3. **JSON textualization** — structured logging support

These changes support `appcore`'s CLI display needs while keeping `ictr` focused on terminal/log output concerns.

## Design Principles

### Separation of Concerns

| Component | Responsibility |
|-----------|----------------|
| **Textualizer** | `Record` → formatted string |
| **Printer** | String → destination (stream, file) |
| **Linearizer** | Object → lines of text (intermediate step) |

### Protocol Resolution

Objects can implement protocols to control their rendering. Fallback chains provide sensible defaults:

1. Check for specific protocol method (e.g., `render_as_json`)
2. Check for base protocol (`render_as_dictionary`)
3. Dataclass introspection (excluding `_`-prefixed fields)
4. Basic type pass-through
5. `repr()` fallback

### Package Boundaries

| Concern | Package | Rationale |
|---------|---------|-----------|
| `DictionaryRenderable` | `ictr` | Base for serialization |
| `JsonRenderable` | `ictr` | Structured logging |
| `MarkdownRenderable` | `ictr` | Terminal display via Rich |
| `PlaintextRenderable` | `ictr` | Wrappable text (deferred) |
| `JsonTextualizer` | `ictr` | Structured logging output |
| Linearizers (public) | `ictr` | For downstream use |
| `TomlRenderable` | `appcore` | Config/CLI serialization |
| CLI display logic | `appcore` | Format multiplexing |

---

## Renderable Protocols

### `DictionaryRenderable`

Base protocol for objects that can represent themselves as dictionaries suitable for serialization.
```python
class DictionaryRenderable( __.typx.Protocol ):
    '''Objects providing dictionary representation for serialization.'''

    def render_as_dictionary( self ) -> dict[ str, __.typx.Any ]:
        '''Returns dictionary suitable for JSON/TOML serialization.

        Implementations should:
        - Exclude private attributes (``_`` prefix)
        - Convert opaque identifiers appropriately
        - Ensure all values are serializable
        '''
        ...
```

### `JsonRenderable`

Extends `DictionaryRenderable` with custom JSON formatting control.
```python
class JsonRenderable( DictionaryRenderable, __.typx.Protocol ):
    '''Objects providing custom JSON serialization.'''

    def render_as_json( self, compact: bool = False, indent: int = 2 ) -> str:
        '''Returns JSON string representation.'''
        # Default implementation available via inheritance
        d = self.render_as_dictionary( )
        if compact:
            return __.json.dumps(
                d, ensure_ascii = False, separators = ( ',', ':' ) )
        return __.json.dumps( d, ensure_ascii = False, indent = indent )
```

### `MarkdownRenderable`

For objects that render as atomic Markdown blocks (tables, code blocks, etc.) that should not be wrapped or modified.
```python
class MarkdownRenderable( __.typx.Protocol ):
    '''Objects providing Markdown representation for terminal/log output.'''

    def render_as_markdown(
        self,
        colorize: bool = False,
        columns_max: int | None = None,
    ) -> str:
        '''Returns Markdown string.

        ``columns_max`` is advisory. Objects may use it to size tables
        or wrap prose paragraphs, but atomic structures (tables, code
        blocks) may exceed it. The textualizer will not further modify
        the returned content.

        When ``colorize`` is True, objects may include ANSI sequences
        or rely on Rich rendering downstream.
        '''
        ...
```

### `PlaintextRenderable` (Deferred)

For objects providing wrappable plain text. Deferred for future implementation.
```python
class PlaintextRenderable( __.typx.Protocol ):
    '''Objects providing wrappable plain text representation.'''

    def render_as_plaintext( self ) -> str:
        '''Returns plain text that may be wrapped by the textualizer.'''
        ...
```

---

## Linearizer Refactoring

### New Configuration Hierarchy

Factor `LinearizerConfiguration` out of `TextualizerConfiguration`:
```python
class LinearizerConfiguration( __.immut.DataclassObject ):
    '''Configuration for linearization behavior.'''

    exceptionscfg: ExceptionsConfiguration = __.dcls.field(
        default_factory = ExceptionsConfiguration )
    incision_boundary: IncisionBoundaries = IncisionBoundaries.Wordsplits
```

### `LinearizerState`

Runtime state DTO for linearization, parallel to `TextualizerState`:
```python
class LinearizerState( __.immut.DataclassObject ):
    '''Runtime state for linearization.'''

    configuration: LinearizerConfiguration
    control: TextualizerControl
    colorize: bool
    columns_max: Absential[ int ] = absent

    @classmethod
    def from_configuration(
        cls,
        configuration: LinearizerConfiguration | None = None,
        control: TextualizerControl | None = None,
    ) -> __.typx.Self:
        if configuration is None:
            configuration = LinearizerConfiguration( )
        if control is None:
            control = TextualizerControl( )
        colorize = ENRICH and control.colorize
        columns_max_ = control.columns_max
        return cls(
            configuration = configuration,
            control = control,
            colorize = colorize,
            columns_max = absent if columns_max_ is None else columns_max_ )
```

### Updated `TextualizerConfiguration`
```python
class TextualizerConfiguration( __.immut.DataclassObject ):
    '''Behaviors and format for text from standard textualizer.'''

    linearizercfg: LinearizerConfiguration = __.dcls.field(
        default_factory = LinearizerConfiguration )
    colorize: bool = True
    columns_constraint: ColumnsConstraints = ColumnsConstraints.Complect
    columns_max: __.typx.Optional[ int ] = None
    detail_prefix_initial: str = ''
    detail_prefix_subsequent: __.typx.Optional[ str ] = None
    details_separator: str = '\n\n'
    line_prefix_initial: str = ''
    line_prefix_subsequent: __.typx.Optional[ str ] = None
    summary_incision_ratio: float = 0.3
```

### Updated `TextualizerState`

Add method to derive `LinearizerState`:
```python
class TextualizerState( __.immut.DataclassObject ):
    # ... existing fields ...

    def as_linearizer_state( self ) -> LinearizerState:
        '''Derives linearizer state from textualizer state.'''
        return LinearizerState(
            configuration = self.configuration.linearizercfg,
            control = self.control,
            colorize = self.colorize,
            columns_max = self.columns_max )
```

### Public Linearization API
```python
def linearize(
    obj: object,
    configuration: LinearizerConfiguration | None = None,
    control: TextualizerControl | None = None,
) -> tuple[ str, ... ]:
    '''Public API for linearizing objects to text lines.

    Args:
        obj: Object to linearize.
        configuration: Linearization settings. Uses defaults if None.
        control: Output context (colorization, columns). Uses defaults if None.

    Returns:
        Tuple of text lines.
    '''
    state = LinearizerState.from_configuration( configuration, control )
    return linearize_omni( state, obj, state.columns_max )
```

---

## JSON Textualization

### `JsonTextualizer`

Textualizer that produces JSON-formatted output for structured logging:
```python
class JsonTextualizer( Textualizer ):
    '''Textualizer producing JSON-formatted output.'''

    compact: bool = False
    indent: int = 2

    def __call__(
        self, control: TextualizerControl, record: Record
    ) -> str:
        data = {
            'timestamp': record.ctime.isoformat( ),
            'address': record.address,
            'flavor': (
                record.flavor if isinstance( record.flavor, str )
                else f"trace{record.flavor}" ),
            'content': self._serialize_content( record.content ),
        }
        if self.compact:
            return __.json.dumps(
                data, ensure_ascii = False, separators = ( ',', ':' ) )
        return __.json.dumps(
            data, ensure_ascii = False, indent = self.indent )

    def _serialize_content( self, content: object ) -> Any:
        '''Serializes content with protocol support.'''
        if isinstance( content, MessageContent ):
            return self._serialize_message_content( content )
        return self._serialize_object( content )

    def _serialize_object( self, obj: object ) -> Any:
        '''Resolution order for object serialization.'''
        # 1. Direct JSON control
        if hasattr( obj, 'render_as_json' ):
            return __.json.loads( obj.render_as_json( compact = True ) )

        # 2. Dictionary representation
        if hasattr( obj, 'render_as_dictionary' ):
            return obj.render_as_dictionary( )

        # 3. Dataclass introspection
        if __.dcls.is_dataclass( obj ) and not isinstance( obj, type ):
            return self._serialize_dataclass( obj )

        # 4. Basic types
        if isinstance( obj, ( str, int, float, bool, type( None ) ) ):
            return obj
        if isinstance( obj, ( list, tuple ) ):
            return [ self._serialize_object( item ) for item in obj ]
        if isinstance( obj, dict ):
            return {
                str( k ): self._serialize_object( v )
                for k, v in obj.items( ) }

        # 5. Fallback
        return repr( obj )

    def _serialize_dataclass( self, obj: object ) -> dict[ str, Any ]:
        '''Serializes dataclass, excluding private fields.'''
        result: dict[ str, Any ] = { }
        for field in __.dcls.fields( obj ):
            if field.name.startswith( '_' ): continue
            value = getattr( obj, field.name )
            result[ field.name ] = self._serialize_object( value )
        return result
```

---

## Integration with `appcore`

### Reusable Components

`appcore` can reuse these `ictr` components for CLI display:

| Component | Usage |
|-----------|-------|
| `Printer` protocol | Output abstraction |
| `standard.Printer` | Concrete stream printer |
| `TextualizerControl` | Colorization, column detection |
| `produce_columns_max_calculator` | TTY column width |
| `linearize()` | Object → text lines |
| `LinearizerConfiguration` | Linearization settings |
| `LinearizerState` | Runtime linearization context |

### Display Pattern
```python
# In appcore CLI code

async def display(
    obj: object,
    display_options: DisplayOptions,
    exits: AsyncExitStack,
) -> None:
    stream = await display_options.provide_stream( exits )
    printer = ictr.standard.Printer(
        target = stream,
        force_color = display_options.assume_rich_terminal )
    control = printer.provide_textualizer_control( ) or ictr.TextualizerControl( )

    match display_options.presentation:
        case Presentations.Json:
            text = _render_json( obj )
        case Presentations.Toml:
            text = _render_toml( obj )
        case Presentations.Markdown:
            text = _render_markdown( obj, control )
        case Presentations.Plain:
            lines = ictr.linearize( obj, control = control )
            text = '\n'.join( lines )

    printer( text )
```

### `appcore`-Specific Protocols
```python
# In appcore

class TomlRenderable( ictr.DictionaryRenderable, __.typx.Protocol ):
    '''Objects providing custom TOML serialization.'''

    def render_as_toml( self ) -> str:
        '''Returns TOML string representation.'''
        return tomli_w.dumps( self.render_as_dictionary( ) )
```

---

## Implementation Phases

### Phase 1: Pre-1.0 (Breaking Changes)

1. Factor `LinearizerConfiguration` from `TextualizerConfiguration`
2. Add `LinearizerState` DTO
3. Change linearizer signatures to use `LinearizerState`
4. Add `as_linearizer_state()` to `TextualizerState`
5. Export linearizers and configuration types publicly

### Phase 2: Post-1.0 (Additive)

1. Add `DictionaryRenderable` protocol
2. Add `JsonRenderable` protocol
3. Add `MarkdownRenderable` protocol
4. Add `JsonTextualizer`
5. Update linearizers to check for `render_as_*` methods
6. Add public `linearize()` convenience function
7. (Deferred) Add `PlaintextRenderable` protocol

---

## Summary

This design:

- Keeps `ictr` focused on terminal/log output
- Provides clean protocols for objects to control their rendering
- Exposes linearization as a public API for `appcore`
- Maintains separation between textualizers (what) and printers (where)
- Enables structured JSON logging
- Minimizes breaking changes before 1.0
