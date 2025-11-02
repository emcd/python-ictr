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


''' Inspection of variables as function arguments. '''

# TODO: Implement if deeper inspection than f-string {name=} is needed.


# import executing as _executing


from . import __


class Inspection( __.immut.DataclassObject ):
    ''' Result of variable inspection. '''

    name: str
    value: __.typx.Any


Inspections: __.typx.TypeAlias = __.cabc.Sequence[ Inspection ]


def inspect_variables( *variables: __.typx.Any ) -> Inspections:
    ''' Returns values of variables with names and execution context. '''
    inspections: list[ Inspection ] = [ ]
    # TODO: Implement.
    return tuple( inspections )
