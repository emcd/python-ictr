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

    import sys
    import ictr
    ictr = ictr.install( printer_factories = [ sys.stdout ] )

.. doctest:: flavors

    >>> # General information
    >>> ictr( 'note', address = 'doctest' )( 'Configuration loaded.' )
    NOTE|  Configuration loaded.

    >>> # Warnings
    >>> ictr( 'monition', address = 'doctest' )( 'Disk space low.' )
    MONITION|  Disk space low.

    >>> # Errors
    >>> ictr( 'error', address = 'doctest' )( 'Connection failed.' )
    ERROR|  Connection failed.

    >>> # Critical failures
    >>> ictr( 'abort', address = 'doctest' )( 'System shutting down.' )
    ABORT|  System shutting down.

    >>> # Successful operations
    >>> ictr( 'success', address = 'doctest' )( 'Build completed.' )
    SUCCESS|  Build completed.

    >>> # Future/Pending tasks
    >>> ictr( 'future', address = 'doctest' )( 'TODO: Refactor this.' )
    FUTURE|  TODO: Refactor this.

    >>> # Tips/Advice
    >>> ictr( 'advice', address = 'doctest' )( 'Try using --verbose for more info.' )
    ADVICE|  Try using --verbose for more info.

.. testcleanup:: flavors

    import builtins
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )

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

    import sys
    import ictr
    ictr = ictr.install( printer_factories = [ sys.stdout ] )

.. doctest:: aliases

    >>> ictr( 'n', address = 'doctest' )( 'Note alias.' )
    NOTE|  Note alias.
    >>> ictr( 'e', address = 'doctest' )( 'Error alias.' )
    ERROR|  Error alias.

.. testcleanup:: aliases

    import builtins
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )

Exception-Capturing Flavors
===============================================================================

Some flavors are designed to capture and display exceptions automatically.
These flavors have the suffix ``x``.

* ``errorx`` -> ``error`` with exception stack trace
* ``abortx`` -> ``abort`` with exception stack trace

See the :doc:`exceptions` example for detailed usage.
