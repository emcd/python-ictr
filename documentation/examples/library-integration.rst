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
Library Integration
*******************************************************************************

How to use ``ictr`` within a library without interfering with application-level
configuration.

Registering Addresses
===============================================================================

Libraries should use ``register_address`` to configure their own module addresses
without interfering with the application's configuration. The library can set defaults
for its modules, which the application can override.

.. code-block:: python

    # mylibrary/__init__.py
    import ictr

    # Register library-specific configuration
    ictr.register_address(
        'mylibrary',
        flavors={
            # Custom library flavors or overrides if needed
        }
    )

The ``register_address`` function is convenient for libraries because:

* If the application has installed ``ictr``, the library's configuration is registered
  with that dispatcher.
* If the application hasn't installed ``ictr``, a default dispatcher is created
  automatically.
* Either way, the library can emit messages without worrying about whether the
  application has initialized ``ictr``.

.. testsetup:: library

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

    # Simulate application install
    ictr_app = ictr.install( printer_factories = [ capture_factory ] )

.. doctest:: library

    >>> # Library registers its address configuration
    >>> config = ictr.register_address( 'mylib' )

    >>> # Application uses the dispatcher to emit messages
    >>> ictr_app( 'note', address = 'mylib' )( 'Library initialization complete.' )

    >>> # Verify the message was captured
    >>> print( capture.getvalue( ).strip( ) )
    [note] Library initialization complete.

.. testcleanup:: library

    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')