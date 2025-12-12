# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Tests for standard linearizers. '''


from unittest.mock import MagicMock

import pytest

from absence import absent

from ictr import printers as _printers
from ictr.standard import core as _core
from ictr.standard import linearizers as _linearizers


def make_auxdata(
    colorize = False, columns_max = absent, exceptionscfg = None
):
    config = _core.LinearizerConfiguration()
    if exceptionscfg:
        config = _core.LinearizerConfiguration( exceptionscfg = exceptionscfg )
        
    control = MagicMock( spec = _printers.TextualizationControl )
    control.colorize = colorize
    control.columns_max = ( None if columns_max is absent else columns_max )
    
    return _core.LinearizerState(
        configuration = config,
        control = control,
        colorize = colorize,
        columns_max = columns_max
    )


class Test_000_Omni_Dispatch:
    ''' linearize_omni dispatch logic. '''

    def test_000_dispatch_plain( self ):
        ''' Dispatches to plain linearizers when colorize=False. '''
        auxdata = make_auxdata( colorize = False )
        # Should produce plain text
        lines = _linearizers.linearize_omni( auxdata, {'a': 1} )
        assert lines == ("{'a': 1}",)

    def test_010_dispatch_rich( self ):
        ''' Dispatches to rich linearizers when colorize=True. '''
        from ictr.standard import __ as std_imports
        if not std_imports.ENRICH: pytest.skip("Rich not available")
        
        auxdata = make_auxdata( colorize = True )
        lines = _linearizers.linearize_omni( auxdata, {'a': 1} )
        # Rich formatting is different or at least valid
        assert "a" in "".join(lines)


class Test_100_Object_Plain:
    ''' linearize_object_plain. '''

    def test_100_simple_object( self ):
        ''' Linearizes simple object. '''
        auxdata = make_auxdata()
        lines = _linearizers.linearize_object_plain( auxdata, {'a': 1} )
        assert lines == ("{'a': 1}",)

    def test_130_columns_max( self ):
        ''' Linearizes with columns_max constraint. '''
        auxdata = make_auxdata()
        obj = {'a': 1, 'b': 2, 'c': 3}
        lines = _linearizers.linearize_object_plain(
            auxdata, obj, columns_max = 10 )
        # pprint should wrap
        assert len(lines) > 1


class Test_200_Exception_Plain:
    ''' linearize_exception_plain. '''

    def test_200_message_only( self ):
        ''' Exception message without stack trace. '''
        ecfg = _core.ExceptionsConfiguration( enable_stacktraces = False )
        auxdata = make_auxdata( exceptionscfg = ecfg )
        exc = ValueError("msg")
        lines = _linearizers.linearize_exception_plain( auxdata, exc )
        assert lines == ("[ValueError] msg",)

    def test_210_with_stacktrace( self ):
        ''' Exception with stack trace. '''
        ecfg = _core.ExceptionsConfiguration( enable_stacktraces = True )
        auxdata = make_auxdata( exceptionscfg = ecfg )
        try:
            raise ValueError("msg")
        except ValueError as e:
            exc = e
        
        lines = _linearizers.linearize_exception_plain( auxdata, exc )
        assert "[ValueError] msg" in lines
        # Check for stack trace parts
        assert any( "File" in line for line in lines )


class Test_300_Stacktrace_Plain:
    ''' linearize_stacktrace_plain. '''

    def test_300_basic_frame( self ):
        ''' Basic frame formatting. '''
        auxdata = make_auxdata()
        # Mock StackSummary
        Frame = MagicMock()
        Frame.filename = 'file.py'
        Frame.lineno = 10
        Frame.name = 'func'
        Frame.line = 'code'
        stack = [Frame]
        
        lines = _linearizers.linearize_stacktrace_plain( auxdata, stack )
        assert "File 'file.py', line 10, in func" in lines
        assert "    code" in lines

    def test_310_columns_max_wrapping( self ):
        ''' Stack trace frame wrapping with columns_max. '''
        auxdata = make_auxdata()
        Frame = MagicMock()
        Frame.filename = 'long_filename_path_to_file.py'
        Frame.lineno = 10
        Frame.name = 'function_name'
        Frame.line = 'code'
        stack = [Frame]
        
        # Very narrow width to force wrap
        lines = _linearizers.linearize_stacktrace_plain(
            auxdata, stack, columns_max = 20 )
        # Should split filename and address
        # Check logic: if address_size > columns_max
        assert any( "line 10, in function_name" in line for line in lines )
        # With 20 columns, it truncates significantly
        assert any( "File '... " in line for line in lines )


class Test_400_Text_Plain:
    ''' linearize_text_plain. '''

    def test_400_simple_text( self ):
        ''' Simple text pass-through. '''
        auxdata = make_auxdata()
        lines = _linearizers.linearize_text_plain( auxdata, "line1\nline2" )
        assert lines == ("line1", "line2")

    def test_410_wrapping( self ):
        ''' Text wrapping with columns_max. '''
        auxdata = make_auxdata()
        text = "This is a long line that should wrap."
        lines = _linearizers.linearize_text_plain(
            auxdata, text, columns_max = 10 )
        assert len(lines) > 1
        assert lines[0] == "This is a"


class Test_500_Rich_Variants:
    ''' Rich variants. '''

    def test_500_object_rich( self ):
        ''' Rich object linearization. '''
        from ictr.standard import __ as std_imports
        if not std_imports.ENRICH: pytest.skip("Rich not available")
        
        auxdata = make_auxdata( colorize = True )
        # Real Rich output
        lines = _linearizers.linearize_object_rich( auxdata, {'a':1} )
        # Rich formats dict like:
        # {
        #     'a': 1
        # }
        # or similar depending on width.
        assert len(lines) > 0
        assert "a" in "".join(lines)

    def test_510_text_rich( self ):
        ''' Rich text linearization. '''
        from ictr.standard import __ as std_imports
        if not std_imports.ENRICH: pytest.skip("Rich not available")
        
        auxdata = make_auxdata( colorize = True )
        lines = _linearizers.linearize_text_rich( auxdata, "text" )
        # Rich should output text, possibly with styles if provided
        assert "text" in lines[0]

    def test_520_exception_rich( self ):
        ''' Rich exception linearization. '''
        from ictr.standard import __ as std_imports
        if not std_imports.ENRICH: pytest.skip("Rich not available")
        
        exc = ValueError("msg")
        
        # Test without stacktrace
        ecfg = _core.ExceptionsConfiguration( enable_stacktraces = False )
        auxdata_ns = make_auxdata( colorize = True, exceptionscfg = ecfg )
        lines = _linearizers.linearize_exception_rich( auxdata_ns, exc )
        # Rich printing of exception object might just be str(exc)
        assert any( "msg" in line for line in lines )
        
        # Test with stacktrace
        ecfg_s = _core.ExceptionsConfiguration( enable_stacktraces = True )
        auxdata_s = make_auxdata( colorize = True, exceptionscfg = ecfg_s )
        lines = _linearizers.linearize_exception_rich( auxdata_s, exc )
        # Rich Traceback has frames if available, or just exception
        # if not raised. It usually includes exception type name.
        assert any( "ValueError" in line for line in lines )

    def test_530_stacktrace_rich( self ):
        ''' Rich stacktrace linearization. '''
        from ictr.standard import __ as std_imports
        if not std_imports.ENRICH: pytest.skip("Rich not available")
        
        auxdata = make_auxdata( colorize = True )
        # Mock StackSummary
        Frame = MagicMock()
        Frame.filename = 'file.py'
        Frame.lineno = 10
        Frame.name = 'func'
        Frame.line = 'code'
        stack = [Frame]
        
        lines = _linearizers.linearize_stacktrace_rich( auxdata, stack )
        assert len(lines) > 0
        # Check for some content
        combined = "".join(lines)
        assert "file.py" in combined or "func" in combined