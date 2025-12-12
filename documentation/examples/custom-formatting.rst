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
Custom Formatting
*******************************************************************************

You can customize how messages are rendered and delivered.

Custom Printers
===============================================================================

You can send output to files, loggers, or other destinations by providing a
custom printer factory.

.. testsetup:: custom_printer

    import ictr
    from io import StringIO

    class FilePrinter:
        ''' Custom printer that writes to a file with simple formatting. '''

        def __init__( self, file ):
            self.file = file

        def __call__( self, record ):
            self.file.write( f"LOG: {record.content.summary}\n" )

        def provide_textualization_control( self ):
            return None

    capture = StringIO( )

    def my_factory( address, flavor ):
        return FilePrinter( capture )

    ictr = ictr.install( printer_factories = [ my_factory ] )

.. doctest:: custom_printer

    >>> ictr( 'note', address = 'doctest' )( 'Custom log message.' )

    >>> print( capture.getvalue( ).strip( ) )
    LOG: Custom log message.

.. testcleanup:: custom_printer

    import builtins
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )
