.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
System Overview
*******************************************************************************

This package implements a layered diagnostic output system with clean
separation between message dispatch, content transformation, and output
rendering. The architecture enables flexible configuration, library-friendly
registration, and optional Rich integration without tight coupling.

Component Layers
===============================================================================

The system is organized into three primary layers::

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

**Dispatcher Layer**: Entry point for diagnostic calls. Routes messages to
appropriate reporters based on module address and flavor. Manages activation
control (which flavors/trace levels are active per module).

**Reporter Layer**: Bridges dispatcher and output. Each reporter instance
binds a specific address + flavor combination to a compositor and printer.
Active/inactive state controls whether messages are processed.

**Compositor Layer**: Transforms structured records into formatted text
lines. Composed of introducer (prefix generation), linearizers (content to
lines), and layout logic. Supports both plain and Rich rendering.

**Printer Layer**: Abstracts output targets. Default prints to stderr, but
custom printers can route to files, logging, or other destinations. Provides
column constraints to compositors for proper line wrapping.

Data Flow
===============================================================================

Typical message flow through the system::

    User Code
       │
       │ ctrl.note( "summary", detail1, detail2 )
       ↓
    Dispatcher.__getattr__( "note" )
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

Configuration Hierarchy
===============================================================================

Configuration follows Python package structure with inheritance::

    Global Configuration (all modules)
       ├─→ Package Configuration (myapp.*)
       │      ├─→ Subpackage Configuration (myapp.subsystem.*)
       │      └─→ Module Configuration (myapp.module)
       └─→ Package Configuration (library.*)

Each level can specify:

* **Active flavors**: Which message categories produce output
* **Max trace level**: Deepest trace level to render
* **Printer factory**: How to create output targets
* **Compositor factory**: How to format messages
* **Per-flavor overrides**: Flavor-specific configuration

Libraries register configurations without affecting application or other
library settings. Applications can selectively enable library diagnostics by
updating active flavors for specific addresses.

Standard Flavor Recipes
===============================================================================

The ``ictr.standard`` subpackage provides ready-made configurations:

**Message Flavors**: ``note``, ``monition``, ``error``, ``errorx``,
``abort``, ``abortx``, ``future``, ``success``, ``advice`` with semantic
labels, colors, and emoji.

**Trace Levels**: 0-9 with automatic hierarchical indentation (2 spaces per
level) for visualizing call depth.

**Rich Integration**: Automatic detection and graceful fallback. When Rich is
available, enables colorized output with styled prefixes. When absent, uses
plain text formatting.

These recipes implement common patterns but all components are replaceable via
configuration factories.

Extension Points
===============================================================================

The architecture provides multiple extension points:

**Custom Compositors**: Implement ``Compositor`` protocol to control
formatting logic. Factory pattern allows different compositors per address or
flavor.

**Custom Printers**: Implement ``Printer`` protocol to route output to custom
targets (files, logging, remote services, etc.).

**Custom Introducers**: Replace prefix generation logic while reusing standard
linearizers and layout.

**Custom Linearizers**: Replace content-to-lines conversion for specific
object types (structured data, custom exceptions, etc.).

All extensions integrate through factory configuration, preserving the layered
architecture and avoiding tight coupling.

Threading and Concurrency
===============================================================================

The system is designed for concurrent use:

* Dispatcher registration uses mutex-protected initialization
* Reporters are immutable once created
* Compositors and printers are stateless protocols
* Configuration objects are immutable dataclasses

No global mutable state exists after initialization, enabling safe concurrent
message emission from multiple threads.

Deployment Patterns
===============================================================================

**Application Development**: Use global installation (``install_builtin()``)
for convenient access without imports. Configure global settings and
per-module overrides as needed.

**Library Development**: Register library-specific configuration during
import. Respect application's activation control. Avoid global installation
from libraries.

**Testing**: Direct instantiation without builtins. Override printer factories
to capture output for assertions. Mock auxiliaries (time, thread discovery)
for deterministic tests.
