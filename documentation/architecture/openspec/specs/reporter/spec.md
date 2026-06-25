# Reporter

## Purpose

Reporters bridge the dispatcher and output layers. Each reporter instance binds
a specific address + flavor combination to a compositor and printer.
Active/inactive state controls whether messages are processed.

## Requirements

### Requirement: Message Emission

The system SHALL format and emit diagnostic messages through the reporter.

#### Scenario: String summary with details
- **WHEN** `reporter('Server started', port, host)` is called
- **THEN** a record is created with the summary and details, then printed

#### Scenario: Exception summary
- **WHEN** `reporter(exception, 'context')` is called
- **THEN** a record is created with the exception as summary and context as detail

#### Scenario: Inactive reporter
- **WHEN** `reporter('message')` is called on an inactive reporter
- **THEN** no output is produced

### Requirement: Active State Control

The system SHALL control reporter activity based on flavor activation and
trace level configuration.

#### Scenario: Active flavor reporter
- **WHEN** a reporter is created for an active flavor
- **THEN** the reporter's `active` flag is True

#### Scenario: Inactive flavor reporter
- **WHEN** a reporter is created for a flavor not in the active set
- **THEN** the reporter's `active` flag is False

#### Scenario: Trace level reporter active
- **WHEN** a reporter is created for trace level 3 and max level is 5
- **THEN** the reporter's `active` flag is True

#### Scenario: Trace level reporter inactive
- **WHEN** a reporter is created for trace level 7 and max level is 5
- **THEN** the reporter's `active` flag is False

### Requirement: Record Creation

The system SHALL create structured records from reporter arguments.

#### Scenario: Message content creation
- **WHEN** `reporter('summary', detail1, detail2)` is called
- **THEN** a `Record` is created with `MessageContent(summary='summary', details=(detail1, detail2))`

#### Scenario: Record identity
- **WHEN** a record is created
- **THEN** it contains the reporter's address and flavor

### Requirement: Multi-Printer Output

The system SHALL support routing output to multiple printers.

#### Scenario: Multiple printers configured
- **WHEN** a reporter has multiple printers
- **THEN** each printer receives the formatted output
