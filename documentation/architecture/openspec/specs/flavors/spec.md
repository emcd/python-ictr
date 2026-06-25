# Flavors

## Purpose

Flavors are the message categorization system. They provide semantic categories
(note, error, success, etc.) and numeric trace levels (0-9) for controlling
output verbosity and styling.

## Requirements

### Requirement: Standard Message Flavors

The system SHALL provide standard message flavors with semantic meanings for
common diagnostic scenarios.

#### Scenario: Informational message
- **WHEN** `ictr('note')('message')` is called
- **THEN** output includes `NOTE|` prefix with blue styling

#### Scenario: Warning message
- **WHEN** `ictr('monition')('message')` is called
- **THEN** output includes `MONITION|` prefix with yellow styling

#### Scenario: Error message
- **WHEN** `ictr('error')('message')` is called
- **THEN** output includes `ERROR|` prefix with red styling

#### Scenario: Error with traceback
- **WHEN** `ictr('errorx')('message')` is called inside an except block
- **THEN** output includes `ERROR|` prefix and active exception traceback

#### Scenario: Abort message
- **WHEN** `ictr('abort')('message')` is called
- **THEN** output includes `ABORT|` prefix with bright red styling

#### Scenario: Abort with traceback
- **WHEN** `ictr('abortx')('message')` is called inside an except block
- **THEN** output includes `ABORT|` prefix and active exception traceback

#### Scenario: Deprecation notice
- **WHEN** `ictr('future')('message')` is called
- **THEN** output includes `FUTURE|` prefix with magenta styling

#### Scenario: Success confirmation
- **WHEN** `ictr('success')('message')` is called
- **THEN** output includes `SUCCESS|` prefix with green styling

#### Scenario: Advisory message
- **WHEN** `ictr('advice')('message')` is called
- **THEN** output includes `ADVICE|` prefix with cyan styling

### Requirement: Flavor Aliases

The system SHALL provide short aliases for standard flavors to reduce typing
during interactive debugging.

#### Scenario: Single-letter aliases
- **WHEN** `ictr('n')`, `ictr('m')`, `ictr('e')`, `ictr('a')`, `ictr('f')`, `ictr('s')`, `ictr('v')` are used
- **THEN** they behave identically to `note`, `monition`, `error`, `abort`, `future`, `success`, `advice`

#### Scenario: Extended aliases
- **WHEN** `ictr('ex')` or `ictr('ax')` is used
- **THEN** they behave identically to `errorx` and `abortx`

### Requirement: Hierarchical Trace Levels

The system SHALL support numeric trace levels with automatic indentation to
visualize call depth and execution flow.

#### Scenario: Trace level 0
- **WHEN** `ictr(0)('message')` is called
- **THEN** output includes `TRACE0|` prefix with no indentation

#### Scenario: Trace level 3
- **WHEN** `ictr(3)('message')` is called
- **THEN** output includes `TRACE3|` prefix with 6 spaces of indentation

#### Scenario: Trace level 9
- **WHEN** `ictr(9)('message')` is called
- **THEN** output includes `TRACE9|` prefix with 18 spaces of indentation

### Requirement: Selective Flavor Activation

The system SHALL support enabling/disabling flavors by name and module.

#### Scenario: Global active flavors
- **WHEN** `install(active_flavors={'note', 'error'})` is called
- **THEN** only `note` and `error` flavors produce output globally

#### Scenario: Per-address active flavors
- **WHEN** `install(active_flavors={'mylib': {'success'}})` is called
- **THEN** `mylib` address has `success` enabled in addition to global flavors

#### Scenario: Omniflavor activation
- **WHEN** `install(active_flavors=omniflavor)` is called
- **THEN** all flavors are active for all addresses

### Requirement: Trace Level Filtering

The system SHALL support setting maximum active trace level to control
debugging output verbosity.

#### Scenario: Global trace level
- **WHEN** `install(trace_levels=3)` is called
- **THEN** trace levels 0-3 produce output and levels 4-9 are suppressed

#### Scenario: Per-address trace level
- **WHEN** `install(trace_levels={'mylib': 5})` is called
- **THEN** `mylib` has trace levels 0-5 active while global default is -1

#### Scenario: Default trace level
- **WHEN** no trace levels are configured
- **THEN** all trace levels are disabled (default -1)
