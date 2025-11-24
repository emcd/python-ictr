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


''' Printers, printer factories, and auxiliary functions and types. '''



import colorama as _colorama

from . import __
from . import exceptions as _exceptions
from . import flavors as _flavors
from . import records as _records


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = _exceptions.ArgumentClassInvalidity ) )


class TextualizerControl( __.immut.DataclassObject ):
    ''' Contextual data for formatter and introduction factories. '''

    charset: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.typx.Doc(
            ''' Character set encoding of target.

                May be ``None`` if indeterminable or irrelevant. ''' ),
    ] = None
    colorize: __.typx.Annotated[
        bool, __.typx.Doc( ''' Colorize textualization? ''' )
    ] = False
    columns_count: __.typx.Annotated[
        __.typx.Optional[ int ],
        __.typx.Doc(
            ''' Available line length of target character screen.

                May be ``None`` if indeterminable or irrelevant. ''' ),
    ] = None


class Printer( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Abstract base class for printers. '''

    @__.abc.abstractmethod
    def __call__( self, record: str | _records.Record ) -> None:
        ''' Prints record to destination. '''
        raise NotImplementedError

    @__.abc.abstractmethod
    def provide_textualizer_control(
        self
    ) -> __.typx.Optional[ TextualizerControl ]:
        ''' Provides control object for textualizer, if capable. '''
        raise NotImplementedError

    # TODO: print (same as __call__)
    # TODO: print_async


class SimplePrinter( Printer ):
    ''' Simple printer that writes to a text stream. '''

    target: __.io.TextIOBase
    force_color: bool = False

    def __call__( self, record: str | _records.Record ) -> None:
        text = record if isinstance( record, str ) else str( record )
        if not self.force_color and not self.target.isatty( ):
            text = remove_ansi_c1_sequences( text )
        print( text, file = self.target )

    def provide_textualizer_control(
        self
    ) -> __.typx.Optional[ TextualizerControl ]:
        tty = self.target.isatty( )
        colorize = tty
        if __.os.environ.get( 'NO_COLOR' ): colorize = False
        colorize = colorize or self.force_color
        # TODO: Detect terminal width if isatty.
        # TODO: Get encoding from target.
        return TextualizerControl( colorize = colorize )


PrinterFactory: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, _flavors.Flavor ], Printer ] )
PrinterFactoryUnion: __.typx.TypeAlias = __.io.TextIOBase | PrinterFactory


@_validate_arguments
def produce_simple_printer(
    target: __.io.TextIOBase,
    mname: str,
    flavor: _flavors.Flavor,
    force_color: bool = False,
) -> Printer:
    ''' Produces printer which uses standard Python 'print'. '''
    match __.sys.platform:
        case 'win32':
            winansi = _colorama.AnsiToWin32( target ) # pyright: ignore
            target_ = ( # pragma: no cover
                winansi.stream if winansi.convert else target )
        case _: target_ = target
    return SimplePrinter(
        target = target_, force_color = force_color ) # pyright: ignore


def remove_ansi_c1_sequences( text: str ) -> str:
    # https://stackoverflow.com/a/14693789/14833542
    regex = __.re.compile( r'''\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])''' )
    return regex.sub( '', text )
