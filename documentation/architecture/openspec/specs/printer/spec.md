# Printer

## Purpose

Printers abstract output targets. Default printer writes to stderr, but custom
printers can route to files, logging, or other destinations. Provides column
constraints to compositors for proper line wrapping.

## Requirements

### Requirement: Default stderr Output

The system SHALL output diagnostic messages to stderr by default.

#### Scenario: Default printer
- **WHEN** no custom printer factories are configured
- **THEN** messages are printed to stderr

### Requirement: Textualization Control

The system SHALL provide textualization control information to compositors.

#### Scenario: Column count detection
- **WHEN** the output target is a TTY
- **THEN** the printer provides the terminal column count

#### Scenario: Non-TTY output
- **WHEN** the output target is not a TTY
- **THEN** the printer provides None for column count

#### Scenario: Colorization capability
- **WHEN** the output target supports ANSI
- **THEN** the printer indicates colorization is available

### Requirement: Custom Printer Factories

The system SHALL support custom printer factories for routing output to
arbitrary targets.

#### Scenario: Custom factory
- **WHEN** `install(printer_factories=my_factory)` is called
- **THEN** messages are routed through the custom factory

#### Scenario: Text stream target
- **WHEN** a writable text stream is provided as printer factory
- **THEN** messages are written to the stream

#### Scenario: Multiple printer factories
- **WHEN** multiple printer factories are provided
- **THEN** each factory produces a printer and all receive output

### Requirement: ANSI Handling

The system SHALL handle ANSI escape sequences appropriately based on output
target capabilities.

#### Scenario: TTY output
- **WHEN** output target is a TTY
- **THEN** ANSI sequences are preserved in output

#### Scenario: Non-TTY output
- **WHEN** output target is not a TTY
- **THEN** ANSI sequences are stripped from output
