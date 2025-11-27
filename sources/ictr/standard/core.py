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
    # TODO? Merge into IntroducerConfiguration.
    ''' Auxiliary functions used by textualizers and interpolation.

        Typically used by unit tests to inject mock dependencies,
        but can also be used to deeply customize output.
    '''

    exc_info_discoverer: __.typx.Annotated[
        __.typx.Callable[ [ ], __.ExceptionInfo ],
        __.ddoc.Doc( ''' Returns information on current exception. ''' ),
    ] = __.sys.exc_info
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
    ] = __.time.strftime


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


class IntroductionDecors( __.enum.IntFlag ):
    ''' Decoration styles for introductions. '''

    Plain =     0
    Color =     __.enum.auto( )
    Emoji =     __.enum.auto( )


class LabelPresentations( __.enum.IntFlag ):
    ''' How introduction labels should be presented. '''

    Nothing =   0
    Words =     __.enum.auto( )
    Emoji =     __.enum.auto( )


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
            ''' Mapping of interpolant names to style objects.

                Ignored if not using ``rich``.
            ''' ),
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
    control: __.TextualizerControl
    columns_max: __.typx.Annotated[
        __.Absential[ int ],
        __.ddoc.Doc(
            ''' Available line length (maximum columns) of target. ''' ),
    ] = __.absent


class TextualizerConfiguration( __.immut.DataclassObject ):
    ''' Behaviors and format for text from standard textualizer. '''

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
    exception_format: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Template for exception message. ''' )
    ] = '[{name}] {message}'
    incision_boundary: __.typx.Annotated[
        IncisionBoundaries,
        __.ddoc.Doc(
            ''' Where to constrain text which exceeds maximum columns. ''' ),
    ] = IncisionBoundaries.Wordsplits
    line_prefix: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Prefix before every line. ''' )
    ] = ''
    # TODO: stacktrace_exceptiongroups: Traceback each exception group member?
    summary_incision_ratio: __.typx.Annotated[
        float,
        __.ddoc.Doc(
            ''' Ratio of introduction width to full width at which to split.

                If ratio is met or exceeded, then introduction and summary are
                split onto consecutive lines.
            ''' ),
    ] = 0.3


class TextualizerState( __.immut.DataclassObject ):
    ''' Data transfer object for textualizer state. '''

    configuration: TextualizerConfiguration
    control: __.TextualizerControl
    columns_constraint: __.typx.Annotated[
        ColumnsConstraints,
        __.ddoc.Doc( ''' Effective columns constraint for lines. ''' ),
    ] = ColumnsConstraints.Exceed
    columns_max: __.typx.Annotated[
        __.Absential[ int ],
        __.ddoc.Doc(
            ''' Available line length (maximum columns) of target. ''' ),
    ]

    @classmethod
    def from_configuration(
        cls,
        configuration: TextualizerConfiguration,
        control: __.TextualizerControl,
    ) -> __.typx.Self:
        columns_constraint = configuration.columns_constraint
        columns_max = control.columns_max or configuration.columns_max
        if columns_max is None:
            columns_constraint = ColumnsConstraints.Exceed
            columns_max = __.absent
        return cls(
            configuration = configuration,
            control = control,
            columns_constraint = columns_constraint,
            columns_max = columns_max )


AUXILIARIES_DEFAULT = Auxiliaries( )
INTRODUCER_CONFIGURATION_DEFAULT = IntroducerConfiguration( )
TEXTUALIZER_CONFIGURATION_DEFAULT = TextualizerConfiguration( )
