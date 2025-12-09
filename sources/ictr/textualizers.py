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


''' Interfaces for compositors, introducers, et cetera. '''


from . import __
from . import flavors as _flavors
from . import printers as _printers
from . import records as _records


class Compositor( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Abstract base class for compositors. '''

    @__.abc.abstractmethod
    def __call__(
        self,
        control: _printers.TextualizationControl,
        record: _records.Record,
    ) -> str:
        ''' Renders record as text. '''
        raise NotImplementedError


CompositorFactory: __.typx.TypeAlias = (
    __.typx.Callable[ [ str, _flavors.Flavor ], Compositor ] )


class Introducer( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Abstract base class for introducers. '''

    @__.abc.abstractmethod
    def __call__(
        self,
        control: _printers.TextualizationControl,
        record: _records.Record,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> str:
        ''' Renders record as text label. '''
        raise NotImplementedError


IntroducerUnion: __.typx.TypeAlias = str | Introducer


class Linearizer( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Abstract base class for linearizers. '''

    @__.abc.abstractmethod
    def __call__(
        self,
        control: _printers.TextualizationControl,
        entity: object,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> tuple[ str, ... ]:
        ''' Renders object as lines of text. '''
        raise NotImplementedError


def produce_compositor_factory_default(
    introducer: __.Absential[ IntroducerUnion ] = __.absent,
    line_prefix_initial: str = '',
    line_prefix_subsequent: str = '  ',
    trace_exceptions: bool = False,
) -> CompositorFactory:
    ''' Produces default compositor factory. '''
    def produce_compositor(
        address: str, flavor: _flavors.Flavor
    ) -> Compositor:
        from .standard import (
            Compositor,
            CompositorConfiguration,
            ExceptionsConfiguration,
            LinearizerConfiguration,
        )
        ecfg = ExceptionsConfiguration(
            enable_discovery = trace_exceptions,
            enable_stacktraces = trace_exceptions )
        lcfg = LinearizerConfiguration( exceptionscfg = ecfg )
        ccfg = CompositorConfiguration(
            line_prefix_initial = line_prefix_initial,
            line_prefix_subsequent = line_prefix_subsequent,
            linearizercfg = lcfg )
        if __.is_absent( introducer ):
            return Compositor( configuration = ccfg )
        return Compositor( configuration = ccfg, introducer = introducer )

    return produce_compositor
