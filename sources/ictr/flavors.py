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


''' Reporter flavors. '''


from . import __


Flavor: __.typx.TypeAlias = int | str


class StandardFlavorSpecification( __.immut.DataclassObject ):
    ''' Specification for standard flavor. '''

    color: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Name of introduction color. ''' ) ]
    emoji: __.typx.Annotated[ str, __.ddoc.Doc( ''' Introduction emoji. ''' ) ]
    label: __.typx.Annotated[ str, __.ddoc.Doc( ''' Introduction label. ''' ) ]
    stack: __.typx.Annotated[
        bool, __.ddoc.Doc( ''' Include stack trace? ''' )
    ] = False


flavor_aliases_standard: __.immut.Dictionary[
    str, str
] = __.immut.Dictionary( {
    'n': 'note', 'm': 'monition',
    'e': 'error', 'a': 'abort',
    'ex': 'errorx', 'ax': 'abortx',
    'f': 'future', 's': 'success',
    'v': 'advice',
} )

flavor_specifications_standard: __.immut.Dictionary[
    str, StandardFlavorSpecification
] = __.immut.Dictionary(
    note = StandardFlavorSpecification(
        color = 'blue',
        emoji = '\N{Information Source}\ufe0f',
        label = 'NOTE' ),
    monition = StandardFlavorSpecification(
        color = 'yellow',
        emoji = '\N{Warning Sign}\ufe0f',
        label = 'MONITION' ),
    error = StandardFlavorSpecification(
        color = 'red', emoji = '❌', label = 'ERROR' ),
    errorx = StandardFlavorSpecification(
        color = 'red', emoji = '❌', label = 'ERROR', stack = True ),
    abort = StandardFlavorSpecification(
        color = 'bright_red', emoji = '💥', label = 'ABORT' ),
    abortx = StandardFlavorSpecification(
        color = 'bright_red', emoji = '💥', label = 'ABORT', stack = True ),
    future = StandardFlavorSpecification(
        color = 'magenta', emoji = '🔮', label = 'FUTURE' ),
    success = StandardFlavorSpecification(
        color = 'green', emoji = '✅', label = 'SUCCESS' ),
    advice = StandardFlavorSpecification(
        color = 'cyan', emoji = '💡', label = 'ADVICE' ),
)
