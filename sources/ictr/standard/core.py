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
    summary_incision_ratio: __.typx.Annotated[
        float,
        __.ddoc.Doc(
            ''' Ratio of introduction width to full width at which to split.

                If ratio is met or exceeded, then introduction and summary are
                split onto consecutive lines.
            ''' ),
    ] = 0.3


class TextualizerState( __.immut.DataclassObject ):
    # TODO: Replace properties with attributes since DTO is short-lived
    #       and should provide consistent state throughout lifetime.
    ''' Data transfer object for simple textualizer state. '''

    configuration: TextualizerConfiguration
    control: __.TextualizerControl

    @property
    def columns_constraint( self ) -> ColumnsConstraints:
        ''' Effective columns constraint for lines. '''
        if __.is_absent( self.columns_max ): return ColumnsConstraints.Exceed
        return self.configuration.columns_constraint

    @property
    def columns_max( self ) -> __.Absential[ int ]:
        ''' Available line length (maximum columns) of target. '''
        columns_max = (
            self.control.columns_max or self.configuration.columns_max )
        if columns_max is None: return __.absent
        return columns_max
