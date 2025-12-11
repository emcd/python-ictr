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


''' Tests for message reporters. '''


from unittest.mock import ANY, MagicMock

from ictr import records as _records
from ictr import reporters as _reporters


class Test_000_Creation:
    ''' Reporter creation. '''

    def test_000_creation( self ):
        ''' Reporter creation with minimal configuration. '''
        reporter = _reporters.Reporter(
            active = True,
            address = 'address',
            flavor = 'flavor',
            compositor = MagicMock(),
            printers = ( )
        )
        assert reporter.active is True
        assert reporter.address == 'address'


class Test_100_Message_Processing:
    ''' Reporter message processing. '''

    def test_100_summary_only( self ):
        ''' Reporter processes message with summary only. '''
        mock_printer = MagicMock()
        mock_printer.provide_textualization_control.return_value = None
        reporter = _reporters.Reporter(
            active = True,
            address = 'address',
            flavor = 'flavor',
            compositor = MagicMock(),
            printers = ( mock_printer, )
        )
        reporter( 'summary' )
        assert mock_printer.called
        call_args = mock_printer.call_args[0]
        assert isinstance( call_args[0], _records.Record )
        assert call_args[0].content.summary == 'summary'
        assert call_args[0].content.details == ( )

    def test_110_summary_and_details( self ):
        ''' Reporter processes message with summary and details. '''
        mock_printer = MagicMock()
        mock_printer.provide_textualization_control.return_value = None
        reporter = _reporters.Reporter(
            active = True,
            address = 'address',
            flavor = 'flavor',
            compositor = MagicMock(),
            printers = ( mock_printer, )
        )
        reporter( 'summary', 'detail1', 'detail2' )
        record = mock_printer.call_args[0][0]
        assert record.content.summary == 'summary'
        assert record.content.details == ( 'detail1', 'detail2' )

    def test_130_inactive_reporter( self ):
        ''' Inactive reporter does not process message. '''
        mock_printer = MagicMock()
        reporter = _reporters.Reporter(
            active = False,
            address = 'address',
            flavor = 'flavor',
            compositor = MagicMock(),
            printers = ( mock_printer, )
        )
        reporter( 'summary' )
        assert not mock_printer.called

    def test_150_timestamp_creation( self ):
        ''' Reporter creates Record with timestamp. '''
        mock_printer = MagicMock()
        mock_printer.provide_textualization_control.return_value = None
        reporter = _reporters.Reporter(
            active = True,
            address = 'address',
            flavor = 'flavor',
            compositor = MagicMock(),
            printers = ( mock_printer, )
        )
        reporter( 'summary' )
        record = mock_printer.call_args[0][0]
        assert record.ctime is not None


class Test_200_Multiple_Printers:
    ''' Multiple printers handling. '''

    def test_210_multiple_printers( self ):
        ''' Reporter with multiple printers. '''
        p1 = MagicMock()
        p1.provide_textualization_control.return_value = None
        p2 = MagicMock()
        p2.provide_textualization_control.return_value = None
        
        reporter = _reporters.Reporter(
            active = True,
            address = 'address',
            flavor = 'flavor',
            compositor = MagicMock(),
            printers = ( p1, p2 )
        )
        reporter( 'summary' )
        assert p1.called
        assert p2.called

    def test_240_printer_with_textualization_control( self ):
        ''' Printer with TextualizationControl receives rendered string. '''
        ctrl = MagicMock()
        printer = MagicMock()
        printer.provide_textualization_control.return_value = ctrl
        
        compositor = MagicMock()
        compositor.return_value = 'rendered string'
        
        reporter = _reporters.Reporter(
            active = True,
            address = 'address',
            flavor = 'flavor',
            compositor = compositor,
            printers = ( printer, )
        )
        reporter( 'summary' )
        
        compositor.assert_called_with( ctrl, ANY )
        printer.assert_called_with( 'rendered string' )
