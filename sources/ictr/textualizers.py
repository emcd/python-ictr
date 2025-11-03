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
from . import flavors as _flavors
from . import printers as _printers
from . import records as _records


PrefixEmitter: __.typx.TypeAlias = (
    __.typx.Callable[ [ str, _flavors.Flavor ], str ] )
PrefixEmitterUnion: __.typx.TypeAlias = str | PrefixEmitter


class Textualizer( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Abstract base class for textualizers. '''

    @__.abc.abstractmethod
    def __call__(
        self, control: _printers.TextualizerControl, record: _records.Record
    ) -> str:
        ''' Renders a record as text. '''
        raise NotImplementedError


class TextualizerDefault( Textualizer ):
    ''' Simple textualizer. '''

    prefix_emitter: __.typx.Annotated[
        PrefixEmitterUnion,
        __.typx.Doc(
            ''' String or factory which produces output prefix string.

                Factory takes control object and record as arguments.
                Returns prefix string.
            ''' ),
    ] = 'ictr| '

    def __call__(
        self, control: _printers.TextualizerControl, record: _records.Record
    ) -> str:
        # TODO: Implement.
        return ''


TextualizerFactory: __.typx.TypeAlias = (
    __.typx.Callable[
        [ _printers.TextualizerControl, _records.Record ], Textualizer ] )
