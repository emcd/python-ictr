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


''' Core data structures and utilities. '''


from . import __


class Auxiliaries( __.immut.DataclassObject ):
    ''' Auxiliary functions used by textualizers and interpolation.

        Typically used by unit tests to inject mock dependencies,
        but can also be used to deeply customize output.
    '''

    pid_discoverer: __.typx.Annotated[
        __.typx.Callable[ [ ], int ],
        __.ddoc.Doc( ''' Returns ID of current process. ''' ),
    ] = __.os.getpid
    thread_discoverer: __.typx.Annotated[
        __.typx.Callable[ [ ], __.threads.Thread ],
        __.ddoc.Doc( ''' Returns current thread. ''' ),
    ] = __.threads.current_thread
    time_formatter: __.typx.Annotated[
        __.typx.Callable[ [ str ], str ],
        __.ddoc.Doc( ''' Returns current time in specified format. ''' ),
    ] = lambda fmt: __.Datetime.now( __.Timezone.utc ).strftime( fmt )


class ColumnsConstraints( __.enum.Enum ):
    ''' How to constrain text which exceeds maximum columns. '''

    Complect    = __.enum.auto( )  # fold/wrap
    Exceed      = __.enum.auto( )  # overflow
    # Truncate    = __.enum.auto( )  # chop/cut


class IncisionBoundaries( __.enum.Enum ):
    ''' Where to constrain text which exceeds maximum columns. '''

    Nowhere     = __.enum.auto( )
    Whitespace  = __.enum.auto( )  # horizontal spaces and tabs
    Wordsplits  = __.enum.auto( )  # hyphens + whitespace
    Anywhere    = __.enum.auto( )


class Style( __.immut.DataclassObject ):
    ''' Style for text. Corresponds to terminal attributes. '''

    bgcolor: __.typx.Optional[ str ] = None
    fgcolor: __.typx.Optional[ str ] = None
    # TODO: Int flag enum for bold, blink, etc...


InterpolantsStylesRegistry: __.typx.TypeAlias = (
    __.accret.Dictionary[ str, Style ] )


class LabelPresentations( __.enum.IntFlag ):
    ''' How introduction labels should be presented. '''

    Nothing =   0
    Words =     __.enum.auto( )
    Emoji =     __.enum.auto( )


class ExceptionsConfiguration( __.immut.DataclassObject ):
    ''' Configuration pertaining to exceptions. '''

    discoverer: __.typx.Annotated[
        __.typx.Callable[ [ ], __.ExceptionInfo ],
        __.ddoc.Doc( ''' Returns information on current exception. ''' ),
    ] = __.sys.exc_info
    enable_discovery: __.typx.Annotated[
        bool, __.ddoc.Doc( ''' Discover active exception? ''' )
    ] = False
    enable_stacktraces: __.typx.Annotated[
        bool, __.ddoc.Doc( ''' Render tracebacks? ''' )
    ] = False
    recursive_stacktraces: __.typx.Annotated[
        bool, __.ddoc.Doc(
            ''' Render traceback for each exception group member? ''' ),
    ] = False
    template: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Template for exception message. ''' )
    ] = '[{name}] {message}'

    def discover( self ) -> __.typx.Optional[ BaseException ]:
        ''' Discovers active exception. '''
        return self.discoverer( )[ 1 ] if self.enable_discovery else None

    def interpolate( self, exception: BaseException ) -> tuple[ str, ... ]:
        ''' Interpolates exception attributes into message template. '''
        eclass = type( exception )
        name = eclass.__name__
        qname = eclass.__qualname__
        mname = eclass.__module__
        interpolants = dict(
            name = name, qname = qname, mname = mname,
            message = str( exception ) )
        interpolants[ 'fqname' ] = f"{mname}.{qname}"
        return tuple( self.template.format( **interpolants ).split( '\n' ) )
