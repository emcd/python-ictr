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


''' Standard compositor and renderers. '''


from . import __
from . import core as _core

from .linearizers import linearize_omni as _linearize_omni


class Compositor( __.Compositor ):
    ''' Standard compositor. '''

    configuration: __.typx.Annotated[
        _core.CompositorConfiguration,
        __.ddoc.Doc( ''' Default behaviors and format for text. ''' ),
    ] = __.dcls.field( default_factory = _core.CompositorConfiguration )
    introducer: __.typx.Annotated[
        __.IntroducerUnion,
        __.ddoc.Doc(
            ''' String or factory which produces introduction string.

                Factory takes control object and record as arguments.
                Returns introduction string.
            ''' ),
    ] = f"{__.package_name}| "

    def __call__(
        self, control: __.TextualizationControl, record: __.Record
    ) -> str:
        configuration = self.configuration
        ecfg = configuration.linearizercfg.exceptionscfg
        auxdata = _core.CompositorState.from_configuration(
            configuration = configuration, control = control )
        content = record.content
        introducer = self.introducer
        introduction = (
            introducer if isinstance( introducer, str )
            else introducer(
                control, record, auxdata.linearizer.columns_max ) )
        if isinstance( content, __.MessageContent ):
            summary_ = content.summary
            exception = (
                None if isinstance( summary_, BaseException )
                else ecfg.discover( ) )
            summary = _render_summary( auxdata, introduction, summary_ )
            details = tuple(
                _render_detail( auxdata, detail )
                for detail in filter( None, ( exception, *content.details ) ) )
            return configuration.details_separator.join( (
                summary, *details ) )
        raise __.ContentMisclassification( type( content ) )


def _calculate_ccount_max(
    initial: str, subsequent: __.typx.Optional[ str ]
) -> int:
    i_ccount = __.count_columns_visual( initial )
    if subsequent is None: return i_ccount
    return max( i_ccount, __.count_columns_visual( subsequent ) )


def _render_detail( auxdata: _core.CompositorState, detail: object ) -> str:
    configuration = auxdata.configuration
    columns_max = auxdata.linearizer.columns_max
    detail_prefix_i = configuration.detail_prefix_initial
    detail_prefix_i_ccount = __.count_columns_visual( detail_prefix_i )
    detail_prefix_s = configuration.detail_prefix_subsequent
    if detail_prefix_s is None:
        detail_prefix_s = ' ' * detail_prefix_i_ccount
    detail_prefix_ccount = _calculate_ccount_max(
        detail_prefix_i, detail_prefix_s )
    line_prefix_ccount = _calculate_ccount_max(
        configuration.line_prefix_initial,
        configuration.line_prefix_subsequent )
    prefix_ccount = line_prefix_ccount + detail_prefix_ccount
    match auxdata.linearizer.columns_constraint:
        case _core.ColumnsConstraints.Complect:
            remainder_ccount = (
                __.absent if __.is_absent( columns_max )
                else columns_max - prefix_ccount )
        case _core.ColumnsConstraints.Exceed:
            remainder_ccount = __.absent
    lines = iter( _linearize_omni(
        auxdata.linearizer, detail, remainder_ccount ) )
    lines_final: list[ str ] = [ ]
    line_i = next( lines )
    _update_lines_collection(
        configuration, lines_final,
        f"{detail_prefix_i}{line_i}",
        tuple( f"{detail_prefix_s}{line}" for line in lines ) )
    return '\n'.join( lines_final )


def _render_summary(
    auxdata: _core.CompositorState, introduction: str, summary: object
) -> str:
    match auxdata.linearizer.columns_constraint:
        case _core.ColumnsConstraints.Complect:
            return _complect_render_summary( auxdata, introduction, summary )
        case _core.ColumnsConstraints.Exceed:
            return _exceed_render_summary( auxdata, introduction, summary )


def _complect_render_summary(
    auxdata: _core.CompositorState, introduction: str, summary: object
) -> str:
    configuration = auxdata.configuration
    columns_max = auxdata.linearizer.columns_max
    line_prefix_i = configuration.line_prefix_initial
    intro_ccount = __.count_columns_visual( introduction )
    prefix_ccount = _calculate_ccount_max(
        line_prefix_i, configuration.line_prefix_subsequent )
    remainder_ccount = (
        __.absent if __.is_absent( columns_max )
        else columns_max - prefix_ccount )
    lines_final: list[ str ] = [ ]
    lines = _linearize_omni( auxdata.linearizer, summary, remainder_ccount )
    match len( lines ):
        case 0: raise __.SummaryLinearizationFailure( )
        case 1:
            content = lines[ 0 ]
            incision_point = 0
            if not __.is_absent( columns_max ):
                incision_point = (
                        configuration.summary_incision_ratio * columns_max )
            isolate_introduction = incision_point <= intro_ccount
            if not isolate_introduction:
                candidate = f"{introduction} {content}"
                candidate_ccount = (
                        prefix_ccount + intro_ccount
                    +   __.count_columns_visual( content ) + 1 )
                if candidate_ccount <= columns_max:
                    lines_final.append( f"{line_prefix_i}{candidate}" )
                else:
                    _update_lines_collection(
                        configuration, lines_final, introduction, lines )
            else:
                _update_lines_collection(
                    configuration, lines_final, introduction, lines )
        case _:
            _update_lines_collection(
                configuration, lines_final, introduction, lines )
    return '\n'.join( lines_final )


def _exceed_render_summary(
    auxdata: _core.CompositorState, introduction: str, summary: object
) -> str:
    configuration = auxdata.configuration
    line_prefix_i = configuration.line_prefix_initial
    lines_final: list[ str ] = [ ]
    lines = _linearize_omni( auxdata.linearizer, summary )
    match len( lines ):
        case 0: raise __.SummaryLinearizationFailure( )
        case 1:
            content = lines[ 0 ]
            lines_final.append( f"{line_prefix_i}{introduction} {content}" )
        case _:
            _update_lines_collection(
                configuration, lines_final, introduction, lines )
    return '\n'.join( lines_final )


def _update_lines_collection(
    configuration: _core.CompositorConfiguration,
    collector: list[ str ],
    line_initial: str,
    lines_subsequent: __.typx.Optional[ tuple[ str, ... ] ] = None,
) -> None:
    line_prefix_i = configuration.line_prefix_initial
    line_prefix_s = configuration.line_prefix_subsequent
    if line_prefix_s is None:
        line_prefix_s = ' ' * __.count_columns_visual( line_prefix_i )
    collector.append( f"{line_prefix_i}{line_initial}" )
    if lines_subsequent:
        collector.extend(
            f"{line_prefix_s}{line}" for line in lines_subsequent )
