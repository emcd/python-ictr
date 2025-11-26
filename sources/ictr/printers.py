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



from . import __
from . import flavors as _flavors
from . import records as _records


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
    columns_max_calculator: ColumnsMaxCalculator = None

    @property
    def columns_max( self ) -> __.typx.Optional[ int ]:
        ''' Available line length (maximum columns) of target.

            May be ``None`` if indeterminable or irrelevant.
        '''
        calculator = self.columns_max_calculator
        return calculator( ) if callable( calculator ) else calculator


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


PrinterFactory: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, _flavors.Flavor ], Printer ] )
PrinterFactoryUnion: __.typx.TypeAlias = __.io.TextIOBase | PrinterFactory


def count_columns_visual( text: str ) -> int:
    # Note: If CSI ED ("Erase on Display") or EL ("Erase in Line") sequences
    #       are used within the text, then the count will not be accurate.
    text_no_ansi = remove_ansi_c1_sequences( text )
    return __.wcwidth.wcswidth( text_no_ansi )


def remove_ansi_c1_sequences( text: str ) -> str:
    # https://stackoverflow.com/a/14693789/14833542
    regex = __.re.compile( r'''\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])''' )
    return regex.sub( '', text )


def produce_columns_max_calculator(
    target: __.io.TextIOBase
) -> ColumnsMaxCalculator:
    fileno = getattr( target, 'fileno', None )
    if fileno is None: return None
    if not __.os.isatty( fileno ): return None

    def calculate( ) -> __.typx.Optional[ int ]:
        try: size = __.shutil.get_terminal_size( fileno )
        except Exception: return None
        return size.columns

    return calculate


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
