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


''' Formatters, formatter factories, and auxiliary functions and types. '''


from . import __
from . import printers as _printers
from . import records as _records


PrefixEmitter: __.typx.TypeAlias = (
    __.typx.Callable[
        [ _printers.TextualizerControl, _records.Record ], str ] )
PrefixEmitterUnion: __.typx.TypeAlias = str | PrefixEmitter


class ColumnsConstraints( __.enum.Enum ):
    ''' How to constrain text which exceeds maximum columns. '''

    Continue    = __.enum.auto( )  # overflow
    Complect    = __.enum.auto( )  # fold/wrap
    Truncate    = __.enum.auto( )  # chop/cut


class IncisionBoundaries( __.enum.Enum ):
    ''' Where to constrain text which exceeds maximum columns. '''

    Anywhere    = __.enum.auto( )
    Wordsplits  = __.enum.auto( )  # hyphens + whitespace
    Whitespace  = __.enum.auto( )  # horizontal spaces and tabs


class PrefixEmission( __.immut.DataclassObject ):
    ''' Structure for emitted prefix. '''

    text: str
    columns_count: int  # visible


class Textualizer( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Abstract base class for textualizers. '''

    @__.abc.abstractmethod
    def __call__(
        self, control: _printers.TextualizerControl, record: _records.Record
    ) -> str:
        ''' Renders a record as text. '''
        raise NotImplementedError


class TextualizerConfiguration( __.immut.DataclassObject ):
    ''' Behaviors and format for text from default textualizer. '''

    base_prefix: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Prefix before every line. ''' )
    ] = ''
    columns_constraint: __.typx.Annotated[
        ColumnsConstraints,
        __.ddoc.Doc(
            ''' How to constrain text which exceeds maximum columns. ''' ),
    ] = ColumnsConstraints.Complect
    columns_count: __.typx.Annotated[
        __.typx.Optional[ int ],
        __.ddoc.Doc(
            ''' How many columns per line to assume if printer does not tell.

                If ``None``, then infinite number of columns is assumed.
            ''' ),
    ] = None
    detail_prefix: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Prefix for message detail. ''' )
    ] = ''
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
    prefix_incision_ratio: __.typx.Annotated[
        float,
        __.ddoc.Doc(
            ''' Ratio of prefix width to full width at which to split.

                If ratio is met or exceeded, then prefix and summary are
                split onto consecutive lines.
            ''' ),
    ] = 0.3


class TextualizerDefault( Textualizer ):
    ''' Simple textualizer. '''

    configuration: __.typx.Annotated[
        TextualizerConfiguration,
        __.ddoc.Doc( ''' Default behaviors and format for text. ''' ),
    ] = __.dcls.field( default_factory = TextualizerConfiguration )
    prefix_emitter: __.typx.Annotated[
        PrefixEmitterUnion,
        __.ddoc.Doc(
            ''' String or factory which produces prefix string.

                Factory takes control object and record as arguments.
                Returns prefix string.
            ''' ),
    ] = 'ictr| '

    def __call__(
        self, control: _printers.TextualizerControl, record: _records.Record
    ) -> str:
        configuration = self.configuration
        content = record.content
        prefix = _render_prefix(
            self.prefix_emitter, control, configuration, record )
        if isinstance( content, _records.MessageContent ):
            summary = _render_summary(
                control, configuration, prefix, content.summary )
            details = _render_details(
                control, configuration, prefix, content.details )
            return configuration.details_separator.join( (
                summary, *details ) )
        raise NotImplementedError  # TODO: Proper error.


def _count_columns_visual( text: str ) -> int:
    # Note: If CSI ED ("Erase on Display") or EL ("Erase in Line") sequences
    #       are used within the text, then the count will not be accurate.
    text_no_ansi = _printers.remove_ansi_c1_sequences( text )
    return __.wcwidth.wcswidth( text_no_ansi )


def _render_details(
    control: _printers.TextualizerControl,
    configuration: TextualizerConfiguration,
    prefix: PrefixEmission,
    content: _records.MessageDetails,
) -> tuple[ str, ... ]:
    # TODO: Implement.
    return ( )


def _render_prefix(
    emitter: PrefixEmitterUnion,
    control: _printers.TextualizerControl,
    configuration: TextualizerConfiguration,
    record: _records.Record,
) -> PrefixEmission:
    text = (
        emitter if isinstance( emitter, str )
        else emitter( control, record ) )
    columns_count = _count_columns_visual( text )
    return PrefixEmission( text = text, columns_count = columns_count )


def _render_summary(
    control: _printers.TextualizerControl,
    configuration: TextualizerConfiguration,
    prefix: PrefixEmission,
    summary: _records.MessageSummary,
) -> str:
    line_initial = _render_summary_initial(
        control, configuration, prefix, summary )
    lines_subsequent = _render_summary_subsequent(
        control, configuration, summary )
    return '\n'.join( ( line_initial, *lines_subsequent ) )


def _render_summary_core(
    control: _printers.TextualizerControl,
    configuration: TextualizerConfiguration,
    summary: _records.MessageSummary,
) -> str:
    if isinstance( summary, str ): return summary
    if isinstance( summary, BaseException ):
        # TODO: Render with exception template.
        return str( summary )
    # TODO? 'pformat' other objects.
    raise NotImplementedError  # TODO: Proper error.


def _render_summary_initial(
    control: _printers.TextualizerControl,
    configuration: TextualizerConfiguration,
    prefix: PrefixEmission,
    summary: _records.MessageSummary,
) -> str:
    line_columns_total = control.columns_count or configuration.columns_count
    infinite_lines = line_columns_total is None
    core = _render_summary_core( control, configuration, summary )
    columns_total = (
            _count_columns_visual( configuration.base_prefix )
        +   prefix.columns_count + 1
        +   _count_columns_visual( core ) )
    prefix_incision_ratio = configuration.prefix_incision_ratio
    isolate_prefix = 0 == prefix_incision_ratio
    if not isolate_prefix and not infinite_lines:
        isolate_prefix = columns_total > line_columns_total
    if not isolate_prefix and not infinite_lines:
        isolate_prefix = (
            prefix.columns_count
            >= line_columns_total * prefix_incision_ratio )
    if isolate_prefix:
        lines: list[ str ] = [ prefix.text ]
        if infinite_lines: lines.append( core )
        else:
            match configuration.columns_constraint:
                case ColumnsConstraints.Continue:
                    lines.append( core )
                case ColumnsConstraints.Complect:
                    # TODO: Implement.
                    pass
                case ColumnsConstraints.Truncate:
                    # TODO: Implement.
                    pass
        return '\n'.join( map(
            lambda line: f"{configuration.base_prefix}{line}", lines ) )
    return "{}{} {}".format( configuration.base_prefix, prefix.text, core )


def _render_summary_subsequent(
    control: _printers.TextualizerControl,
    configuration: TextualizerConfiguration,
    summary: _records.MessageSummary,
) -> tuple[ str, ... ]:
    lines: list[ str ] = [ ]
    if isinstance( summary, str ):
        # TODO: Render with wrapping.
        lines.append( summary )
    elif isinstance( summary, BaseException ):
        # TODO: Render with stack frames, exception template, and wrapping.
        lines.append( str( summary ) )
    # TODO: Implement.
    return tuple( lines )


TextualizerFactory: __.typx.TypeAlias = (
    __.typx.Callable[
        [ _printers.TextualizerControl, _records.Record ], Textualizer ] )
