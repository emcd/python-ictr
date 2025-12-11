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


''' Tests for stack inspection and module discovery. '''


from unittest.mock import MagicMock, patch

import pytest

from ictr import dispatchers as _dispatchers
from ictr import exceptions as _exceptions


class Test_100_Module_Discovery:
    ''' Module address discovery validation. '''

    def test_100_identifies_calling_module( self ):
        ''' discover_address identifies calling module. '''
        # We need to mock inspect.currentframe because we are calling internal
        # function directly or we rely on real stack.
        # Let's rely on real stack first for simple case.
        name = _dispatchers._discover_invoker_module_name()
        assert name == __name__

    def test_110_handles_main_module( self ):
        ''' discover_address handles __main__ module. '''
        # Mock frame for __main__
        mock_frame = MagicMock()
        mock_frame.f_code.co_filename = '<stdin>' # As per code logic
        mock_frame.f_back = None
        
        # We need to simulate that getmodule returns None for this frame
        with (
            patch( 'inspect.currentframe', return_value = mock_frame ),
            patch( 'inspect.getmodule', return_value = None )
        ):
            name = _dispatchers._discover_invoker_module_name()
            assert name == '__main__'

    def test_140_missing_frame_info( self ):
        ''' discover_address raises exception if module inference fails. '''
        mock_frame = MagicMock()
        mock_frame.f_code.co_filename = 'unknown'
        mock_frame.f_back = None
        
        with (
            patch( 'inspect.currentframe', return_value = mock_frame ),
            patch( 'inspect.getmodule', return_value = None ),
            pytest.raises( _exceptions.ModuleInferenceFailure )
        ):
            _dispatchers._discover_invoker_module_name()

    def test_130_skips_internal_modules( self ):
        ''' discover_address skips internal ictr modules. '''
        # Create a chain of frames: [Internal -> Internal -> External]
        
        external_module = MagicMock()
        external_module.__name__ = 'external.module'
        external_frame = MagicMock()
        
        internal_module = MagicMock()
        internal_module.__name__ = 'ictr.internal'
        internal_frame = MagicMock()
        internal_frame.f_back = external_frame
        
        frames = {
            internal_frame: internal_module,
            external_frame: external_module
        }
        
        def getmodule( frame ):
            return frames.get( frame )
            
        with (
            patch( 'inspect.currentframe', return_value = internal_frame ),
            patch( 'inspect.getmodule', side_effect = getmodule )
        ):
            name = _dispatchers._discover_invoker_module_name()
            assert name == 'external.module'
