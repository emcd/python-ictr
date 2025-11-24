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
    # Truncate    = __.enum.auto( )  # chop/cut


class IncisionBoundaries( __.enum.Enum ):
    ''' Where to constrain text which exceeds maximum columns. '''

    Nowhere     = __.enum.auto( )
    Whitespace  = __.enum.auto( )  # horizontal spaces and tabs
    Wordsplits  = __.enum.auto( )  # hyphens + whitespace
    Anywhere    = __.enum.auto( )


class Introduction( __.immut.DataclassObject ):
    ''' Structure for introduction. '''

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
    summary_incision_ratio: __.typx.Annotated[
        float,
        __.ddoc.Doc(
            ''' Ratio of introduction width to full width at which to split.

                If ratio is met or exceeded, then introduction and summary are
                split onto consecutive lines.
            ''' ),
    ] = 0.3


class TextualizerDefault( Textualizer ):
    ''' Simple textualizer. '''

    configuration: __.typx.Annotated[
        TextualizerConfiguration,
        __.ddoc.Doc( ''' Default behaviors and format for text. ''' ),
    ] = __.dcls.field( default_factory = TextualizerConfiguration )
    introducer: __.typx.Annotated[
        Introducer,
        __.ddoc.Doc(
            ''' String or factory which produces introduction string.

                Factory takes control object and record as arguments.
                Returns introduction string.
            ''' ),
    ] = 'ictr| '

    def __call__(
        self, control: _printers.TextualizerControl, record: _records.Record
    ) -> str:
        auxdata = TextualizerState.from_configuration_and_control(
            self.configuration, control )
        configuration = self.configuration
        content = record.content
        introduction = _render_introduction(
            auxdata, self.introducer, record )
        if isinstance( content, _records.MessageContent ):
            summary = _render_summary( auxdata, introduction, content.summary )
            details = tuple(
                _render_detail( auxdata, detail )
                for detail in content.details )
            return configuration.details_separator.join( (
                summary, *details ) )
        raise NotImplementedError  # TODO: Proper error.


class TextualizerState( __.immut.DataclassObject ):
    ''' Data transfer object for simple textualizer state. '''

    configuration: TextualizerConfiguration
    control: _printers.TextualizerControl
    columns_constraint: ColumnsConstraints
    infinite_lines: bool
    line_columns_total: int  # TODO: Convert to dynamic property.

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
        columns_constraint = configuration.columns_constraint
        if infinite_lines:
            columns_constraint = ColumnsConstraints.Continue
        return cls(
            configuration = configuration,
            control = control,
            columns_constraint = columns_constraint,
            infinite_lines = infinite_lines,
            line_columns_total = line_columns_total )


def _complect_exception_plain(
    auxdata: TextualizerState,
    columns_max: int,
    exception: BaseException,
    trace: bool = False,
) -> tuple[ str, ... ]:
    tbe = __.tb.TracebackException.from_exception( exception )
    eclass = type( exception )
    fqname = f"{eclass.__module__}.{eclass.__qualname__}"
    lines = [ f"{fqname}: {exception}" ]
    if trace:
        lines.extend(
            _complect_stacktrace_plain( auxdata, columns_max, tbe.stack ) )
    # TODO: Process '__cause__' and '__context__'.
    # TODO: Process exception groups.
    return tuple( lines )


def _complect_exception_rich(
    auxdata: TextualizerState,
    columns_max: int,
    exception: BaseException,
    trace: bool = False,
) -> tuple[ str, ... ]:
    # TODO: Ensure that exception groups are handled properly.
    capture = __.io.StringIO( )
    console = _produce_rich_console( auxdata, capture, columns_max )
    if not trace:
        console.print( exception )
        return tuple( capture.getvalue( ).split( '\n' ) )
    traceback = _rich_traceback.Traceback.from_exception(
        type( exception ), exception, exception.__traceback__ )
    console.print( traceback )
    return tuple( capture.getvalue( ).split( '\n' ) )


def _complect_object_plain(
    auxdata: TextualizerState, columns_max: int, entity: object
) -> tuple[ str, ... ]:
    # TODO? Pass configurable indentation width.
    text = __.pprint.pformat( entity, indent = 2, width = columns_max )
    return tuple( text.split( '\n' ) )


def _complect_object_rich(
    auxdata: TextualizerState, columns_max: int, entity: object
) -> tuple[ str, ... ]:
    capture = __.io.StringIO( )
    console = _produce_rich_console( auxdata, capture, columns_max )
    console.print( entity )
    return tuple( capture.getvalue( ).split( '\n' ) )


def _complect_omni(
    auxdata: TextualizerState, columns_max: int, entity: object
) -> tuple[ str, ... ]:
    if _ENRICH: return _complect_omni_rich( auxdata, columns_max, entity )
    return _complect_omni_plain( auxdata, columns_max, entity )


def _complect_omni_plain(
    auxdata: TextualizerState, columns_max: int, entity: object
) -> tuple[ str, ... ]:
    if isinstance( entity, str ):
        return _complect_text_plain( auxdata, columns_max, entity )
    if isinstance( entity, BaseException ):
        return _complect_exception_plain( auxdata, columns_max, entity )
    return _complect_object_plain( auxdata, columns_max, entity )


def _complect_omni_rich(
    auxdata: TextualizerState, columns_max: int, entity: object
) -> tuple[ str, ... ]:
    if isinstance( entity, str ):
        return _complect_text_rich( auxdata, columns_max, entity )
    if isinstance( entity, BaseException ):
        return _complect_exception_rich( auxdata, columns_max, entity )
    return _complect_object_rich( auxdata, columns_max, entity )


def _complect_stacktrace_plain(
    auxdata: TextualizerState,
    columns_max: int,
    stacktrace: __.tb.StackSummary,
) -> tuple[ str, ... ]:
    lines: list[ str ] = [ ]
    for frame in stacktrace:
        filename_part = f"File '{frame.filename}'"
        lineno_part = f"line {frame.lineno}" if frame.lineno else ''
        name_part = f"in {frame.name}"
        parts = ( filename_part, lineno_part, name_part )
        address = ', '.join( filter( None, parts ) )
        address_size = len( address )
        if address_size <= columns_max:
            lines.append( address )
        else:
            excess_size = address_size - columns_max - 2  # sans ', '
            parts = ( lineno_part, name_part )
            address = ', '.join( filter( None, parts ) )
            address_size = len( address )
            if excess_size <= address_size:
                lines.append( filename_part )
            else:
                excess_size = columns_max - len( frame.filename ) + 4
                filename = frame.filename[ excess_size : ]
                # TODO? Drop middle rather than start.
                lines.append( f"File '... {filename}'" )
            lines.append( address )
        if frame.line:
            line = frame.line.strip( )
            # TODO? Apply Pygments to line.
            lines_ = iter(
                _complect_text_plain( auxdata, columns_max - 4, line ) )
            lines.append( "    {}".format( next( lines_ ) ) )
            lines.extend( f"      {line_}" for line_ in lines_ )
    return tuple( lines )


def _complect_stacktrace_rich(
    auxdata: TextualizerState,
    columns_max: int,
    stacktrace: __.tb.StackSummary,
) -> tuple[ str, ... ]:
    frames = [
        _rich_traceback.Frame(
            frame.filename, frame.lineno or -1, frame.name, frame.line or '' )
        for frame in stacktrace ]
    stack = _rich_traceback.Stack(
        exc_type = 'Callstack', exc_value = 'Inspection', frames = frames )
    trace = _rich_traceback.Trace( stacks = [ stack ] )
    traceback = _rich_traceback.Traceback( trace = trace )
    capture = __.io.StringIO( )
    console = _produce_rich_console( auxdata, capture, columns_max )
    console.print( traceback )
    # TODO? Remove exception lines.
    return tuple( capture.getvalue( ).split( '\n' ) )


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
    capture = __.io.StringIO( )
    console = _produce_rich_console( auxdata, capture, columns_max )
    console.print( text_, overflow = 'fold', no_wrap = not incise )
    return tuple( capture.getvalue( ).split( '\n' ) )


def _count_columns_visual( text: str ) -> int:
    # Note: If CSI ED ("Erase on Display") or EL ("Erase in Line") sequences
    #       are used within the text, then the count will not be accurate.
    text_no_ansi = _printers.remove_ansi_c1_sequences( text )
    return __.wcwidth.wcswidth( text_no_ansi )


def _produce_rich_console(
    auxdata: TextualizerState, capture: __.typx.IO[ str ], columns_max: int
) -> _rich_console.Console:
    control = auxdata.control
    charset = control.charset or ''
    colorize = control.colorize
    columns_max_nullable = None if auxdata.infinite_lines else columns_max
    safe = charset.startswith( 'utf-' )
    return _rich_console.Console(
        file = capture,
        force_terminal = colorize,
        no_color = not colorize,
        safe_box = safe,
        width = columns_max_nullable )


def _render_introduction(
    auxdata: TextualizerState,
    introducer: Introducer,
    record: _records.Record,
) -> Introduction:
    text = (
        introducer if isinstance( introducer, str )
        else introducer( auxdata.control, record ) )
    columns_count = _count_columns_visual( text )
    return Introduction( text = text, columns_count = columns_count )


def _render_detail(
    auxdata: TextualizerState, detail: _records.MessageDetail
) -> str:
    match auxdata.columns_constraint:
        case ColumnsConstraints.Complect:
            return _complect_render_detail( auxdata, detail )
        case ColumnsConstraints.Continue:
            return _exact_render_detail( auxdata, detail )


def _complect_render_detail(
    auxdata: TextualizerState, detail: _records.MessageDetail
) -> str:
    configuration = auxdata.configuration
    detail_prefix_i = configuration.detail_prefix_initial
    detail_prefix_i_ccount = _count_columns_visual( detail_prefix_i )
    detail_prefix_s = configuration.detail_prefix_subsequent
    if detail_prefix_s is None:
        detail_prefix_s = ' ' * detail_prefix_i_ccount
    line_prefix = configuration.line_prefix
    prefix_ccount = (
        _count_columns_visual( line_prefix ) + detail_prefix_i_ccount )
    remainder_ccount = auxdata.line_columns_total - prefix_ccount
    lines = iter( _complect_omni( auxdata, remainder_ccount, detail ) )
    line_i = next( lines )
    lines_final = [ f"{line_prefix}{detail_prefix_i}{line_i}" ]
    lines_final.extend(
        f"{line_prefix}{detail_prefix_s}{line}" for line in lines )
    return '\n'.join( lines_final )


def _exact_render_detail(
    auxdata: TextualizerState, detail: _records.MessageDetail
) -> str:
    # TODO: Implement.
    return ''


def _render_summary(
    auxdata: TextualizerState,
    introduction: Introduction,
    summary: _records.MessageSummary,
) -> str:
    match auxdata.columns_constraint:
        case ColumnsConstraints.Complect:
            return _complect_render_summary( auxdata, introduction, summary )
        case ColumnsConstraints.Continue:
            return _exact_render_summary( auxdata, introduction, summary )


def _complect_render_summary(
    auxdata: TextualizerState,
    introduction: Introduction,
    summary: _records.MessageSummary,
) -> str:
    # TODO: Consider continuation prefix.
    configuration = auxdata.configuration
    line_prefix = configuration.line_prefix
    prefix_ccount = _count_columns_visual( line_prefix )
    remainder_ccount = auxdata.line_columns_total - prefix_ccount
    lines_final: list[ str ] = [ ]
    lines = _complect_omni( auxdata, remainder_ccount, summary )
    match len( lines ):
        case 0: raise RuntimeError  # TODO: Appropriate error.
        case 1:
            content = lines[ 0 ]
            incision_point = (
                    configuration.summary_incision_ratio
                *   auxdata.line_columns_total )
            isolate_introduction = (
                incision_point <= introduction.columns_count )
            if not isolate_introduction:
                candidate = f"{introduction.text} {content}"
                candidate_ccount = (
                        prefix_ccount + introduction.columns_count
                    +   _count_columns_visual( content ) + 1 )
                if candidate_ccount <= auxdata.line_columns_total:
                    lines_final.append( candidate )
                else:
                    lines_final.extend( ( introduction.text, *lines ) )
            else:
                lines_final.extend( ( introduction.text, *lines ) )
        case _:
            lines_final.extend( ( introduction.text, *lines ) )
    return '\n'.join( f"{line_prefix}{line}" for line in lines_final )


def _exact_render_summary(
    auxdata: TextualizerState,
    introduction: Introduction,
    summary: _records.MessageSummary,
) -> str:
    # TODO: Implement.
    return ''


# # TODO: _truncate_text_plain and _truncate_text_rich
# def _truncate_visual( text: str, columns_max: int ) -> str:
#     lsize = 0
#     for i, c in enumerate( text ):
#         csize = __.wcwidth.wcwidth( c )
#         csize = max( 0, csize )  # control or combining character
#         if lsize + csize > columns_max:
#             # TODO? Add ellipsis.
#             return text[ : i ]
#         lsize += csize
#     return text


TextualizerFactory: __.typx.TypeAlias = (
    __.typx.Callable[
        [ _printers.TextualizerControl, _records.Record ], Textualizer ] )
