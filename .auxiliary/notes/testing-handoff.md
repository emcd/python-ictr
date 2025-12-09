# Testing Handoff

**Date**: 2025-12-09
**Status**: Ready for test implementation

## Overview

This document provides all necessary context for implementing tests for the `ictr` package. The test plan has been created and is ready for implementation.

## Essential References

### Test Plan and Strategy

- **Comprehensive test plan**: `documentation/architecture/testplans/comprehensive-coverage.rst`
  - Coverage analysis (37% current → 100% target)
  - Test module numbering scheme
  - Detailed test descriptions per module
- **Test organization summary**: `documentation/architecture/testplans/summary.rst`

### Development Practices

These files define code style and patterns that tests must follow:

- `.auxiliary/instructions/practices.rst` - General development principles
- `.auxiliary/instructions/practices-python.rst` - Python-specific patterns
- `.auxiliary/instructions/nomenclature.rst` - Naming conventions
- `.auxiliary/instructions/style.rst` - Code formatting standards
- `.auxiliary/instructions/validation.rst` - Quality assurance requirements

### Architecture Documentation

- `documentation/prd.rst` - Product requirements and acceptance criteria
- `documentation/architecture/summary.rst` - System architecture overview
- `documentation/architecture/filesystem.rst` - Package structure
- `documentation/architecture/decisions/` - Architectural decision records

### External Reference

- `/home/me/src/python-icecream-truck/documentation/` - Sister project with similar patterns

## Existing Test Infrastructure

The `tests/test_000_ictr/` directory contains foundational test patterns:

- `__.py` - Common test utilities (module discovery, caching import helper)
- `conftest.py` - Pytest fixtures
- `test_000_package.py` - Package sanity tests (parametrized by module)
- `test_010_base.py` - Common imports validation

**Key patterns to follow**:
- Use `from . import __` for common utilities
- Use `@pytest.mark.parametrize` for data-driven tests
- Each test function has a docstring describing what it tests
- Test numbering within files: `test_000_*`, `test_100_*`, etc.

## Working Examples

Three exploratory scripts in `.auxiliary/scribbles/` demonstrate working usage:

### `01_basic_flavors.py`
- All standard flavors (note, monition, error, abort, future, success, advice)
- Single-letter aliases (n, m, e, a, f, s, v)
- MessageContent with summary and details
- Exception capture with errorx/abortx

### `02_trace_levels.py`
- Hierarchical trace levels 0-9
- Automatic indentation (2 spaces per level)
- Trace level filtering via configuration

### `03_exception_inclusion.py`
- Automatic exception capture
- Stack trace rendering
- Exception chaining (__cause__ and __context__)

Use these as integration test references and for understanding the public API.

## Current Architecture

**Layer flow**: Dispatcher → Reporter → Compositor → Printer

**Key modules**:
| Module | Purpose |
|--------|---------|
| `dispatchers.py` | Entry point, configuration hierarchy, reporter management |
| `reporters.py` | Formats and prints messages via compositor and printers |
| `textualizers.py` | Compositor/Linearizer/Introducer protocols |
| `printers.py` | Printer protocol, TextualizationControl, helper functions |
| `records.py` | Record, MessageContent, MessageSummary, MessageDetail types |
| `flavors.py` | Flavor dataclass and FlavorSpecification |
| `configuration.py` | Configuration and State classes |
| `exceptions.py` | Package-specific exceptions |
| `inspection.py` | Exception inspection utilities |

**Standard implementations** (`ictr.standard.*`):
| Module | Purpose |
|--------|---------|
| `flavors.py` | Standard flavor definitions (note, error, etc.) |
| `compositors.py` | Default compositor implementation |
| `linearizers.py` | Plain and Rich linearizers |
| `introducers.py` | Plain and Rich introducers |
| `printers.py` | Stream-based printer |

## Implementation Priority

Based on coverage gaps and architectural importance:

### Phase 1: Foundations (test_100-199)
Start here to establish core data type testing:
1. `test_100_records.py` - Record, MessageContent types
2. `test_110_flavors.py` - Flavor and FlavorSpecification
3. `test_120_configuration.py` - Configuration hierarchy
4. `test_130_exceptions.py` - Package exceptions

### Phase 2: Protocols (test_200-299)
Test the abstract interfaces:
1. `test_200_textualizers.py` - Compositor, Linearizer, Introducer protocols
2. `test_210_printers.py` - Printer protocol, TextualizationControl

### Phase 3: Core Implementations (test_300-399)
1. `test_300_reporters.py` - Reporter class
2. `test_310_inspection.py` - Exception inspection

### Phase 4: Dispatchers (test_400-499) - Highest Priority Gap
Currently at 24% coverage with 161 lines uncovered:
1. `test_400_dispatchers.py` - Core dispatcher tests
2. `test_410_installation.py` - install_builtins, register_module
3. `test_420_hierarchy.py` - Module address resolution

### Phase 5: Standard Implementations (test_500-699)
1. `test_500_standard_flavors.py` - Standard flavor definitions
2. `test_510_standard_introducers.py` - Plain/Rich introducers
3. `test_520_standard_linearizers.py` - Plain/Rich linearizers
4. `test_530_standard_compositors.py` - Default compositor
5. `test_540_standard_printers.py` - Stream printer

### Phase 6: Integration (test_700-799)
1. `test_700_endtoend.py` - Full message flow
2. `test_710_multiprinter.py` - Multiple printer scenarios
3. `test_720_threading.py` - Concurrent access
4. `test_730_acceptance.py` - PRD acceptance criteria

## Recent Changes to Note

The following architectural changes were made recently:

1. **Textualizer → Compositor rename**: The rendering component is now called "Compositor" (assembles formatted output). Related types: `CompositorConfiguration`, `CompositorState`, `CompositorFactory`.

2. **Linearizer interface extraction**: `LinearizerConfiguration` and `LinearizerState` are now separate from compositor configuration.

3. **TextualizationControl**: Runtime context passed from Printer to Compositor at render time. Includes `charset`, `colorize`, `columns_max_calculator`.

4. **Multi-printer support**: Reporter now supports multiple printers via `printers: Printers` (was `printer: Printer`). Dispatcher accepts `printer_factories: PrinterFactoriesUnion`.

5. **Charset detection**: Standard printer now detects charset from stream's `encoding` attribute.

## Running Tests

```bash
# Run all tests
hatch --env develop run testers

# Run with coverage
hatch --env develop run testers --cov=ictr --cov-report=term-missing

# Run specific test file
hatch --env develop run testers tests/test_000_ictr/test_000_package.py

# Run tests matching pattern
hatch --env develop run testers -k "dispatcher"
```

## Quality Checks

Before committing tests:

```bash
# Type checking
hatch --env develop run linters:pyright

# Linting
hatch --env develop run linters:ruff

# All linters
hatch --env develop run linters
```

## Notes

- Tests should be self-contained and not depend on execution order
- Use fixtures for common setup (dispatchers, printers, etc.)
- Mock external dependencies (Rich, colorama) for isolated unit tests
- Integration tests can use real implementations
- Follow the existing test file header format (Apache 2.0 license block)
