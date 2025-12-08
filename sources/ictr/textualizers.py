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


''' Interfaces for textualizers, introducers, et cetera. '''


from . import __
from . import flavors as _flavors
from . import printers as _printers
from . import records as _records


class Introducer( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Abstract base class for introducers. '''

    @__.abc.abstractmethod
    def __call__(
        self,
        control: _printers.TextualizerControl,
        record: _records.Record,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> str:
        ''' Renders record as text label. '''
        raise NotImplementedError


IntroducerUnion: __.typx.TypeAlias = str | Introducer


class Textualizer( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Abstract base class for textualizers. '''

    @__.abc.abstractmethod
    def __call__(
        self, control: _printers.TextualizerControl, record: _records.Record
    ) -> str:
        ''' Renders record as text. '''
        raise NotImplementedError


TextualizerFactory: __.typx.TypeAlias = (
    __.typx.Callable[
        [ _printers.TextualizerControl, str, _flavors.Flavor ], Textualizer ] )


def produce_textualizer_factory_default(
    introducer: __.Absential[ IntroducerUnion ] = __.absent,
    line_prefix_initial: str = '',
    line_prefix_subsequent: str = '  ',
    trace_exceptions: bool = False,
) -> TextualizerFactory:
    ''' Produces default textualizer factory. '''
    def produce_textualizer(
        control: _printers.TextualizerControl,
        addresss: str,
        flavor: _flavors.Flavor,
    ) -> Textualizer:
        from .standard import (
            ExceptionsConfiguration,
            LinearizerConfiguration,
            Textualizer,
            TextualizerConfiguration,
        )
        ecfg = ExceptionsConfiguration(
            enable_discovery = trace_exceptions,
            enable_stacktraces = trace_exceptions )
        lcfg = LinearizerConfiguration( exceptionscfg = ecfg )
        tcfg = TextualizerConfiguration(
            line_prefix_initial = line_prefix_initial,
            line_prefix_subsequent = line_prefix_subsequent,
            linearizercfg = lcfg )
        if __.is_absent( introducer ):
            return Textualizer( configuration = tcfg )
        return Textualizer( configuration = tcfg, introducer = introducer )

    return produce_textualizer
