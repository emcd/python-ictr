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

    import sys
    import ictr
    ictr = ictr.install( printer_factories = [ sys.stdout ] )

.. doctest:: quickstart

    >>> # Create a reporter for the 'note' flavor and print a message
    >>> ictr( 'note', address = 'doctest' )( 'System initialized.' )
    NOTE|  System initialized.

    >>> # Create a reporter for the 'error' flavor
    >>> ictr( 'error', address = 'doctest' )( 'Something went wrong.' )
    ERROR|  Something went wrong.

.. testcleanup:: quickstart

    import builtins
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )

Explicit Address
===============================================================================

By default, ``ictr`` infers the calling module's name as the address. You can
override this to use a custom address, which is useful for organizing output
by component or for per-address configuration.

.. testsetup:: address

    import sys
    import ictr
    ictr = ictr.install( printer_factories = [ sys.stdout ] )

.. doctest:: address

    >>> ictr( 'note', address = 'my.custom.component' )( 'Starting component...' )
    NOTE|  Starting component...

.. testcleanup:: address

    import builtins
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )
