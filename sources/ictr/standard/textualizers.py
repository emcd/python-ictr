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


''' Standard textualizer and renderers. '''


from . import __
from . import core as _core

from .introducers import Introduction as _Introduction
from .linearizers import linearize_omni as _linearize_omni


class Textualizer( __.Textualizer ):
    ''' Standard textualizer. '''

    configuration: __.typx.Annotated[
        _core.TextualizerConfiguration,
        __.ddoc.Doc( ''' Default behaviors and format for text. ''' ),
    ] = __.dcls.field( default_factory = _core.TextualizerConfiguration )
    introducer: __.typx.Annotated[
        __.IntroducerUnion,
        __.ddoc.Doc(
            ''' String or factory which produces introduction string.

                Factory takes control object and record as arguments.
                Returns introduction string.
            ''' ),
    ] = 'ictr| '

    def __call__(
        self, control: __.TextualizerControl, record: __.Record
    ) -> str:
        configuration = self.configuration
        auxdata = _core.TextualizerState(
            configuration = configuration, control = control )
        content = record.content
        introduction = _render_introduction( auxdata, self.introducer, record )
        if isinstance( content, __.MessageContent ):
            summary = _render_summary( auxdata, introduction, content.summary )
            details = tuple(
                _render_detail( auxdata, detail )
                for detail in content.details )
            return configuration.details_separator.join( (
                summary, *details ) )
        raise NotImplementedError  # TODO: Proper error.


def _render_introduction(
    auxdata: _core.TextualizerState,
    introducer: __.IntroducerUnion,
    record: __.Record,
) -> _Introduction:
    text = (
        introducer if isinstance( introducer, str )
        else introducer( auxdata.control, record ) )
    columns_count = __.count_columns_visual( text )
    return _Introduction( text = text, columns_count = columns_count )


def _render_detail(
    auxdata: _core.TextualizerState, detail: __.MessageDetail
) -> str:
    configuration = auxdata.configuration
    detail_prefix_i = configuration.detail_prefix_initial
    detail_prefix_i_ccount = __.count_columns_visual( detail_prefix_i )
    detail_prefix_s = configuration.detail_prefix_subsequent
    if detail_prefix_s is None:
        detail_prefix_s = ' ' * detail_prefix_i_ccount
    line_prefix = configuration.line_prefix
    prefix_ccount = (
        __.count_columns_visual( line_prefix ) + detail_prefix_i_ccount )
    match auxdata.columns_constraint:
        case _core.ColumnsConstraints.Complect:
            remainder_ccount = (
                __.absent if __.is_absent( auxdata.columns_max )
                else auxdata.columns_max - prefix_ccount )
        case _core.ColumnsConstraints.Exceed:
            remainder_ccount = __.absent
    lines = iter( _linearize_omni( auxdata, detail, remainder_ccount ) )
    line_i = next( lines )
    lines_final = [ f"{line_prefix}{detail_prefix_i}{line_i}" ]
    lines_final.extend(
        f"{line_prefix}{detail_prefix_s}{line}" for line in lines )
    return '\n'.join( lines_final )


def _render_summary(
    auxdata: _core.TextualizerState,
    introduction: _Introduction,
    summary: __.MessageSummary,
) -> str:
    match auxdata.columns_constraint:
        case _core.ColumnsConstraints.Complect:
            return _complect_render_summary( auxdata, introduction, summary )
        case _core.ColumnsConstraints.Exceed:
            return _exceed_render_summary( auxdata, introduction, summary )


def _complect_render_summary(
    auxdata: _core.TextualizerState,
    introduction: _Introduction,
    summary: __.MessageSummary,
) -> str:
    # TODO: Consider continuation prefix.
    configuration = auxdata.configuration
    line_prefix = configuration.line_prefix
    prefix_ccount = __.count_columns_visual( line_prefix )
    remainder_ccount = (
        __.absent if __.is_absent( auxdata.columns_max )
        else auxdata.columns_max - prefix_ccount )
    lines_final: list[ str ] = [ ]
    lines = _linearize_omni( auxdata, summary, remainder_ccount )
    match len( lines ):
        case 0: raise RuntimeError  # TODO: Appropriate error.
        case 1:
            content = lines[ 0 ]
            incision_point = 0
            if not __.is_absent( auxdata.columns_max ):
                incision_point = (
                        configuration.summary_incision_ratio
                    *   auxdata.columns_max )
            isolate_introduction = (
                incision_point <= introduction.columns_count )
            if not isolate_introduction:
                candidate = f"{introduction.text} {content}"
                candidate_ccount = (
                        prefix_ccount + introduction.columns_count
                    +   __.count_columns_visual( content ) + 1 )
                if candidate_ccount <= auxdata.columns_max:
                    lines_final.append( candidate )
                else:
                    lines_final.extend( ( introduction.text, *lines ) )
            else:
                lines_final.extend( ( introduction.text, *lines ) )
        case _:
            lines_final.extend( ( introduction.text, *lines ) )
    return '\n'.join( f"{line_prefix}{line}" for line in lines_final )


def _exceed_render_summary(
    auxdata: _core.TextualizerState,
    introduction: _Introduction,
    summary: __.MessageSummary,
) -> str:
    # TODO: Consider continuation prefix.
    configuration = auxdata.configuration
    line_prefix = configuration.line_prefix
    lines_final: list[ str ] = [ ]
    lines = _linearize_omni( auxdata, summary )
    match len( lines ):
        case 0: raise RuntimeError  # TODO: Appropriate error.
        case 1:
            content = lines[ 0 ]
            lines_final.append( f"{introduction.text} {content}" )
        case _:
            lines_final.extend( ( introduction.text, *lines ) )
    return '\n'.join( f"{line_prefix}{line}" for line in lines_final )
