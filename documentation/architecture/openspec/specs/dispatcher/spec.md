# Dispatcher

## Purpose

The dispatcher is the entry point for diagnostic calls. It manages reporter
selection, activation control, and configuration inheritance. Provides
attribute-based access (`ctrl.note(...)`) and caches reporter instances per
address + flavor combination.

## Requirements

### Requirement: Global Builtin Installation

The system SHALL support optional installation into Python builtins for
convenient access from any module without explicit imports.

#### Scenario: Default installation
- **WHEN** `install()` is called with no arguments
- **THEN** a dispatcher is installed in builtins under the alias `ictr`

#### Scenario: Custom alias
- **WHEN** `install(alias='debug')` is called
- **THEN** the dispatcher is installed under the alias `debug`

#### Scenario: Builtin conflict
- **WHEN** `install()` is called and the alias already exists as a non-dispatcher attribute
- **THEN** an `AttributeNondisplacement` exception is raised

#### Scenario: Replace existing dispatcher
- **WHEN** `install()` is called and a dispatcher already exists under the alias
- **THEN** the existing dispatcher is replaced and address configurations are preserved

### Requirement: Address Registration

The system SHALL allow libraries to register address-specific configurations
without affecting application or other library settings.

#### Scenario: Library registration
- **WHEN** `register_address(name='mylib')` is called
- **THEN** the address is registered with default configuration on the global dispatcher

#### Scenario: Registration with custom configuration
- **WHEN** `register_address(name='mylib', configuration=AddressConfiguration(...))` is called
- **THEN** the address is registered with the provided configuration

#### Scenario: Auto-inferred address
- **WHEN** `register_address()` is called with no name
- **THEN** the invoking module's name is inferred as the address

### Requirement: Reporter Vending

The system SHALL produce and cache reporter instances for address + flavor
combinations.

#### Scenario: First request for a flavor
- **WHEN** `dispatcher('note')` is called for an address
- **THEN** a new reporter is created with resolved configuration and cached

#### Scenario: Subsequent request for same flavor
- **WHEN** `dispatcher('note')` is called again for the same address
- **THEN** the cached reporter is returned

#### Scenario: Trace level flavor
- **WHEN** `dispatcher(3)` is called
- **THEN** a reporter is produced with trace level 3 styling

### Requirement: Environment Variable Configuration

The system SHALL support configuration via environment variables for active
flavors and trace levels.

#### Scenario: Active flavors from environment
- **WHEN** `ICTR_ACTIVE_FLAVORS` is set to `note,error+mylib:success`
- **THEN** global active flavors include `note` and `error`, and `mylib` has `success`

#### Scenario: Trace levels from environment
- **WHEN** `ICTR_TRACE_LEVELS` is set to `3+mylib:5`
- **THEN** global trace level is 3 and `mylib` trace level is 5

#### Scenario: Disabled environment parsing
- **WHEN** `evname_active_flavors=None` is passed to `install()`
- **THEN** active flavors are not parsed from the environment
