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

    compositor_factory: __.typx.Annotated[
        __.typx.Optional[ _texts.CompositorFactory ],
        __.typx.Doc(
            ''' Factory which produces compositor callable.

                Takes address and flavor as arguments. Returns compositor.

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None


FlavorsRegistry: __.typx.TypeAlias = (
    __.immut.Dictionary[ _flavors.Flavor, FlavorConfiguration ] )
FlavorsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ _flavors.Flavor, FlavorConfiguration ] )


def produce_flavors_default( ) -> FlavorsRegistry:
    ''' Produces registry of all standard flavors without customization. '''
    flavors: FlavorsRegistryLiberal = { }
    for name, spec in _flavors.flavor_specifications_standard.items( ):
        tfactory = _texts.produce_compositor_factory_default(
            introducer = f"{spec.label}| ", trace_exceptions = spec.stack )
        flavors[ name ] = FlavorConfiguration(
            compositor_factory = tfactory )
    for alias, name in _flavors.flavor_aliases_standard.items( ):
        flavors[ alias ] = flavors[ name ]
    for level in range( 10 ):
        indent_i = '  ' * level
        indent_s = '  ' * ( level + 1 )
        tfactory = _texts.produce_compositor_factory_default(
            introducer = f"TRACE{level}| ",
            line_prefix_initial = indent_i,
            line_prefix_subsequent = indent_s )
        flavors[ level ] = FlavorConfiguration(
            compositor_factory = tfactory )
    return __.immut.Dictionary( flavors )


class AddressConfiguration( __.immut.DataclassObject ):
    ''' Per-address configuration. '''

    compositor_factory: __.typx.Annotated[
        __.typx.Optional[ _texts.CompositorFactory ],
        __.typx.Doc(
            ''' Factory which produces compositor callable.

                Takes address and flavor as arguments. Returns compositor.

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None
    flavors: __.typx.Annotated[
        FlavorsRegistry,
        __.typx.Doc(
            ''' Registry of flavor identifiers to configurations. ''' ),
    ] = __.dcls.field( default_factory = FlavorsRegistry )


class DispatcherConfiguration( __.immut.DataclassObject ):
    ''' Per-dispatcher configuration. '''

    compositor_factory: __.typx.Annotated[
        _texts.CompositorFactory,
        __.typx.Doc(
            ''' Factory which produces compositor callable.

                Takes address and flavor as arguments. Returns compositor.
            ''' ),
    ] = _texts.produce_compositor_factory_default( )
    flavors: __.typx.Annotated[
        FlavorsRegistry,
        __.typx.Doc(
            ''' Registry of flavor identifiers to configurations. ''' ),
    ] = __.dcls.field( default_factory = produce_flavors_default )
