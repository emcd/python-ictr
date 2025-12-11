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
Quickstart
*******************************************************************************

Installation and basic usage of the Icecream Truck (ictr) library.

Basic Setup
===============================================================================

The simplest way to use ``ictr`` is to install it into the Python builtins. This
makes the ``ictr`` dispatcher available in every module without needing imports.

.. code-block:: python

    import ictr

    # Install 'ictr' into builtins (default alias is 'ictr')
    ictr.install()

Once installed, you can use the ``ictr`` dispatcher to create reporters for
various message "flavors".

.. testsetup:: quickstart

    import ictr
    from io import StringIO
    import sys
    from unittest.mock import patch

    # Capture output for doctest verification
    capture = StringIO()
    
    # Mock printer that satisfies protocol
    class MockPrinter:
        def __init__( self, address, flavor ):
            self.address = address
            self.flavor = flavor
        def __call__( self, record ):
            # Simple simulation of standard printer for doctest
            print( f"{record.content.summary}", file = capture )
        def provide_textualization_control( self ):
            return None

    def capture_factory( address, flavor ):
        return MockPrinter( address, flavor )

    # Install with capture printer
    ictr = ictr.install( printer_factories = [ capture_factory ] )

.. doctest:: quickstart

    >>> # Create a reporter for the 'note' flavor and print a message
    >>> ictr( 'note', address = 'doctest' )( 'System initialized.' )

    >>> # Create a reporter for the 'error' flavor
    >>> ictr( 'error', address = 'doctest' )( 'Something went wrong.' )

.. testcleanup:: quickstart

    # Reset builtins to avoid side effects
    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')

One-Liners
===============================================================================

You can chain the dispatcher call and the reporter call for succinct logging:

.. testsetup:: oneliners

    import ictr
    from io import StringIO
    from unittest.mock import patch
    capture = StringIO( )

    class MockPrinter:
        def __init__( self, address, flavor ):
            self.flavor = flavor
        def __call__( self, record ):
            print( f"[{self.flavor}] {record.content.summary}", file = capture )
        def provide_textualization_control( self ):
            return None

    def capture_factory( address, flavor ):
        return MockPrinter( address, flavor )

    ictr = ictr.install( printer_factories = [ capture_factory ] )

.. doctest:: oneliners

    >>> ictr( 'note', address = 'doctest' )( 'Processing file...' )
    >>> ictr( 'success', address = 'doctest' )( 'File processed successfully.' )

.. testcleanup:: oneliners

    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')

Explicit Address
===============================================================================

By default, ``ictr`` infers the calling module's address. You can override this
if needed:

.. testsetup:: address

    import ictr
    from io import StringIO
    from unittest.mock import patch
    capture = StringIO( )

    class MockPrinter:
        def __init__( self, address, flavor ):
            self.address = address
        def __call__( self, record ):
            print( f"[{self.address}] {record.content.summary}", file = capture )
        def provide_textualization_control( self ):
            return None

    def capture_factory( address, flavor ):
        return MockPrinter( address, flavor )

    ictr = ictr.install( printer_factories = [ capture_factory ] )

.. doctest:: address

    >>> ictr( 'note', address = 'my.custom.component' )( 'Starting component...' )

    >>> # Verify output contains custom address
    >>> print( capture.getvalue( ).strip( ) )
    [my.custom.component] Starting component...

.. testcleanup:: address

    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')
