# Compositor

## Purpose

Compositors transform structured records into formatted text lines. Composed
of an introducer (prefix generation) and linearizers (content to lines).
Supports both plain and Rich rendering.

## Requirements

### Requirement: Prefix Generation

The system SHALL generate formatted prefixes for diagnostic messages.

#### Scenario: Standard flavor prefix
- **WHEN** a `note` message is composited
- **THEN** the prefix `NOTE| ` is generated

#### Scenario: Trace level prefix
- **WHEN** a trace level 2 message is composited
- **THEN** the prefix `TRACE2| ` is generated with 2-space indentation

#### Scenario: Custom introducer
- **WHEN** a custom introducer string is configured
- **THEN** the custom string is used as the prefix

### Requirement: Content Linearization

The system SHALL convert message content to formatted text lines.

#### Scenario: String summary
- **WHEN** a record with string summary is composited
- **THEN** the summary is rendered as text

#### Scenario: Exception summary
- **WHEN** a record with exception summary is composited
- **THEN** the exception type and message are rendered

#### Scenario: Multiple details
- **WHEN** a record with multiple details is composited
- **THEN** each detail is formatted and separated

### Requirement: Column Constraints

The system SHALL respect column width constraints for output formatting.

#### Scenario: Continue mode
- **WHEN** column constraint is `Continue`
- **THEN** output continues on single lines without wrapping

#### Scenario: Complect mode
- **WHEN** column constraint is `Complect`
- **THEN** output is wrapped to fit within column width

#### Scenario: Truncate mode
- **WHEN** column constraint is `Truncate`
- **THEN** output is truncated at column boundary

### Requirement: Rich Integration

The system SHALL optionally integrate with the Rich library for enhanced
formatting.

#### Scenario: Rich available
- **WHEN** Rich is importable
- **THEN** colorized output is produced with styled prefixes

#### Scenario: Rich unavailable
- **WHEN** Rich is not importable
- **THEN** plain text output is produced without styling

#### Scenario: Rich explicitly disabled
- **WHEN** Rich is available but configuration disables it
- **THEN** plain text output is produced

### Requirement: Exception Traceback Rendering

The system SHALL render exception tracebacks with stack traces.

#### Scenario: Exception with traceback
- **WHEN** an `errorx` or `abortx` record is composited with an active exception
- **THEN** the traceback is rendered showing file, line, and code for each frame

#### Scenario: Chained exceptions
- **WHEN** an exception has `__cause__` or `__context__`
- **THEN** the chained exception is rendered with appropriate labeling

#### Scenario: Exception groups
- **WHEN** a `BaseExceptionGroup` is the summary
- **THEN** group members are rendered with nesting preservation
