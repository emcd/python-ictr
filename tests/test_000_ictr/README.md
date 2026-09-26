# Test Module Numbering

Test modules follow architectural layering with systematic numbering:

| Range | Layer | Examples |
|-------|-------|----------|
| 000-099 | Package Infrastructure | `test_000_package.py`, `test_010_base.py` |
| 100-199 | Core Data Structures and Protocols | `test_100_records.py`, `test_110_flavors.py`, `test_120_configuration.py`, `test_130_exceptions.py` |
| 200-299 | Protocols and Interfaces | `test_200_textualizers.py`, `test_210_printers.py` |
| 300-399 | Core Layer Implementations | `test_300_reporters.py`, `test_310_inspection.py` |
| 400-499 | Dispatcher Layer | `test_400_dispatchers.py` |
| 500-699 | Standard Recipe Implementations | `test_500_standard_core.py` through `test_550_standard_printers.py` |
| 700-799 | Integration Tests | `test_700_integration_basic.py` |

Lower numbers represent lower-level, foundational components. Higher numbers
represent higher-level, integrated functionality. 100-number blocks provide
room for growth within each category. Integration tests at 700+ validate
cross-layer functionality.

## Test Function Numbering

Within each test module, functions are numbered by component:

- **000-099**: Basic functionality tests for the module
- **100-199, 200-299, etc.**: Each function/class gets its own 100-number block
- **Increments of 10-20**: For closely related test variations within a block
