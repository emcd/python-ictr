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


''' Tests for printer protocols and factories. '''


import io
import sys
from unittest.mock import MagicMock, patch

from ictr import printers as _printers


class Test_000_Protocols:
    ''' Protocol validation. '''

    def test_000_printer_protocol( self ):
        ''' Printer protocol is defined. '''
        assert issubclass( _printers.Printer, object )


class Test_050_TextualizationControl:
    ''' TextualizationControl functionality. '''
    
    def test_050_columns_max_property( self ):
        ''' columns_max property logic. '''
        ctrl = _printers.TextualizationControl()
        assert ctrl.columns_max is None
        
        ctrl = _printers.TextualizationControl( columns_max_calculator = 80 )
        assert ctrl.columns_max == 80
        
        ctrl = _printers.TextualizationControl(
            columns_max_calculator = lambda: 100 )
        assert ctrl.columns_max == 100


class Test_100_Factory_Functions:
    ''' Factory function validation. '''

    def test_100_produce_default_creates_factory( self ):
        ''' produce_printer_factory_default returns callable. '''
        factory = _printers.produce_printer_factory_default( sys.stderr )
        assert callable( factory )

    def test_110_factory_creates_printer( self ):
        ''' Factory creates printer instance. '''
        factory = _printers.produce_printer_factory_default( sys.stderr )
        printer = factory( 'address', 'flavor' )
        # Verifies it matches protocol
        assert isinstance( printer, _printers.Printer )

    def test_120_factory_with_custom_target( self ):
        ''' produce_printer_factory_default with custom stream. '''
        stream = io.StringIO()
        factory = _printers.produce_printer_factory_default( stream )
        printer = factory( 'address', 'flavor' )
        assert isinstance( printer, _printers.Printer )


class Test_300_Columns_Max_Calculator:
    ''' Columns max calculator validation. '''
    
    def test_300_terminal_file( self ):
        ''' produce_columns_max_calculator with terminal file. '''
        # Mock file object that looks like a tty
        mock_file = MagicMock( spec = io.TextIOBase )
        mock_file.fileno.return_value = 1
        
        with (
            patch( 'os.isatty', return_value = True ),
            patch( 'shutil.get_terminal_size' ) as mock_size
        ):
            mock_size.return_value.columns = 80
            calculator = _printers.produce_columns_max_calculator( mock_file )
            assert callable( calculator )
            assert calculator() == 80

    def test_310_non_terminal_file( self ):
        ''' produce_columns_max_calculator with non-terminal file. '''
        mock_file = MagicMock( spec = io.TextIOBase )
        mock_file.fileno.return_value = 1
        
        with patch( 'os.isatty', return_value = False ):
            calculator = _printers.produce_columns_max_calculator( mock_file )
            assert calculator is None

    def test_320_no_fileno( self ):
        ''' produce_columns_max_calculator with file without fileno. '''
        mock_file = MagicMock( spec = io.TextIOBase )
        del mock_file.fileno # Ensure no fileno attribute
        
        calculator = _printers.produce_columns_max_calculator( mock_file )
        assert calculator is None

    def test_330_get_terminal_size_failure( self ):
        ''' produce_columns_max_calculator handles error. '''
        mock_file = MagicMock( spec = io.TextIOBase )
        mock_file.fileno.return_value = 1
        
        with (
            patch( 'os.isatty', return_value = True ),
            patch( 'shutil.get_terminal_size', side_effect = OSError )
        ):
            calculator = _printers.produce_columns_max_calculator( mock_file )
            assert callable( calculator )
            assert calculator() is None
