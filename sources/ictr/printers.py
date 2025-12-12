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


ColumnsMaxCalculator: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Union[
        __.typx.Optional[ int ],
        __.cabc.Callable[ [ ], __.typx.Optional[ int ] ],
    ],
    __.typx.Doc(
        ''' Available line length of target character screen.

            * May be an integer.
            * May be ``None`` if indeterminable or irrelevant.
            * May be a callable which takes no arguments and returns ``None``
              or an integer. This support terminal resizing, for example.
        ''' ),
]


class TextualizationControl( __.immut.DataclassObject ):
    ''' Contextual data for compositor and introducer factories. '''

    charset: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.typx.Doc(
            ''' Character set encoding of target.

                May be ``None`` if indeterminable or irrelevant. ''' ),
    ] = None
    colorize: __.typx.Annotated[
        bool, __.typx.Doc( ''' Colorize textualization? ''' )
    ] = False
    columns_max_calculator: ColumnsMaxCalculator = None

    @property
    def columns_max( self ) -> __.typx.Optional[ int ]:
        ''' Available line length (maximum columns) of target.

            May be ``None`` if indeterminable or irrelevant.
        '''
        calculator = self.columns_max_calculator
        return calculator( ) if callable( calculator ) else calculator


class Printer(
    __.immut.DataclassProtocol, __.typx.Protocol,
    decorators = ( __.typx.runtime_checkable, ),
):
    ''' Abstract base class for printers. '''

    @__.abc.abstractmethod
    def __call__( self, record: str | _records.Record ) -> None:
        ''' Prints record to destination. '''
        raise NotImplementedError

    @__.abc.abstractmethod
    def provide_textualization_control(
        self
    ) -> __.typx.Optional[ TextualizationControl ]:
        ''' Provides control object for textualization, if capable. '''
        raise NotImplementedError

    # TODO: print (same as __call__)
    # TODO: print_async


Printers: __.typx.TypeAlias = __.cabc.Sequence[ Printer ]
PrinterFactory: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, _flavors.Flavor ], Printer ] )
PrinterFactoryUnion: __.typx.TypeAlias = __.io.TextIOBase | PrinterFactory
PrinterFactoriesUnion: __.typx.TypeAlias = (
    __.cabc.Sequence[ PrinterFactoryUnion ] )


@_validate_arguments
def count_columns_visual( text: str ) -> int:
    # Note: If CSI ED ("Erase on Display") or EL ("Erase in Line") sequences
    #       are used within the text, then the count will not be accurate.
    text_no_ansi = remove_ansi_c1_sequences( text )
    return __.wcwidth.wcswidth( text_no_ansi )


@_validate_arguments
def remove_ansi_c1_sequences( text: str ) -> str:
    # https://stackoverflow.com/a/14693789/14833542
    regex = __.re.compile( r'''\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])''' )
    return regex.sub( '', text )


@_validate_arguments
def produce_columns_max_calculator(
    target: __.io.TextIOBase
) -> ColumnsMaxCalculator:
    fileno_revealer = getattr( target, 'fileno', None )
    if fileno_revealer is None: return None
    try: fileno = fileno_revealer( )
    except ( IOError, OSError, __.io.UnsupportedOperation ): return None
    if not __.os.isatty( fileno ): return None

    def calculate( ) -> __.typx.Optional[ int ]:
        try: size = __.shutil.get_terminal_size( fileno )
        except Exception: return None
        return size.columns

    return calculate


@_validate_arguments
def produce_printer_factory_default(
    target: __.io.TextIOBase,
    force_color: bool = False,
) -> PrinterFactory:
    ''' Produces default printer factory associated with a stream.

        Can optionally force ANSI SGR sequences (terminal color attributes,
        etc...) on target stream.
    '''
    def produce_printer( address: str, flavor: _flavors.Flavor ) -> Printer:
        from .standard import Printer
        match __.sys.platform:
            case 'win32':
                winansi = _colorama.AnsiToWin32( target ) # pyright: ignore
                target_ = ( # pragma: no cover
                    winansi.stream if winansi.convert else target )
            case _: target_ = target
        return Printer(
            target = target_, force_color = force_color ) # pyright: ignore

    return produce_printer


# def truncate_visual( text: str, columns_max: int ) -> str:
#     lsize = 0
#     for i, c in enumerate( text ):
#         csize = __.wcwidth.wcwidth( c )
#         csize = max( 0, csize )  # control or combining character
#         if lsize + csize > columns_max:
#             # TODO? Add ellipsis.
#             return text[ : i ]
#         lsize += csize
#     return text
