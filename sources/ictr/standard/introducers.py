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


''' Standard introducer with support for decorations and styles. '''


from . import __
from . import core as _core


class Introducer( __.Introducer ):
    ''' Standard introducer. '''

    configuration: __.typx.Annotated[
        _core.IntroducerConfiguration,
        __.ddoc.Doc(
            ''' Default behaviors and format for introductory text. ''' ),
    ] = __.dcls.field( default_factory = _core.IntroducerConfiguration )

    def __call__(
        self,
        control: __.TextualizationControl,
        record: __.Record,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> str:
        configuration = self.configuration
        auxdata = _core.IntroducerState.from_configuration(
            configuration = configuration,
            control = control,
            columns_max = columns_max )
        if isinstance( record.flavor, int ):
            return _render_trace_label( auxdata, record )
        return _render_nominal_label( auxdata, record )


def _render_nominal_label(
    auxdata: _core.IntroducerState, record: __.Record
) -> str:
    configuration = auxdata.configuration
    styles = dict( configuration.styles )
    flavor = record.flavor
    if isinstance( flavor, int ):
        raise __.FlavorMisclassification( flavor, expectation = 'string' )
    name = __.flavor_aliases_standard.get( flavor, flavor )
    spec = __.flavor_specifications_standard[ name ]
    label = ''
    if configuration.label_as & _core.LabelPresentations.Emoji:
        if configuration.label_as & _core.LabelPresentations.Words:
            label = f"{spec.emoji} {spec.label}"
        else: label = f"{spec.emoji}"
    elif configuration.label_as & _core.LabelPresentations.Words:
        label = f"{spec.label}"
    if auxdata.colorize:
        styles[ 'flavor' ] = _core.Style( fgcolor = spec.color )
    return _render_common( auxdata, record, styles, label )


def _render_trace_label(
    auxdata: _core.IntroducerState, record: __.Record
) -> str:
    # TODO? Option to render indentation guides.
    configuration = auxdata.configuration
    styles = dict( configuration.styles )
    flavor = record.flavor
    if not isinstance( flavor, int ):
        raise __.FlavorMisclassification( flavor, expectation = 'int' )
    level = flavor
    label = ''
    if configuration.label_as & _core.LabelPresentations.Emoji:
        if configuration.label_as & _core.LabelPresentations.Words:
            label = f"🔎 TRACE{level}"
        else: label = '🔎'
    elif configuration.label_as & _core.LabelPresentations.Words:
        label = f"TRACE{level}"
    if auxdata.colorize and level < len( _trace_color_names ):
        styles[ 'flavor' ] = (
            _core.Style( fgcolor = _trace_color_names[ level ] ) )
    return _render_common( auxdata, record, styles, label )


def _render_common(
    auxdata: _core.IntroducerState,
    record: __.Record,
    styles: __.cabc.Mapping[ str, _core.Style ],
    label: str
) -> str:
    # TODO? Performance optimization: Only compute and interpolate PID, thread,
    #       and timestamp, if capabilities set permits.
    configuration = auxdata.configuration
    auxiliaries = configuration.auxiliaries
    thread = auxiliaries.thread_discoverer( )
    interpolants: dict[ str, str ] = {
        'flavor': label,
        'address': record.address,
        'timestamp': auxiliaries.time_formatter( configuration.ts_format ),
        'process_id': str( auxiliaries.pid_discoverer( ) ),
        'thread_id': str( thread.ident ),
        'thread_name': thread.name,
    }
    if auxdata.colorize:
        _stylize_interpolants( auxdata, interpolants, styles )
    return configuration.template.format( **interpolants )


def _stylize_interpolants(
    auxdata: _core.IntroducerState,
    interpolants: dict[ str, str ],
    styles: __.cabc.Mapping[ str, _core.Style ],
) -> None:
    style_default = styles.get( 'flavor' )
    interpolants_: dict[ str, str ] = { }
    for iname, ivalue in interpolants.items( ):
        style = styles.get( iname, style_default )
        if not style: continue # pragma: no branch
        capture = __.io.StringIO( )
        console = __.produce_rich_console(
            auxdata.control, capture, auxdata.columns_max )
        style_ = __.rich_style.Style( color = style.fgcolor )
        console.print( ivalue, end = '', highlight = False, style = style_  )
        interpolants_[ iname ] = capture.getvalue( )
    interpolants.update( interpolants_ )


_trace_color_names: tuple[ str, ... ] = (
    'grey85', 'grey82', 'grey78', 'grey74', 'grey70',
    'grey66', 'grey62', 'grey58', 'grey54', 'grey50' )

_trace_prefix_styles: tuple[ _core.Style, ... ] = tuple(
    _core.Style( fgcolor = name ) for name in _trace_color_names )
