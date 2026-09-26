# Configuration

## Purpose

Hierarchical configuration following Python package structure. Configuration
inherits through the package hierarchy with address-specific overrides.

## Requirements

### Requirement: Hierarchical Configuration Inheritance

The system SHALL support configuration inheritance following Python package
structure.

#### Scenario: Exact address match
- **WHEN** configuration is resolved for `myapp.subsystem.module`
- **THEN** exact match `myapp.subsystem.module` configuration is used if present

#### Scenario: Parent package inheritance
- **WHEN** configuration is resolved for `myapp.subsystem.module` and no exact match exists
- **THEN** `myapp.subsystem` configuration is used if present

#### Scenario: Grandparent package inheritance
- **WHEN** no parent configuration exists
- **THEN** `myapp` configuration is used if present

#### Scenario: Global fallback
- **WHEN** no ancestor configuration exists
- **THEN** global (None key) configuration is used

### Requirement: Address-Specific Configuration

The system SHALL support per-address configuration for compositor factories
and flavor registries.

#### Scenario: Address compositor factory
- **WHEN** `AddressConfiguration(compositor_factory=my_factory)` is registered
- **THEN** messages for that address use the custom compositor factory

#### Scenario: Address flavor configuration
- **WHEN** `AddressConfiguration(flavors={note: FlavorConfiguration(...)})` is registered
- **THEN** the `note` flavor for that address uses the custom configuration

### Requirement: Flavor-Specific Configuration

The system SHALL support per-flavor configuration for compositor factories.

#### Scenario: Flavor compositor factory
- **WHEN** `FlavorConfiguration(compositor_factory=my_factory)` is configured for `error`
- **THEN** `error` messages use the custom compositor factory

#### Scenario: Inherited flavor configuration
- **WHEN** no flavor-specific configuration exists
- **THEN** the address-level or global compositor factory is used

### Requirement: Configuration Immutability

The system SHALL use immutable configuration objects after creation.

#### Scenario: Accretive address registry
- **WHEN** an address is registered in `AddressesConfigurationsRegistry`
- **THEN** it cannot be removed (accretive/append-only)

#### Scenario: Immutable configuration objects
- **WHEN** `DispatcherConfiguration`, `AddressConfiguration`, or `FlavorConfiguration` is created
- **THEN** fields cannot be modified after creation
