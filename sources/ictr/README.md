# ictr

Non-intrusive system for logging and debug printing.

## Architecture

The system is organized into four layers with protocol-based boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│  Dispatcher Layer                                           │
│  ┌───────────┐  Manages routing and activation control    │
│  │ Dispatcher├──────────────────────────────────────────┐  │
│  └─────┬─────┘                                          │  │
└────────┼────────────────────────────────────────────────┼──┘
         │ creates/caches                         invokes │
         ↓                                                 ↓
┌─────────────────────────────────────────────────────────────┐
│  Reporter Layer                                             │
│  ┌────────┐  Coordinates textualization and printing      │
│  │Reporter├────────────────────────────────────────────┐  │
│  └───┬────┘                                            │  │
└──────┼─────────────────────────────────────────────────┼──┘
       │ uses                                      uses  │
       ↓                                                 ↓
┌──────────────────────────┐   ┌──────────────────────────┐
│   Compositor Layer       │   │    Printer Layer         │
│  ┌─────────────┐         │   │  ┌────────┐             │
│  │ Compositor  │ Formats │   │  │Printer │ Outputs     │
│  │  + Introducer content │   │  └────────┘ to targets  │
│  │  + Linearizers        │   │                          │
│  └─────────────┘         │   │                          │
└──────────────────────────┘   └──────────────────────────┘
```

**Dispatcher** (`dispatchers.py`): Entry point for diagnostic calls. Routes
messages to appropriate reporters based on module address and flavor. Manages
activation control (which flavors/trace levels are active per module).

**Reporter** (`reporters.py`): Bridges dispatcher and output. Each reporter
instance binds a specific address + flavor combination to a compositor and
printer. Active/inactive state controls whether messages are processed.

**Compositor** (`textualizers.py`): Transforms structured records into
formatted text lines. Composed of introducer (prefix generation) and
linearizers (content to lines). Supports both plain and Rich rendering.

**Printer** (`printers.py`): Abstracts output targets. Default prints to
stderr, but custom printers can route to files, logging, or other destinations.
Provides column constraints to compositors for proper line wrapping.

## Data Flow

```
User Code
   │
   │ ctrl.note( "summary", detail1, detail2 )
   ↓
Dispatcher.__call__( "note" )
   │
   │ returns cached or creates Reporter
   ↓
Reporter.__call__( "summary", detail1, detail2 )
   │
   │ packages MessageContent → Record
   ↓
Compositor( control, record )
   │
   │ 1. Introducer generates prefix lines
   │ 2. Linearizers convert content to text lines
   │ 3. Layout combines introduction + content
   ↓
Printer( formatted_lines )
   │
   └→ Output Target (stderr, file, logging, etc.)
```

## Configuration Hierarchy

Configuration follows Python package structure with inheritance:

```
Global Configuration (all modules)
   ├─→ Package Configuration (myapp.*)
   │      ├─→ Subpackage Configuration (myapp.subsystem.*)
   │      └─→ Module Configuration (myapp.module)
   └─→ Package Configuration (library.*)
```

Each level can specify:
- **Active flavors**: Which message categories produce output
- **Max trace level**: Deepest trace level to render
- **Printer factory**: How to create output targets
- **Compositor factory**: How to format messages
- **Per-flavor overrides**: Flavor-specific configuration

## Standard Flavors

The `standard/` subpackage provides ready-made configurations:

| Flavor    | Label     | Color     | Stack | Aliases |
|-----------|-----------|-----------|-------|---------|
| note      | NOTE      | blue      | no    | n       |
| monition  | MONITION  | yellow    | no    | m       |
| error     | ERROR     | red       | no    | e       |
| errorx    | ERROR     | red       | yes   | ex      |
| abort     | ABORT     | bright_red| no    | a       |
| abortx    | ABORT     | bright_red| yes   | ax      |
| future    | FUTURE    | magenta   | no    | f       |
| success   | SUCCESS   | green     | no    | s       |
| advice    | ADVICE    | cyan      | no    | v       |

Trace levels 0-9 provide automatic hierarchical indentation (2 spaces per
level) for visualizing call depth.

## Threading Safety

- Dispatcher registration uses mutex-protected initialization
- Reporters are immutable once created
- Compositors and printers are stateless protocols
- Configuration objects are immutable dataclasses

No global mutable state exists after initialization, enabling safe concurrent
message emission from multiple threads.
