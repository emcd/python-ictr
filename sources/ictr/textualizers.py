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


_ENRICH = False
try:
    import rich.console as _rich_console
    import rich.text as _rich_text
    import rich.traceback as _rich_traceback
    _ENRICH = True  # pyright: ignore[reportConstantRedefinition]
except ImportError: pass


IntroducerFunction: __.typx.TypeAlias = (
    __.typx.Callable[
        [ _printers.TextualizerControl, _records.Record ], str ] )
Introducer: __.typx.TypeAlias = str | IntroducerFunction


class ColumnsConstraints( __.enum.Enum ):
    ''' How to constrain text which exceeds maximum columns. '''

    Continue    = __.enum.auto( )  # overflow
    Complect    = __.enum.auto( )  # fold/wrap
    Truncate    = __.enum.auto( )  # chop/cut


class IncisionBoundaries( __.enum.Enum ):
    ''' Where to constrain text which exceeds maximum columns. '''

    Nowhere     = __.enum.auto( )
    Whitespace  = __.enum.auto( )  # horizontal spaces and tabs
    Wordsplits  = __.enum.auto( )  # hyphens + whitespace
    Anywhere    = __.enum.auto( )


class PrefixEmission( __.immut.DataclassObject ):
    # TODO: Rename to 'Introduction'.
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
        Introducer,
        __.ddoc.Doc(
            ''' String or factory which produces prefix string.

                Factory takes control object and record as arguments.
                Returns prefix string.
            ''' ),
    ] = 'ictr| '

    def __call__(
        self, control: _printers.TextualizerControl, record: _records.Record
    ) -> str:
        auxdata = TextualizerState.from_configuration_and_control(
            self.configuration, control )
        configuration = self.configuration
        content = record.content
        prefix = _render_prefix( self.prefix_emitter, auxdata, record )
        if isinstance( content, _records.MessageContent ):
            summary = _render_summary( auxdata, prefix, content.summary )
            details = _render_details( auxdata, prefix, content.details )
            return configuration.details_separator.join( (
                summary, *details ) )
        raise NotImplementedError  # TODO: Proper error.


class TextualizerState( __.immut.DataclassObject ):
    ''' Data transfer object for simple textualizer state. '''

    configuration: TextualizerConfiguration
    control: _printers.TextualizerControl
    infinite_lines: bool
    line_columns_total: int

    @classmethod
    def from_configuration_and_control(
        cls,
        configuration: TextualizerConfiguration,
        control: _printers.TextualizerControl,
    ) -> __.typx.Self:
        line_columns_total_nullable = (
            control.columns_count or configuration.columns_count )
        infinite_lines = line_columns_total_nullable is None
        line_columns_total = (
            __.sys.maxsize if infinite_lines else line_columns_total_nullable )
        return cls(
            configuration = configuration,
            control = control,
            infinite_lines = infinite_lines,
            line_columns_total = line_columns_total )


def _complect_exception_plain(
    auxdata: TextualizerState, columns_max: int, exception: BaseException
) -> tuple[ str, ... ]:
    # tbe = __.tb.TracebackException.from_exception( exception )
    # TODO: Implement
    return ( )


def _complect_exception_rich(
    auxdata: TextualizerState, columns_max: int, exception: BaseException
) -> tuple[ str, ... ]:
    # TODO: Ensure that exception groups are handled properly.
    console = _produce_rich_console( auxdata, columns_max )
    traceback = _rich_traceback.Traceback.from_exception(
        type( exception ), exception, exception.__traceback__ )
    with console.capture( ) as capture:
        console.print( traceback )
    return tuple( capture.get( ).split( '\n' ) )


def _complect_object_plain(
    auxdata: TextualizerState, columns_max: int, entity: object
) -> tuple[ str, ... ]:
    # TODO? Pass configurable indentation width.
    text = __.pprint.pformat( entity, indent = 2, width = columns_max )
    return tuple( text.split( '\n' ) )


def _complect_object_rich(
    auxdata: TextualizerState, columns_max: int, entity: object
) -> tuple[ str, ... ]:
    console = _produce_rich_console( auxdata, columns_max )
    with console.capture( ) as capture:
        console.print( entity )
    return tuple( capture.get( ).split( '\n' ) )


def _complect_text_plain(
    auxdata: TextualizerState, columns_max: int, text: str
) -> tuple[ str, ... ]:
    configuration = auxdata.configuration
    incise_excesses = (
        configuration.incision_boundary is not IncisionBoundaries.Nowhere )
    incise_naturally = (
        configuration.incision_boundary is IncisionBoundaries.Wordsplits )
    text_no_ansi = _printers.remove_ansi_c1_sequences( text )
    # TODO? Account for wide characters.
    return tuple( __.textwrap.wrap(
        text_no_ansi,
        break_long_words = incise_excesses,
        break_on_hyphens = incise_naturally,
        width = columns_max ) )


def _complect_text_rich(
    auxdata: TextualizerState, columns_max: int, text: str
) -> tuple[ str, ... ]:
    configuration = auxdata.configuration
    text_ = _rich_text.Text.from_ansi( text )
    incise = (
        configuration.incision_boundary is not IncisionBoundaries.Nowhere )
    console = _produce_rich_console( auxdata, columns_max )
    with console.capture( ) as capture:
        console.print( text_, overflow = 'fold', no_wrap = not incise )
    return tuple( capture.get( ).split( '\n' ) )


def _count_columns_visual( text: str ) -> int:
    # Note: If CSI ED ("Erase on Display") or EL ("Erase in Line") sequences
    #       are used within the text, then the count will not be accurate.
    text_no_ansi = _printers.remove_ansi_c1_sequences( text )
    return __.wcwidth.wcswidth( text_no_ansi )


def _produce_rich_console(
    auxdata: TextualizerState, columns_max: int
) -> _rich_console.Console:
    control = auxdata.control
    charset = control.charset or ''
    colorize = control.colorize
    columns_max_nullable = None if auxdata.infinite_lines else columns_max
    safe = charset.startswith( 'utf-' )
    blackhole = __.io.StringIO( )
    return _rich_console.Console(
        file = blackhole,
        force_terminal = colorize,
        no_color = not colorize,
        safe_box = safe,
        width = columns_max_nullable )


def _render_details(
    auxdata: TextualizerState,
    prefix: PrefixEmission,
    content: _records.MessageDetails,
) -> tuple[ str, ... ]:
    # TODO: Implement.
    return ( )


def _render_prefix(
    emitter: Introducer,
    auxdata: TextualizerState,
    record: _records.Record,
) -> PrefixEmission:
    text = (
        emitter if isinstance( emitter, str )
        else emitter( auxdata.control, record ) )
    columns_count = _count_columns_visual( text )
    return PrefixEmission( text = text, columns_count = columns_count )


def _render_summary(
    auxdata: TextualizerState,
    prefix: PrefixEmission,
    summary: _records.MessageSummary,
) -> str:
    line_initial = _render_summary_initial( auxdata, prefix, summary )
    lines_subsequent = _render_summary_subsequent( auxdata, summary )
    return '\n'.join( ( line_initial, *lines_subsequent ) )


def _render_summary_core(
    auxdata: TextualizerState, summary: _records.MessageSummary
) -> str:
    if isinstance( summary, str ):
        text = summary
        if not _ENRICH:
            text = _printers.remove_ansi_c1_sequences( text )
        return text
    if isinstance( summary, BaseException ):
        eclass = type( summary )
        qname = eclass.__qualname__
        return auxdata.configuration.exception_format.format(
            message = str( summary ),
            name = eclass.__name__,
            qname = qname,
            fqname = f"{eclass.__module__}.{qname}" )
    return ''  # Assume complex render in subsequent lines.


def _render_summary_initial(
    auxdata: TextualizerState,
    prefix: PrefixEmission,
    summary: _records.MessageSummary,
) -> str:
    configuration = auxdata.configuration
    prefix_columns_count = (
            _count_columns_visual( auxdata.configuration.base_prefix )
        +   prefix.columns_count + 1 )
    core = _render_summary_core( auxdata, summary )
    columns_total = prefix_columns_count + _count_columns_visual( core )
    prefix_incision_ratio = configuration.prefix_incision_ratio
    isolate_prefix = 0 == prefix_incision_ratio
    if not isolate_prefix and not auxdata.infinite_lines:
        isolate_prefix = columns_total > auxdata.line_columns_total
    if not isolate_prefix and not auxdata.infinite_lines:
        isolate_prefix = (
            prefix.columns_count
            >= auxdata.line_columns_total * prefix_incision_ratio )
    # TODO: If prefix is not isolated, still allow message to wrap.
    if isolate_prefix:
        lines: list[ str ] = [ prefix.text ]
        if auxdata.infinite_lines: lines.append( core )
        else:
            columns_allocation = (
                    auxdata.line_columns_total
                -   _count_columns_visual( configuration.base_prefix ) )
            match configuration.columns_constraint:
                case ColumnsConstraints.Continue:
                    lines.append( core )
                case ColumnsConstraints.Complect:
                    lines.extend( _complect_text_plain(
                        auxdata, columns_allocation, core ) )
                case ColumnsConstraints.Truncate:
                    lines.append(
                        _truncate_visual( core, columns_allocation ) )
        return '\n'.join( map(
            lambda line: f"{configuration.base_prefix}{line}", lines ) )
    return "{}{} {}".format( configuration.base_prefix, prefix.text, core )


def _render_summary_subsequent(
    auxdata: TextualizerState,
    summary: _records.MessageSummary,
) -> tuple[ str, ... ]:
    lines: list[ str ] = [ ]
    if isinstance( summary, str ): return ( )
    if isinstance( summary, BaseException ):
        # TODO: Render with stack frames, exception template, and wrapping.
        lines.append( str( summary ) )
    else:
        # TODO? 'pformat' other objects in subsequent lines.
        pass
    # TODO: Prepend base prefix and blank detail prefix to each line.
    return tuple( lines )


# TODO: _truncate_text_plain and _truncate_text_rich
def _truncate_visual( text: str, columns_max: int ) -> str:
    lsize = 0
    for i, c in enumerate( text ):
        csize = __.wcwidth.wcwidth( c )
        csize = max( 0, csize )  # control or combining character
        if lsize + csize > columns_max:
            # TODO? Add ellipsis.
            return text[ : i ]
        lsize += csize
    return text


TextualizerFactory: __.typx.TypeAlias = (
    __.typx.Callable[
        [ _printers.TextualizerControl, _records.Record ], Textualizer ] )
