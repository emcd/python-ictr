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


''' Tests for standard core structures. '''


from unittest.mock import MagicMock

import pytest

from ictr import printers as _printers
from ictr.standard import core as _core


class Test_000_CompositorConfiguration:
    ''' CompositorConfiguration validation. '''

    def test_000_defaults( self ):
        ''' Defaults are correct. '''
        config = _core.CompositorConfiguration()
        assert config.line_prefix_initial == ''
        assert config.details_separator == '\n\n'
        assert config.linearizercfg is not None

    def test_140_immutability( self ):
        ''' Configuration is immutable. '''
        config = _core.CompositorConfiguration()
        with pytest.raises( AttributeError ):
            config.line_prefix_initial = '>>'


class Test_010_CompositorState:
    ''' CompositorState validation. '''

    def test_300_from_configuration_rich_available( self ):
        ''' State creation with Rich logic. '''
        config = _core.CompositorConfiguration()
        control = MagicMock( spec = _printers.TextualizationControl )
        control.colorize = True
        control.columns_max = 80
        
        # We cannot patch ENRICH because module is immutable.
        # We check the actual value.
        from ictr.standard import __ as std_imports
        expected_colorize = std_imports.ENRICH
        
        state = _core.CompositorState.from_configuration( config, control )
        
        assert state.linearizer.colorize is expected_colorize
        if expected_colorize:
            assert state.linearizer.columns_max == 80

    def test_310_from_configuration_rich_unavailable( self ):
        ''' State creation with Rich unavailable. '''
        # If ENRICH is True, we cannot test the False path without patching.
        from ictr.standard import __ as std_imports
        if std_imports.ENRICH:
            pytest.skip(
                "Cannot test ENRICH=False path when Rich is installed "
                "and module is immutable" )
            
        config = _core.CompositorConfiguration()
        control = MagicMock( spec = _printers.TextualizationControl )
        control.colorize = True
        control.columns_max = 80
        
        state = _core.CompositorState.from_configuration( config, control )
        assert state.linearizer.colorize is False


class Test_200_ExceptionsConfiguration:
    ''' ExceptionsConfiguration validation. '''

    def test_210_discover_finds_exception( self ):
        ''' Discover finds active exception. '''
        config = _core.ExceptionsConfiguration( enable_discovery = True )
        try:
            raise ValueError( "test" )
        except ValueError as exc:
            discovered = config.discover()
            assert discovered is exc

    def test_220_discover_no_exception( self ):
        ''' Discover returns None when no exception. '''
        config = _core.ExceptionsConfiguration( enable_discovery = True )
        assert config.discover() is None

    def test_230_interpolate( self ):
        ''' Interpolate formats exception message. '''
        config = _core.ExceptionsConfiguration(
            template = '{name}: {message}' )
        exc = ValueError( "test" )
        lines = config.interpolate( exc )
        assert lines == ( "ValueError: test", )

