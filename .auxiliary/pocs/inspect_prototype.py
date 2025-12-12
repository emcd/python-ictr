"""Prototype implementation of inspection using executing library.

This is a proof-of-concept to understand how executing works and test
various argument patterns.
"""

import ast
import inspect
from typing import Any


# Check if executing is available
try:
    from executing import Source
    EXECUTING_AVAILABLE = True
except ImportError:
    EXECUTING_AVAILABLE = False
    print("WARNING: 'executing' not installed. Install with: pip install executing asttokens")


def inspect_arguments(*args, debug=False, _frame=None) -> list[tuple[str | None, Any]]:
    """Extract variable names for arguments using executing.

    Returns list of (name, value) pairs where:
    - name is None for literals (they pass through unnamed)
    - name is source text for variables/expressions
    - name is '???' for unresolvable arguments

    Args:
        *args: Arguments to inspect
        debug: If True, print debug information
        _frame: Internal parameter - frame to inspect (for wrappers)

    Returns:
        List of (name, value) tuples
    """
    if not EXECUTING_AVAILABLE:
        if debug:
            print("DEBUG: executing not available")
        return [('???', arg) for arg in args]

    # Get the caller's frame
    if _frame is not None:
        # Frame explicitly provided (e.g., by a wrapper function)
        caller_frame = _frame
    else:
        # Skip inspect_arguments itself to get to the actual caller
        frame = inspect.currentframe()
        if frame is None:
            if debug:
                print("DEBUG: currentframe is None")
            return [('???', arg) for arg in args]

        caller_frame = frame.f_back
        if caller_frame is None:
            if debug:
                print("DEBUG: caller_frame is None")
            return [('???', arg) for arg in args]

    if debug:
        print(f"DEBUG: Got frames, about to call Source.for_frame on caller_frame")

    try:
        source = Source.for_frame(caller_frame)
        if debug:
            print(f"DEBUG: Got source")
        node = source.executing(caller_frame).node
        if debug:
            print(f"DEBUG: Got node: {node} (type: {type(node).__name__ if node else 'None'})")

        if node is None:
            if debug:
                print(f"DEBUG: node is None")
            return [('???', arg) for arg in args]

        if not isinstance(node, ast.Call):
            if debug:
                print(f"DEBUG: node is {type(node).__name__}, not Call")
            return [('???', arg) for arg in args]

        if debug:
            print(f"DEBUG: node is Call, processing {len(node.args)} args")

        results = []
        for i, (arg_node, arg_value) in enumerate(zip(node.args, args)):
            if debug:
                print(f"DEBUG: Processing arg {i}: node type = {type(arg_node).__name__}")
            # Check if it's a literal
            if isinstance(arg_node, (ast.Constant, ast.JoinedStr)):
                # Literal - pass through without name
                if debug:
                    print(f"DEBUG: Arg {i} is literal")
                results.append((None, arg_value))
            else:
                # Variable or expression - get source text
                if debug:
                    print(f"DEBUG: Arg {i} is variable/expression, getting text")
                try:
                    # Get text using asttokens
                    atok = source.asttokens()
                    arg_text = atok.get_text(arg_node)
                    if debug:
                        print(f"DEBUG: Arg {i} text: {arg_text!r}")
                    results.append((arg_text, arg_value))
                except Exception as e:
                    # Fallback for unresolvable
                    if debug:
                        print(f"DEBUG: Arg {i} failed to get text: {e}")
                    results.append(('???', arg_value))

        return results

    except Exception as e:
        # Something went wrong - fallback
        if debug:
            print(f"DEBUG: Exception during inspection: {e}")
            import traceback
            traceback.print_exc()
        return [('???', arg) for arg in args]


def format_inspection(pairs: list[tuple[str | None, Any]]) -> str:
    """Format inspection results for display.

    Args:
        pairs: List of (name, value) tuples from inspect_arguments

    Returns:
        Formatted string
    """
    parts = []
    for name, value in pairs:
        if name is None:
            # Literal - just show repr
            parts.append(repr(value))
        elif name == '???':
            # Unresolved - mark it
            parts.append(f"???: {value!r}")
        else:
            # Variable/expression - show name: value
            parts.append(f"{name}: {value!r}")

    return ", ".join(parts)


def demo_inspect(*args, **kwargs):
    """Demo function that shows inspection results.

    This simulates what Reporter.inspect() would do.
    """
    debug = kwargs.pop('debug', False)
    # Pass our caller's frame so inspect_arguments looks at the right call site
    caller_frame = inspect.currentframe().f_back
    pairs = inspect_arguments(*args, debug=debug, _frame=caller_frame)
    output = format_inspection(pairs)
    print(f"DEMO| {output}")


if __name__ == "__main__":
    print("=== Inspection Prototype Demo ===\n")

    # Test 1: Simple variables
    print("Test 1: Simple variables")
    x = 42
    y = "hello"
    demo_inspect(x, y)
    print()

    # Test 2: Mixed literals and variables
    print("Test 2: Mixed literals and variables")
    filename = "/tmp/data.txt"
    bytes_read = 1024
    demo_inspect('Reading file', filename, bytes_read)
    print()

    # Test 3: Literals only
    print("Test 3: Literals only")
    demo_inspect('error', 'Something went wrong', 42)
    print()

    # Test 4: F-strings
    print("Test 4: F-strings (should be treated as literals)")
    count = 5
    demo_inspect(f"Processed {count} items")
    print()

    # Test 5: Expressions
    print("Test 5: Expressions")
    data = {'key': 'value'}
    items = [1, 2, 3]
    demo_inspect(data['key'], len(items), items[0])
    print()

    # Test 6: Multiline call
    print("Test 6: Multiline call")
    some_long_variable_name = "long value"
    another_variable = 999
    demo_inspect(
        some_long_variable_name,
        another_variable,
    )
    print()

    # Test 7: Complex expression
    print("Test 7: Complex expression")
    result = 10 + 20
    demo_inspect(10 + 20, result, result * 2)
    print()
