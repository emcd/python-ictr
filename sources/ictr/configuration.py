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


''' Portions of configuration hierarchy. '''


from . import __
from . import flavors as _flavors
from . import textualizers as _texts


class FlavorConfiguration( __.immut.DataclassObject ):
    ''' Per-flavor configuration. '''

    textualizer_factory: __.typx.Annotated[
        __.typx.Optional[ _texts.TextualizerFactory ],
        __.typx.Doc(
            ''' Factory which produces formatter callable.

                Takes formatter control, module name, and flavor as arguments.
                Returns formatter to convert an argument to a string.

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None
    include_context: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc(
            ''' Include stack frame with output?

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None


def produce_default_flavors( ) -> __.immut.Dictionary[
    _flavors.Flavor, FlavorConfiguration
]:
    ''' Produces flavors for trace depths 0 through 9. '''
    return __.immut.Dictionary( {
        i: FlavorConfiguration(
            textualizer_factory = _produce_trace_textualizer_factory( i ) )
                for i in range( 10 ) } )


FlavorsRegistry: __.typx.TypeAlias = (
    __.immut.Dictionary[ _flavors.Flavor, FlavorConfiguration ] )
FlavorsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ _flavors.Flavor, FlavorConfiguration ] )


class ModuleConfiguration( __.immut.DataclassObject ):
    ''' Per-module or per-package configuration. '''

    flavors: __.typx.Annotated[
        FlavorsRegistry,
        __.typx.Doc(
            ''' Registry of flavor identifiers to configurations. ''' ),
    ] = __.dcls.field( default_factory = FlavorsRegistry )
    textualizer_factory: __.typx.Annotated[
        __.typx.Optional[ _texts.TextualizerFactory ],
        __.typx.Doc(
            ''' Factory which produces formatter callable.

                Takes formatter control, module name, and flavor as arguments.
                Returns formatter to convert an argument to a string.

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None
    include_context: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc(
            ''' Include stack frame with output?

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None


class DispatcherConfiguration( __.immut.DataclassObject ):
    ''' Per-dispatcher configuration. '''

    flavors: __.typx.Annotated[
        FlavorsRegistry,
        __.typx.Doc(
            ''' Registry of flavor identifiers to configurations. ''' ),
    ] = __.dcls.field( default_factory = produce_default_flavors )
    textualizer_factory: __.typx.Annotated[
        _texts.TextualizerFactory,
        __.typx.Doc(
            ''' Factory which produces formatter callable.

                Takes formatter control, module name, and flavor as arguments.
                Returns formatter to convert an argument to a string.
            ''' ),
    # TODO: Assign a factory which utilizes record fields.
    ] = lambda tcontrol, record: _texts.TextualizerDefault( )
    include_context: __.typx.Annotated[
        bool, __.typx.Doc( ''' Include stack frame with output? ''' )
    ] = False


def _produce_trace_textualizer_factory(
    level: int
) -> _texts.TextualizerFactory:
    return (
        lambda tcontrol, record:
        _texts.TextualizerDefault( introducer = f"TRACE{level}| " ) )
