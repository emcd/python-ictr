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


''' Printers and printer factories. '''


from . import __


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = __.ArgumentClassInvalidity ) )


class Printer( __.Printer ):
    ''' Simple printer that writes to a text stream. '''

    target: __.io.TextIOBase
    force_color: bool = False

    def __call__( self, record: str | __.Record ) -> None:
        text = record if isinstance( record, str ) else str( record )
        if not self.force_color and not self.target.isatty( ):
            text = __.remove_ansi_c1_sequences( text )
        print( text, file = self.target )

    def provide_textualizer_control(
        self
    ) -> __.typx.Optional[ __.TextualizationControl ]:
        tty = self.target.isatty( )
        colorize = tty
        if __.os.environ.get( 'NO_COLOR' ): colorize = False
        colorize = colorize or self.force_color
        columns_max_calculator = (
            __.produce_columns_max_calculator( self.target ) )
        # TODO: Get encoding from target.
        return __.TextualizationControl(
            colorize = colorize,
            columns_max_calculator = columns_max_calculator )
