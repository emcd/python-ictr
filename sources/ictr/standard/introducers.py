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


class IntroducerConfiguration( __.immut.DataclassObject ):
    ''' Behaviors and format for text from standard introducer. '''

    auxiliaries: __.typx.Annotated[
        _core.Auxiliaries,
        __.typx.Doc( ''' Auxiliaries for interpolation. ''' ),
    ] = __.dcls.field( default_factory = _core.Auxiliaries )
    colorize: __.typx.Annotated[
        bool, __.typx.Doc( ''' Attempt to colorize? ''' )
    ] = True
    label_as: __.typx.Annotated[
        _core.LabelPresentations,
        __.ddoc.Doc(
            ''' How to present prefix label.

                ``Words``: As words like ``TRACE0`` or ``ERROR``.
                ``Emoji``: As emoji like ``🔎`` or ``❌``.

                For both emoji and words: ``Emoji | Words``.
            ''' )
    ] = _core.LabelPresentations.Words
    styles: __.typx.Annotated[
        _core.InterpolantsStylesRegistry,
        __.ddoc.Doc(
            ''' Mapping of interpolant names to style objects. ''' ),
    ] = __.dcls.field( default_factory = _core.InterpolantsStylesRegistry )
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


INTRODUCER_CONFIGURATION_DEFAULT = IntroducerConfiguration( )


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


class Introducer( __.Introducer ):
    ''' Standard introducer. '''

    configuration: __.typx.Annotated[
        IntroducerConfiguration,
        __.ddoc.Doc(
            ''' Default behaviors and format for introductory text. ''' ),
    ] = __.dcls.field( default_factory = IntroducerConfiguration )

    def __call__(
        self,
        control: __.TextualizationControl,
        record: __.Record,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> str:
        configuration = self.configuration
        auxdata = IntroducerState.from_configuration(
            configuration = configuration,
            control = control,
            columns_max = columns_max )
        if isinstance( record.flavor, int ):
            return _render_trace_label( auxdata, record )
        return _render_nominal_label( auxdata, record )


def _render_nominal_label(
    auxdata: IntroducerState, record: __.Record
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
    auxdata: IntroducerState, record: __.Record
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
    auxdata: IntroducerState,
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
    auxdata: IntroducerState,
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
