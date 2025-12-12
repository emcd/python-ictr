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


''' Conversion of objects to lines of text. '''


from . import __
from . import core as _core


class Linearizer( __.Linearizer ):

    configuration: __.typx.Annotated[
        _core.LinearizerConfiguration,
        __.ddoc.Doc( ''' Default behaviors for textual linearizer. ''' ),
    ] = __.dcls.field( default_factory = _core.LinearizerConfiguration )

    def __call__(
        self,
        control: __.TextualizationControl,
        entity: object,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> tuple[ str, ... ]:
        auxdata = _core.LinearizerState.from_configuration(
            configuration = self.configuration, control = control )
        return linearize_omni( auxdata, entity, columns_max = columns_max )


def linearize_exception_plain(
    auxdata: _core.LinearizerState,
    exception: BaseException,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    ecfg = auxdata.configuration.exceptionscfg
    tbe = __.tb.TracebackException.from_exception( exception )
    lines = [ *ecfg.interpolate( exception ) ]
    if ecfg.enable_stacktraces:
        lines.extend(
            linearize_stacktrace_plain( auxdata, tbe.stack, columns_max ) )
    # TODO: Process '__cause__' and '__context__'.
    # TODO: Process exception groups.
    return tuple( lines )


def linearize_exception_rich(
    auxdata: _core.LinearizerState,
    exception: BaseException,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    # TODO: Ensure that exception groups are handled properly.
    ecfg = auxdata.configuration.exceptionscfg
    capture = __.io.StringIO( )
    console = __.produce_rich_console( auxdata.control, capture, columns_max )
    if not ecfg.enable_stacktraces:
        console.print( exception )
        return tuple( capture.getvalue( ).split( '\n' ) )
    traceback = __.rich_traceback.Traceback.from_exception(
        type( exception ), exception, exception.__traceback__ )
    console.print( traceback )
    return tuple( capture.getvalue( ).split( '\n' ) )


def linearize_object_plain(
    auxdata: _core.LinearizerState,
    entity: object,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    # TODO? Pass configurable indentation width.
    text = (
        __.pprint.saferepr( entity ) if __.is_absent( columns_max )
        else __.pprint.pformat( entity, indent = 2, width = columns_max ) )
    return tuple( text.split( '\n' ) )


def linearize_object_rich(
    auxdata: _core.LinearizerState,
    entity: object,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    capture = __.io.StringIO( )
    console = __.produce_rich_console( auxdata.control, capture, columns_max )
    console.print( entity )
    return tuple( capture.getvalue( ).split( '\n' ) )


def linearize_omni(
    auxdata: _core.LinearizerState,
    entity: object,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    if auxdata.colorize:
        return linearize_omni_rich( auxdata, entity, columns_max )
    return linearize_omni_plain( auxdata, entity, columns_max )


def linearize_omni_plain(
    auxdata: _core.LinearizerState,
    entity: object,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    if isinstance( entity, str ):
        return linearize_text_plain( auxdata, entity, columns_max )
    if isinstance( entity, BaseException ):
        return linearize_exception_plain( auxdata, entity, columns_max )
    return linearize_object_plain( auxdata, entity, columns_max )


def linearize_omni_rich(
    auxdata: _core.LinearizerState,
    entity: object,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    if isinstance( entity, str ):
        return linearize_text_rich( auxdata, entity, columns_max )
    if isinstance( entity, BaseException ):
        return linearize_exception_rich( auxdata, entity, columns_max )
    return linearize_object_rich( auxdata, entity, columns_max )


def linearize_stacktrace_plain(
    auxdata: _core.LinearizerState,
    stacktrace: __.tb.StackSummary,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    infinite_lines = __.is_absent( columns_max )
    lines: list[ str ] = [ ]
    for frame in stacktrace:
        filename_part = f"File '{frame.filename}'"
        lineno_part = f"line {frame.lineno}" if frame.lineno else ''
        name_part = f"in {frame.name}"
        parts = ( filename_part, lineno_part, name_part )
        address = ', '.join( filter( None, parts ) )
        address_size = len( address )
        if infinite_lines or address_size <= columns_max:
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
                linearize_text_plain(
                    auxdata, line,
                    __.absent if infinite_lines else columns_max - 4 ) )
            lines.append( "    {}".format( next( lines_ ) ) )
            lines.extend( f"      {line_}" for line_ in lines_ )
    return tuple( lines )


def linearize_stacktrace_rich(
    auxdata: _core.LinearizerState,
    stacktrace: __.tb.StackSummary,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    frames = [
        __.rich_traceback.Frame(
            frame.filename, frame.lineno or -1, frame.name, frame.line or '' )
        for frame in stacktrace ]
    stack = __.rich_traceback.Stack(
        exc_type = 'Callstack', exc_value = 'Inspection', frames = frames )
    trace = __.rich_traceback.Trace( stacks = [ stack ] )
    traceback = __.rich_traceback.Traceback( trace = trace )
    capture = __.io.StringIO( )
    console = __.produce_rich_console( auxdata.control, capture, columns_max )
    console.print( traceback )
    # TODO? Remove exception lines.
    return tuple( capture.getvalue( ).split( '\n' ) )


def linearize_text_plain(
    auxdata: _core.LinearizerState,
    text: str,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    text_no_ansi = __.remove_ansi_c1_sequences( text )
    if __.is_absent( columns_max ):
        return tuple( text_no_ansi.split( '\n' ) )
    configuration = auxdata.configuration
    incise_excesses = (
        configuration.incision_boundary
        is not _core.IncisionBoundaries.Nowhere )
    incise_naturally = (
        configuration.incision_boundary
        is _core.IncisionBoundaries.Wordsplits )
    # TODO? Account for wide characters.
    return tuple( __.textwrap.wrap(
        text_no_ansi,
        break_long_words = incise_excesses,
        break_on_hyphens = incise_naturally,
        width = columns_max ) )


def linearize_text_rich(
    auxdata: _core.LinearizerState,
    text: str,
    columns_max: __.Absential[ int ] = __.absent,
) -> tuple[ str, ... ]:
    configuration = auxdata.configuration
    text_ = __.rich_text.Text.from_ansi( text )
    infinite_lines = __.is_absent( columns_max )
    incise = (
            not infinite_lines
        and configuration.incision_boundary
            is not _core.IncisionBoundaries.Nowhere )
    capture = __.io.StringIO( )
    console = __.produce_rich_console( auxdata.control, capture, columns_max )
    console.print(
        text_,
        overflow = 'ignore' if infinite_lines else 'fold',
        no_wrap = not incise )
    return tuple( capture.getvalue( ).split( '\n' ) )
