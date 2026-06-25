# Records

## Purpose

Records are the central data structure flowing through the ictr pipeline. They
carry all information needed for formatting and output in an immutable structure.

## Requirements

### Requirement: Message Content Structure

The system SHALL support structured message content with summary and details.

#### Scenario: String summary
- **WHEN** a message is created with a string summary
- **THEN** the record contains `MessageContent` with the string as summary

#### Scenario: Exception summary
- **WHEN** a message is created with an exception as summary
- **THEN** the record contains `MessageContent` with the exception as summary

#### Scenario: Multiple details
- **WHEN** a message is created with multiple detail arguments
- **THEN** the record contains `MessageContent` with details as a tuple

#### Scenario: Empty details
- **WHEN** a message is created with only a summary
- **THEN** the record contains `MessageContent` with an empty details tuple

### Requirement: Record Identity

The system SHALL identify each record with its source address and flavor.

#### Scenario: Address identification
- **WHEN** a record is created by a reporter
- **THEN** the record contains the reporter's address

#### Scenario: Flavor identification
- **WHEN** a record is created by a reporter
- **THEN** the record contains the reporter's flavor (string or int)

### Requirement: Record Immutability

The system SHALL create immutable records that cannot be modified after creation.

#### Scenario: Immutable content
- **WHEN** a `Record` is created
- **THEN** its fields cannot be reassigned

#### Scenario: Immutable content details
- **WHEN** a `MessageContent` is created
- **THEN** its summary and details cannot be modified
