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


''' Tests for standard compositor. '''








from unittest.mock import MagicMock

from ictr import printers as _printers
from ictr import records as _records
from ictr.standard import compositors as _compositors
from ictr.standard import core as _core


class Test_000_Compositor_Basics:


    ''' Basic compositor functionality. '''





    def test_000_creation( self ):


        ''' Compositor creation with default configuration. '''


        compositor = _compositors.Compositor()


        assert compositor.configuration is not None


        assert compositor.introducer is not None





    def test_010_call_flow( self ):


        ''' Compositor.__call__ basic flow. '''


        compositor = _compositors.Compositor()


        control = MagicMock( spec = _printers.TextualizationControl )


        control.colorize = False


        control.columns_max = None


        


        content = _records.MessageContent( summary = 'test', details = () )


        record = _records.Record(


            address = 'addr', content = content, flavor = 'note' )


        


        # Real linearizer returns ('test',) for 'test'


        result = compositor( control, record )


        assert 'test' in result








class Test_100_Render_Summary:


    ''' Summary rendering logic. '''





    def test_100_exceed_constraint( self ):


        ''' Render summary with Exceed constraint (default). '''


        config = _core.CompositorConfiguration()


        compositor = _compositors.Compositor( configuration = config )


        control = MagicMock( spec = _printers.TextualizationControl )


        control.colorize = False


        control.columns_max = None


        


        content = _records.MessageContent( summary = 'summary', details = () )


        record = _records.Record(


            address = 'a', content = content, flavor = 'n' )


        


        # intro is "ictr| " by default


        result = compositor( control, record )


        assert result == 'ictr|  summary'





    def test_110_complect_constraint_single_line( self ):


        ''' Render summary with Complect constraint, fits in line. '''


        config = _core.CompositorConfiguration()


        compositor = _compositors.Compositor( configuration = config )


        control = MagicMock( spec = _printers.TextualizationControl )


        control.colorize = False


        control.columns_max = 80


        


        content = _records.MessageContent( summary = 'short', details = () )


        record = _records.Record(


            address = 'a', content = content, flavor = 'n' )


        


        result = compositor( control, record )


        assert result == 'ictr|  short'





    def test_120_complect_constraint_multiline( self ):


        ''' Render summary with Complect constraint, multiline result. '''


        config = _core.CompositorConfiguration(


            line_prefix_subsequent = '.. '


        )


        compositor = _compositors.Compositor( configuration = config )


        control = MagicMock( spec = _printers.TextualizationControl )


        control.colorize = False


        # Small width to force wrap


        control.columns_max = 10


        


        # String > 10 chars


        content = _records.MessageContent(


            summary = '1234567890123', details = () )


        record = _records.Record(


            address = 'a', content = content, flavor = 'n' )


        


        result = compositor( control, record )


        # Check result format


        assert result.startswith('ictr| ')


        assert '\n.. ' in result


        assert '123' in result








class Test_200_Render_Detail:


    ''' Detail rendering logic. '''





    def test_200_render_detail( self ):


        ''' Render detail with prefixes. '''


        config = _core.CompositorConfiguration(


            detail_prefix_initial = '* ',


            detail_prefix_subsequent = '  '


        )


        compositor = _compositors.Compositor( configuration = config )


        control = MagicMock( spec = _printers.TextualizationControl )


        control.colorize = False


        control.columns_max = 10


        


        content = _records.MessageContent(


            summary = 'summary', details = ('1234567890123',)


        )


        record = _records.Record(


            address = 'a', content = content, flavor = 'n' )


        


        result = compositor( control, record )


        # Check for prefixes


        assert '* ' in result


        assert '\n  ' in result








class Test_300_Exception_Handling:


    ''' Exception discovery and rendering. '''





    def test_300_exception_discovery( self ):


        ''' Compositor discovers exception if configured. '''


        exc = ValueError("test")


        


        # Configure exceptions with mock discoverer


        mock_discoverer = MagicMock( return_value = ( None, exc, None ) )


        ecfg = _core.ExceptionsConfiguration(


            enable_discovery = True,


            discoverer = mock_discoverer,


            enable_stacktraces = False


        )


        lcfg = _core.LinearizerConfiguration( exceptionscfg = ecfg )


        config = _core.CompositorConfiguration( linearizercfg = lcfg )


        


        compositor = _compositors.Compositor( configuration = config )


        control = MagicMock( spec = _printers.TextualizationControl )


        control.colorize = False


        control.columns_max = None


        


        content = _records.MessageContent( summary = 'msg', details = () )


        record = _records.Record(


            address = 'a', content = content, flavor = 'n' )


        


        result = compositor( control, record )


        assert '[ValueError] test' in result





    def test_310_exception_summary( self ):


        ''' Compositor handles BaseException summary (no rediscovery). '''


        # Default config (discovery disabled)


        compositor = _compositors.Compositor()


        control = MagicMock( spec = _printers.TextualizationControl )


        control.colorize = False


        control.columns_max = None


    


        exc = ValueError("summary")


        content = _records.MessageContent( summary = exc, details = () )


        record = _records.Record(


            address = 'a', content = content, flavor = 'n' )


        


        result = compositor( control, record )


        assert '[ValueError] summary' in result



