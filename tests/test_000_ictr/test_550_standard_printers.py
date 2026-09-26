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


''' Tests for standard printers. '''


import io
from unittest.mock import MagicMock, patch

from ictr.standard import printers as _printers


class Test_000_Printer:
    ''' Standard printer functionality. '''

    def test_000_creation( self ):
        ''' Printer creation. '''
        target = MagicMock( spec = io.TextIOBase )
        printer = _printers.Printer( target = target )
        assert printer.target is target
        assert printer.force_colorize is False

    def test_100_call_writes_to_target( self ):
        ''' __call__ writes text to target. '''
        # Using StringIO as target to verify output
        target = io.StringIO()
        # Mock isatty to False to avoid colorization check issues if any
        # But StringIO doesn't have isatty by default, need to check code.
        # Code calls target.isatty().

        # We can't easily set isatty on StringIO instance in a way that
        # Printer logic expects unless we subclass or mock.

        target = MagicMock( spec = io.TextIOBase )
        target.isatty.return_value = False

        printer = _printers.Printer( target = target )
        printer( "message" )

        # print( text, file=target ) calls target.write()
        target.write.assert_called()
        # print calls write multiple times (content then newline)
        calls = [args[0] for args, _ in target.write.call_args_list]
        assert any("message" in call for call in calls)

    def test_110_call_with_record( self ):
        ''' __call__ handles Record (converts to str). '''
        target = MagicMock( spec = io.TextIOBase )
        target.isatty.return_value = False
        printer = _printers.Printer( target = target )

        record = MagicMock()
        record.__str__.return_value = "record_str"

        printer( record )
        target.write.assert_called()
        calls = [args[0] for args, _ in target.write.call_args_list]
        assert any("record_str" in call for call in calls)

    def test_200_provide_control( self ):
        ''' provide_textualization_control returns correct control. '''
        target = MagicMock( spec = io.TextIOBase )
        target.isatty.return_value = True
        target.encoding = 'utf-8'
        target.fileno.return_value = 1

        printer = _printers.Printer( target = target )

        with (
            patch( 'os.isatty', return_value = True ),
            patch( 'shutil.get_terminal_size' ) as mock_size
        ):
            mock_size.return_value.columns = 80

            ctrl = printer.provide_textualization_control()
            assert ctrl.colorize is True
            assert ctrl.charset == 'utf-8'
            assert ctrl.columns_max == 80

    def test_300_colorization_tty( self ):
        ''' Colorization determined by tty. '''
        target = MagicMock( spec = io.TextIOBase )
        target.isatty.return_value = True
        printer = _printers.Printer( target = target )
        assert printer._determine_colorization() is True

        target.isatty.return_value = False
        assert printer._determine_colorization() is False

    def test_310_colorization_no_color_env( self ):
        ''' NO_COLOR environment variable disables color. '''
        target = MagicMock( spec = io.TextIOBase )
        target.isatty.return_value = True
        printer = _printers.Printer( target = target )

        with patch( 'os.environ.get', return_value = '1' ):
            assert printer._determine_colorization() is False

    def test_320_colorization_force_color( self ):
        ''' force_color overrides NO_COLOR and tty. '''
        target = MagicMock( spec = io.TextIOBase )
        target.isatty.return_value = False
        printer = _printers.Printer( target = target, force_colorize = True )

        with patch( 'os.environ.get', return_value = '1' ):
            assert printer._determine_colorization() is True

    def test_400_strip_ansi_if_no_color( self ):
        ''' Strips ANSI codes if colorization is disabled. '''
        target = MagicMock( spec = io.TextIOBase )
        target.isatty.return_value = False
        printer = _printers.Printer( target = target )

        ansi_text = "\x1b[31mRed\x1b[0m"
        printer( ansi_text )

        target.write.assert_called()
        calls = [args[0] for args, _ in target.write.call_args_list]
        combined = "".join(calls)
        assert "Red" in combined
        assert "\x1b" not in combined
