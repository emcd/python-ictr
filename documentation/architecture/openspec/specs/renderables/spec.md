# renderables Specification

## Purpose
TBD - created by archiving change hoist-renderable-protocol. Update Purpose after archive.
## Requirements
### Requirement: Renderable Protocol

The system SHALL provide `Renderable` and `RenderableDataclass` protocols at
the package level for objects that can render themselves as dictionaries. These
are the cross-package contracts that libraries like appcore import.

#### Scenario: Protocol compliance
- **WHEN** a class implements `render_as_dictionary()` returning a `dict[str, Any]`
- **THEN** it satisfies the `Renderable` protocol
- **AND** can be recognized via `isinstance()` checks at runtime

#### Scenario: Dataclass protocol compliance
- **WHEN** a dataclass implements `render_as_dictionary()` returning a `dict[str, Any]`
- **THEN** it satisfies the `RenderableDataclass` protocol
- **AND** is recognized as both a dataclass and a renderable

#### Scenario: Package-level import
- **WHEN** `from ictr import Renderable` or `from ictr import RenderableDataclass` is used
- **THEN** the protocols are available without importing from `ictr.standard`

#### Scenario: Backward compatibility
- **WHEN** `from ictr.standard import DictionaryRenderable` is used
- **THEN** it resolves to the same `Renderable` protocol via alias
- **AND** existing code continues to work without changes

