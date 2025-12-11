.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Flavors
*******************************************************************************

``ictr`` comes with a set of standard message flavors to categorize your output.

Standard Flavors
===============================================================================

Each flavor has a specific semantic meaning and default presentation (color and
emoji).

.. testsetup:: flavors

    import ictr
    from io import StringIO
    from unittest.mock import patch
    capture = StringIO()
    
    class MockPrinter:
        def __init__(self, address, flavor):
            self.flavor = flavor
        def __call__(self, record):
            print(f"<{self.flavor}> {record.content.summary}", file=capture)
        def provide_textualization_control(self): return None

    def capture_factory(address, flavor):
        return MockPrinter(address, flavor)
    
    ictr = ictr.install(printer_factories=[capture_factory])

.. doctest:: flavors

    >>> # General information
    >>> ictr('note', address='doctest')('Configuration loaded.')
    
    >>> # Warnings
    >>> ictr('monition', address='doctest')('Disk space low.')
    
    >>> # Errors
    >>> ictr('error', address='doctest')('Connection failed.')
    
    >>> # Critical failures
    >>> ictr('abort', address='doctest')('System shutting down.')
    
    >>> # Successful operations
    >>> ictr('success', address='doctest')('Build completed.')
    
    >>> # Future/Pending tasks
    >>> ictr('future', address='doctest')('TODO: Refactor this.')
    
    >>> # Tips/Advice
    >>> ictr('advice', address='doctest')('Try using --verbose for more info.')

.. testcleanup:: flavors

    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')

Flavor Aliases
===============================================================================

For convenience, single-letter aliases are available for all standard flavors:

* ``n`` -> ``note``
* ``m`` -> ``monition``
* ``e`` -> ``error``
* ``a`` -> ``abort``
* ``s`` -> ``success``
* ``f`` -> ``future``
* ``v`` -> ``advice`` (advice/verbum)

.. testsetup:: aliases

    import ictr
    # Setup capture
    from io import StringIO
    from unittest.mock import patch
    capture = StringIO()
    
    class MockPrinter:
        def __init__(self, address, flavor):
            self.flavor = flavor
        def __call__(self, record):
            print(f"[{record.flavor}] {record.content.summary}", file=capture)
        def provide_textualization_control(self): return None

    def capture_factory(address, flavor):
        return MockPrinter(address, flavor)
    
    ictr = ictr.install(printer_factories=[capture_factory])

.. doctest:: aliases

    >>> ictr('n', address='doctest')('Note alias.')
    >>> ictr('e', address='doctest')('Error alias.')
    
    >>> # Output shows the resolved flavor
    >>> print(capture.getvalue().strip())
    [n] Note alias.
    [e] Error alias.

.. testcleanup:: aliases

    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')

Exception-Capturing Flavors
===============================================================================

Some flavors are designed to capture and display exceptions automatically.
These flavors have the suffix ``x``.

* ``errorx`` -> ``error`` with exception stack trace
* ``abortx`` -> ``abort`` with exception stack trace

See the :doc:`exceptions` example for detailed usage.
