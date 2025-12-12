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
Trace Levels
*******************************************************************************

Hierarchical debugging using numeric trace levels.

Levels 0-9
===============================================================================

You can use integers 0 through 9 as flavors. These correspond to trace levels,
where higher numbers indicate deeper or more verbose tracing.

.. testsetup:: levels

    import sys
    import ictr
    # Enable all trace levels for this test
    ictr = ictr.install(
        printer_factories = [ sys.stdout ],
        trace_levels = { None: 9 }  # Enable up to level 9 globally
    )

.. doctest:: levels

    >>> ictr( 0, address = 'doctest' )( 'Top level trace.' )
    TRACE0|  Top level trace.
    >>> ictr( 1, address = 'doctest' )( 'Detailed trace.' )
      TRACE1|  Detailed trace.
    >>> ictr( 9, address = 'doctest' )( 'Very verbose trace.' )
                      TRACE9|  Very verbose trace.

.. testcleanup:: levels

    import builtins
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )

Filtering by Level
===============================================================================

You can control which trace levels are displayed by setting the ``trace_levels``
configuration. Messages with a level **less than or equal to** the configured
limit will be displayed.

.. testsetup:: filtering

    import sys
    import ictr
    # Set max trace level to 1
    ictr = ictr.install(
        printer_factories = [ sys.stdout ],
        trace_levels = { None: 1 }
    )

.. doctest:: filtering

    >>> ictr( 0, address = 'doctest' )( 'Level 0 visible' )
    TRACE0|  Level 0 visible
    >>> ictr( 1, address = 'doctest' )( 'Level 1 visible' )
      TRACE1|  Level 1 visible
    >>> ictr( 2, address = 'doctest' )( 'Level 2 hidden' )

.. testcleanup:: filtering

    import builtins
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )

Indentation
===============================================================================

By default, the standard printer indents trace messages based on their level
to visually represent the hierarchy.

* Level 0: No indentation
* Level 1: 2 spaces
* Level 2: 4 spaces
* ...and so on.
