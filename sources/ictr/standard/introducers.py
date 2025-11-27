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
        self, control: __.TextualizerControl, record: __.Record
    ) -> str:
        # TODO: Implement.
        return ''


class Introduction( __.immut.DataclassObject ):
    ''' Structure for introduction. '''

    text: str
    columns_count: int  # visible
