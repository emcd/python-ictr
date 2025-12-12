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
Rich Formatting
*******************************************************************************

``ictr`` integrates with the `Rich <https://github.com/Textualize/rich>`_ library
for beautiful terminal output.

Automatic Detection
===============================================================================

If ``rich`` is installed, ``ictr`` will automatically use it for:

* Syntax highlighting of data structures
* Colorful tracebacks
* Emoji rendering

.. testsetup:: rich

    import ictr
    from io import StringIO

    capture = StringIO( )

    def capture_factory( address, flavor ):
        ''' Printer that captures Rich-formatted output. '''
        from ictr.standard import Printer
        return Printer( target = capture, force_color = True )

    ictr = ictr.install( printer_factories = [ capture_factory ] )

.. doctest:: rich

    >>> ictr( 'note', address = 'doctest' )( 'Rich output enabled.' )

    >>> # Complex data structures are pretty-printed
    >>> data = { 'a': 1, 'b': [ 2, 3 ] }
    >>> ictr( 'note', address = 'doctest' )( 'Data:', data )

    >>> # Verify output contains the message (may include ANSI color codes)
    >>> 'Rich output enabled' in capture.getvalue( )
    True

.. testcleanup:: rich

    import builtins
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )