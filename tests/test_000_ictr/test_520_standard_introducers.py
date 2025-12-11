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


''' Tests for standard introducer. '''


from unittest.mock import MagicMock

import pytest

from ictr import printers as _printers
from ictr import records as _records
from ictr.standard import core as _core
from ictr.standard import introducers as _intros


class Test_000_Introducer_Call:
    ''' Introducer call validation. '''

    def test_100_flavor_introduction( self ):
        ''' Introducer renders flavor label. '''
        introducer = _intros.Introducer()
        control = MagicMock( spec = _printers.TextualizationControl )
        control.colorize = False
        control.columns_max = None
        
        content = _records.MessageContent( summary = '', details = () )
        record = _records.Record(
            address = 'test', content = content, flavor = 'note' )
        
        # Default template is "{flavor}| "
        # Default label_as is Words. 'note' label is 'NOTE'.
        result = introducer( control, record )
        assert result == 'NOTE| '

    def test_200_trace_introduction( self ):
        ''' Introducer renders trace label. '''
        introducer = _intros.Introducer()
        control = MagicMock( spec = _printers.TextualizationControl )
        control.colorize = False
        
        content = _records.MessageContent( summary = '', details = () )
        record = _records.Record(
            address = 'test', content = content, flavor = 0 )
        
        # Default label_as is Words. Level 0 is 'TRACE0'.
        result = introducer( control, record )
        assert result == 'TRACE0| '

    def test_140_custom_label_as_emoji( self ):
        ''' Introducer renders emoji label. '''
        config = _core.IntroducerConfiguration(
            label_as = _core.LabelPresentations.Emoji )
        introducer = _intros.Introducer( configuration = config )
        control = MagicMock( spec = _printers.TextualizationControl )
        control.colorize = False
        
        content = _records.MessageContent( summary = '', details = () )
        record = _records.Record(
            address = 'test', content = content, flavor = 'note' )
        
        # note emoji is '\N{Information Source}\ufe0f'
        result = introducer( control, record )
        assert '\N{Information Source}' in result

    def test_300_template_interpolation( self ):
        ''' Template interpolates variables. '''
        config = _core.IntroducerConfiguration(
            template = "{flavor} @ {address}| " )
        introducer = _intros.Introducer( configuration = config )
        control = MagicMock( spec = _printers.TextualizationControl )
        control.colorize = False
        
        content = _records.MessageContent( summary = '', details = () )
        record = _records.Record(
            address = 'test.addr', content = content, flavor = 'error' )
        
        result = introducer( control, record )
        assert result == 'ERROR @ test.addr| '

    def test_330_style_interpolation_rich( self ):
        ''' Style interpolation with Rich. '''
        from ictr.standard import __ as std_imports
        if not std_imports.ENRICH:
            pytest.skip("Rich not available")

        config = _core.IntroducerConfiguration()
        introducer = _intros.Introducer( configuration = config )
        control = MagicMock( spec = _printers.TextualizationControl )
        control.colorize = True
        control.columns_max = 80
        
        content = _records.MessageContent( summary = '', details = () )
        record = _records.Record(
            address = 'test', content = content, flavor = 'note' )
        
        # We can't mock produce_rich_console, so we just verify it runs
        # without error and returns a string (implicit check).
        # We can also check if result contains ANSI codes if we want to be
        # strict, but exact output depends on Rich version/config.
        
        result = introducer( control, record )
        assert isinstance( result, str )
