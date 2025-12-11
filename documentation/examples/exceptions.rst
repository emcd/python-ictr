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
Exceptions
*******************************************************************************

Handling and displaying exceptions with ``ictr``.

Automatic Capture
===============================================================================

Use the ``errorx`` (or alias ``ex``) flavor to automatically capture and display
active exceptions.

.. testsetup:: capture

    import ictr as ictr_module
    from io import StringIO
    from unittest.mock import patch
    import sys
    
    capture = StringIO()
    
    class MockPrinter:
        def __init__( self, address, flavor ):
            pass
        def __call__( self, record ):
            pass

        def provide_textualization_control( self ):
            return ictr_module.TextualizationControl(
                columns_max_calculator = 80,
                colorize = False
            )

    class StringPrinter:
        def __init__( self, address, flavor ):
            pass
        def __call__( self, text ):
            print( text, file = capture )
        def provide_textualization_control( self ):
            return ictr_module.TextualizationControl( colorize = False )

    def capture_factory( address, flavor ):
        return StringPrinter( address, flavor )

    ictr = ictr_module.install( printer_factories = [ capture_factory ] )

.. doctest:: capture

    >>> try:
    ...     1 / 0
    ... except ZeroDivisionError:
    ...     ictr( 'errorx', address = 'doctest' )( 'Calculation failed.' )

    >>> # Verify output contains exception info
    >>> output = capture.getvalue( )
    >>> '[ZeroDivisionError] division by zero' in output
    True
    >>> 'Calculation failed.' in output
    True

.. testcleanup:: capture

    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')

Tracebacks
===============================================================================

You can enable stack traces for any flavor via configuration, but ``errorx`` and
``abortx`` have them enabled by default.

.. testsetup:: traceback

    import ictr as ictr_module
    from io import StringIO
    from unittest.mock import patch
    capture = StringIO()
    
    class StringPrinter:
        def __init__(self, address, flavor): pass
        def __call__(self, text): print(text, file=capture)
        def provide_textualization_control(self):
            return ictr_module.TextualizationControl(colorize=False)

    def capture_factory(address, flavor): return StringPrinter(address, flavor)
    
    ictr = ictr_module.install(printer_factories=[capture_factory])

.. doctest:: traceback

    >>> def faulty_function():
    ...     raise ValueError("Invalid value")
    
    >>> try:
    ...     faulty_function()
    ... except ValueError:
    ...     ictr('errorx', address='doctest')('Operation failed.')

    >>> output = capture.getvalue()
    >>> '[ValueError] Invalid value' in output
    True
    >>> 'faulty_function()' in output
    True

.. testcleanup:: traceback

    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')
