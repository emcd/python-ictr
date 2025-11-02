# Executing Library Integration

## Overview

The `executing` library retrieves information about what a Python frame is currently executing, particularly the AST node being processed. This is the foundation for inspection capabilities in ictr v2.

## Core API Usage

### Getting the AST Node

```python
import executing
node = executing.Source.executing(frame).node
```

The returned `node` is an AST object or `None` if identification fails. The same instance is always returned for repeated calls at identical execution points.

### Alternative Approaches

- Pass traceback objects directly to `Source.executing(tb)` rather than `tb_frame` for accuracy
- Use `Source.for_frame(frame)` to obtain a Source instance
- Call `code_qualname()` to retrieve the current function's `__qualname__`

## Supported AST Node Types

The library identifies nodes for:
- `Call` (function calls)
- `Attribute` (attribute access)
- `Subscript` (indexing)
- `BinOp` (binary operations, excluding `and`/`or`)
- `UnaryOp` (unary operations)
- `Compare` (comparisons, excluding chains)

## Important Caveats

**Reliability**: When identification succeeds, accuracy is guaranteed. The library validates through extensive property testing across real code.

**Optional dependency**: Extracting source code text requires separately installing `asttokens` and calling methods like `.text()` or `.asttokens()`.

**Node identification limitations**: It works in almost all cases for supported nodes, but identification occasionally returns `None`.

## How Icecream Uses Executing

### Core Integration

```python
# Get the call site
callNode = Source.executing(callFrame).node
assert isinstance(callNode, ast.Call)

# Get source text for each argument
source = Source.for_frame(callFrame)
argStrs = [source.get_text_with_indentation(arg) for arg in callNode.args]

# Zip with actual values
pairs = list(zip(argStrs, args))
# Result: [('x', 42), ('message', 'hello'), ...]
```

### Process Flow

1. Retrieve the AST node at the current execution point
2. Extract `callNode.args` (the function arguments as AST nodes)
3. Use `source.get_text_with_indentation(arg)` to get source text for each argument
4. Pair extracted names with evaluated values

## Our Implementation Strategy

### Literal Detection (Option B)

For `.inspect()` to handle literals vs. variables intelligently:

**Literals** (don't inspect - pass through as-is):
- `ast.Constant` - string/number/boolean literals
- `ast.JoinedStr` - f-strings (pre-formatted)

**Variables** (inspect - extract names):
- `ast.Name` - simple variable references

**Expressions** (inspect - extract source):
- `ast.Call`, `ast.Attribute`, `ast.Subscript`, `ast.BinOp`, etc.

### Proposed Implementation

```python
import ast
import inspect
from executing import Source

def inspect_call(*args) -> list[tuple[str | None, Any]]:
    """
    Extract variable names for args using executing.

    Returns list of (name, value) pairs where:
    - name is None for literals (they pass through unnamed)
    - name is source text for variables/expressions
    - name is '???' for unresolvable arguments (fallback)
    """
    frame = inspect.currentframe().f_back.f_back  # Adjust depth as needed
    source = Source.for_frame(frame)
    node = source.executing(frame).node

    if node is None or not isinstance(node, ast.Call):
        # Fallback: couldn't identify call site
        return [('???', arg) for arg in args]

    results = []
    for arg_node, arg_value in zip(node.args, args):
        # Check if it's a literal
        if isinstance(arg_node, (ast.Constant, ast.JoinedStr)):
            # Literal - pass through without name
            results.append((None, arg_value))
        else:
            # Variable or expression - get source text
            try:
                arg_text = source.get_text_with_indentation(arg_node)
                results.append((arg_text, arg_value))
            except Exception:
                # Fallback for unresolvable
                results.append(('???', arg_value))

    return results
```

### Usage Example

```python
# In user code:
filename = "/tmp/data.txt"
bytes_read = 1024

# Mixed literals and variables
ictr('io').inspect('Reading file', filename, bytes_read)
```

Would produce:
```python
[
    (None, 'Reading file'),        # Literal string - no name
    ('filename', '/tmp/data.txt'), # Variable - inspected
    ('bytes_read', 1024)           # Variable - inspected
]
```

The formatter would render this as:
```
IO| 'Reading file', filename: '/tmp/data.txt', bytes_read: 1024
```

## Implementation Decisions

### 1. Frame Depth

**Context**: Only `Reporter.inspect()` needs inspection, not `Reporter.__call__()`.

Call chain: `user_code → ictr(flavor) → Reporter.inspect() → inspect_call()`

**Question**: Should we exclude stdlib/builtins frames for async scenarios (coroutines, etc.)?

**Decision**: Use simple fixed offset initially.

**Rationale**:
- Most common case is synchronous - fixed frame offset works fine
- Async overhead is usually minimal and predictable
- Stack filtering is complex and fragile (how to define "stdlib"? compiled extensions?)
- `executing` will gracefully fail (return `None`) if given wrong frame, triggering `???` fallback
- Can add smarter logic later if async scenarios prove problematic

**Implementation**: Use `frame.f_back.f_back` to skip `Reporter.inspect()` and `inspect_arguments()`.

**Future consideration**: If async issues arise, could use `inspect.stack()` with filtering to find first frame outside ictr module. But defer until needed.

### 2. F-String Handling

**Decision**: Treat f-strings as literals (already formatted).

```python
x = 42
ictr('debug').inspect(f"Value: {x}")  # Treated as literal, not inspected
# Output: DEBUG| 'Value: 42'  (not "f'Value: {x}': 'Value: 42'")
```

### 3. Fallback Behavior

**Decision**: Mark unresolvable arguments with `???`.

When `executing` fails to identify the call site or extract text:
```python
# Output: DEBUG| ???: <value>, ???: <value>
```

This makes it clear that inspection failed while still showing values.

### 4. Performance

**Deferred**: Don't optimize until we see a need.

The executing docs suggest caching already happens. We'll profile later if needed.

### 5. Multiline Calls

**Question**: How to display multiline expressions?

```python
ictr('debug').inspect(
    some_long_variable_name,
    another_variable,
)
```

**Hypothesis**: `get_text_with_indentation()` handles this, returning the full expression text.

**To verify**: Test with multiline expressions and see what we get.

**Consideration**: Should we show the full multiline context in output, or normalize/strip whitespace?

## Dependencies

- `executing` - core functionality
- `asttokens` - required by executing for source text extraction
- Both should be added to project dependencies

## Prototype Results

✓ **Prototype completed** in `.auxiliary/scribbles/`

### Key Findings

1. **AST Token API**: Must use `source.asttokens().get_text(node)`, not the icecream-specific `get_text_with_indentation()`.

2. **Frame Handling**: Wrapper functions must explicitly pass their caller's frame via `_frame` parameter to avoid inspecting the wrapper's call instead of the user's call.

   ```python
   def wrapper(*args):
       caller_frame = inspect.currentframe().f_back
       return inspect_arguments(*args, _frame=caller_frame)
   ```

3. **Literal Detection**: Works perfectly with `isinstance(arg_node, (ast.Constant, ast.JoinedStr))`.
   - String literals: `ast.Constant`
   - F-strings: `ast.JoinedStr` (treated as already-formatted literals)

4. **Multiline Calls**: `asttokens.get_text()` correctly extracts variable names from multiline calls without extra whitespace issues.

5. **Expression Extraction**: Complex expressions like `data['key']`, `len(items)`, `result * 2` extract correctly as source text.

### Test Results

All test cases pass:
- ✓ Simple variables
- ✓ Literals (strings, numbers, booleans, None)
- ✓ Mixed literals and variables
- ✓ F-strings (treated as literals)
- ✓ Expressions (dict access, function calls, arithmetic)
- ✓ Multiline calls
- ✓ Formatting output

### For Real Implementation

In `Reporter.inspect()`, the pattern will be:

```python
class Reporter:
    def inspect(self, *args, **kwargs):
        # Get our caller's frame to pass to inspection
        frame = inspect.currentframe().f_back
        pairs = inspect_call(*args, _frame=frame, **kwargs)
        # Format and output...
```

This ensures the inspection looks at the user's call site, not Reporter's internal call.
