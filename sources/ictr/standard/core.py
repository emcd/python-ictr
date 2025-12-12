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


class IntroducerConfiguration( __.immut.DataclassObject ):
    ''' Behaviors and format for text from standard introducer. '''

    auxiliaries: __.typx.Annotated[
        Auxiliaries, __.typx.Doc( ''' Auxiliaries for interpolation. ''' )
    ] = __.dcls.field( default_factory = Auxiliaries )
    colorize: __.typx.Annotated[
        bool, __.typx.Doc( ''' Attempt to colorize? ''' )
    ] = True
    label_as: __.typx.Annotated[
        LabelPresentations,
        __.ddoc.Doc(
            ''' How to present prefix label.

                ``Words``: As words like ``TRACE0`` or ``ERROR``.
                ``Emoji``: As emoji like ``🔎`` or ``❌``.

                For both emoji and words: ``Emoji | Words``.
            ''' )
    ] = LabelPresentations.Words
    styles: __.typx.Annotated[
        InterpolantsStylesRegistry,
        __.ddoc.Doc(
            ''' Mapping of interpolant names to style objects. ''' ),
    ] = __.dcls.field( default_factory = InterpolantsStylesRegistry )
    template: __.typx.Annotated[
        str,
        __.ddoc.Doc(
            ''' String format for prefix.

                The following interpolants are supported:
                ``flavor``: Decorated flavor.
                ``address``: Address of invoker.
                ``timestamp``: Current timestamp, formatted as string.
                ``process_id``: ID of current process according to OS kernel.
                ``thread_id``: ID of current thread.
                ``thread_name``: Name of current thread.
            ''' ),
    ] = "{flavor}| " # "{timestamp} [{module_qname}] {flavor}| "
    ts_format: __.typx.Annotated[
        str,
        __.ddoc.Doc(
            ''' String format for prefix timestamp.

                Used by :py:func:`time.strftime` or equivalent.
            ''' ),
    ] = '%Y-%m-%d %H:%M:%S.%f'


class IntroducerState( __.immut.DataclassObject ):
    ''' Data transfer object for introducer state. '''

    configuration: IntroducerConfiguration
    control: __.TextualizationControl
    colorize: __.typx.Annotated[ bool, __.ddoc.Doc( ''' Colorize? ''' ) ]
    columns_max: __.typx.Annotated[
        __.Absential[ int ],
        __.ddoc.Doc(
            ''' Available line length (maximum columns) of target. ''' ),
    ] = __.absent

    @classmethod
    def from_configuration(
        cls,
        configuration: IntroducerConfiguration,
        control: __.TextualizationControl,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> __.typx.Self:
        colorize = __.ENRICH and control.colorize and configuration.colorize
        return cls(
            configuration = configuration,
            control = control,
            colorize = colorize,
            columns_max = columns_max )


class LinearizerConfiguration( __.immut.DataclassObject ):
    ''' Behaviors for standard textual linearizer. '''

    colorize: __.typx.Annotated[
        bool, __.typx.Doc( ''' Attempt to colorize? ''' )
    ] = True
    columns_constraint: __.typx.Annotated[
        ColumnsConstraints,
        __.ddoc.Doc(
            ''' How to constrain text which exceeds maximum columns. ''' ),
    ] = ColumnsConstraints.Complect
    columns_max: __.typx.Annotated[
        __.typx.Optional[ int ],
        __.ddoc.Doc(
            ''' How many columns per line to assume if printer does not tell.

                If ``None``, then infinite number of columns is assumed.
            ''' ),
    ] = None
    exceptionscfg: __.typx.Annotated[
        ExceptionsConfiguration,
        __.ddoc.Doc( ''' Configuration pertaining to exceptions. ''' ),
    ] = __.dcls.field( default_factory = ExceptionsConfiguration )
    incision_boundary: __.typx.Annotated[
        IncisionBoundaries,
        __.ddoc.Doc(
            ''' Where to constrain text which exceeds maximum columns. ''' ),
    ] = IncisionBoundaries.Wordsplits


class LinearizerState( __.immut.DataclassObject ):
    ''' Data transfer object for linearizer state. '''

    configuration: LinearizerConfiguration
    control: __.TextualizationControl
    colorize: __.typx.Annotated[ bool, __.ddoc.Doc( ''' Colorize? ''' ) ]
    columns_constraint: __.typx.Annotated[
        ColumnsConstraints,
        __.ddoc.Doc( ''' Effective columns constraint for lines. ''' ),
    ] = ColumnsConstraints.Exceed
    columns_max: __.typx.Annotated[
        __.Absential[ int ],
        __.ddoc.Doc(
            ''' Available line length (maximum columns) of target. ''' ),
    ] = __.absent

    @classmethod
    def from_configuration(
        cls,
        configuration: LinearizerConfiguration,
        control: __.TextualizationControl,
    ) -> __.typx.Self:
        colorize = __.ENRICH and control.colorize and configuration.colorize
        columns_constraint = configuration.columns_constraint
        columns_max = control.columns_max or configuration.columns_max
        if columns_max is None:
            columns_constraint = ColumnsConstraints.Exceed
            columns_max = __.absent
        return cls(
            configuration = configuration,
            control = control,
            colorize = colorize,
            columns_constraint = columns_constraint,
            columns_max = columns_max )


class CompositorConfiguration( __.immut.DataclassObject ):
    ''' Behaviors and format for text from standard compositor. '''

    detail_prefix_initial: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Initial prefix for message detail. ''' )
    ] = ''
    detail_prefix_subsequent: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.ddoc.Doc(
            ''' Subsequent prefix for message detail.

                If ``None``, then automatic padding is calculated based on the
                visual width of the initial prefix for message detail.
            ''' ),
    ] = None
    # TODO? 'details_maximum'
    details_separator: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Separator between details. ''' )
    ] = '\n\n'
    line_prefix_initial: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Prefix before first line. ''' )
    ] = ''
    line_prefix_subsequent: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.ddoc.Doc(
            ''' Prefix before each line after the first.

                If ``None``, then automatic padding is calculated based on the
                visual width of the initial line prefix.
            ''' ),
    ] = None
    linearizercfg: __.typx.Annotated[
        LinearizerConfiguration,
        __.ddoc.Doc(
            ''' Text linearization and pretty-formatting behaviors. ''' ),
    ] = __.dcls.field( default_factory = LinearizerConfiguration )
    summary_incision_ratio: __.typx.Annotated[
        float,
        __.ddoc.Doc(
            ''' Ratio of introduction width to full width at which to split.

                If ratio is met or exceeded, then introduction and summary are
                split onto consecutive lines.
            ''' ),
    ] = 0.3


class CompositorState( __.immut.DataclassObject ):
    ''' Data transfer object for textualizer state. '''

    configuration: CompositorConfiguration
    linearizer: LinearizerState

    @classmethod
    def from_configuration(
        cls,
        configuration: CompositorConfiguration,
        control: __.TextualizationControl,
    ) -> __.typx.Self:
        linearizer = LinearizerState.from_configuration(
            configuration = configuration.linearizercfg, control = control )
        return cls( configuration = configuration, linearizer = linearizer )


COMPOSITOR_CONFIGURATION_DEFAULT = CompositorConfiguration( )
INTRODUCER_CONFIGURATION_DEFAULT = IntroducerConfiguration( )
