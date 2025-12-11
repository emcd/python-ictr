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


''' Standard flavors, flavor aliases, etc.... '''


from . import __
from . import compositors as _compositors
from . import core as _core
from . import introducers as _intros


def produce_flavors(
    introducercfg: _core.IntroducerConfiguration = (
        _core.INTRODUCER_CONFIGURATION_DEFAULT ),
    compositorcfg: _core.CompositorConfiguration = (
        _core.COMPOSITOR_CONFIGURATION_DEFAULT ),
) -> __.FlavorsRegistry:
    ''' Produces registry of all standard flavors.

        Customization of introducers and compositors is possible.
    '''
    flavors: __.FlavorsRegistryLiberal = { }
    introducer = _intros.Introducer( configuration = introducercfg )
    compositor = _compositors.Compositor(
        configuration = compositorcfg, introducer = introducer )
    for name, spec in __.flavor_specifications_standard.items( ):
        ccfg = compositorcfg
        if spec.stack:
            lcfg = ccfg.linearizercfg
            ecfg = __.dcls.replace(
                lcfg.exceptionscfg,
                enable_discovery = True,
                enable_stacktraces = True )
            lcfg = __.dcls.replace( lcfg, exceptionscfg = ecfg )
            ccfg = __.dcls.replace( ccfg, linearizercfg = lcfg )
        compositor = _compositors.Compositor(
            configuration = ccfg, introducer = introducer )
        flavors[ name ] = __.FlavorConfiguration(
            compositor_factory = _produce_compositor_factory( compositor ) )
    for alias, name in __.flavor_aliases_standard.items( ):
        flavors[ alias ] = flavors[ name ]
    for level in range( 10 ):
        indent_i = '  ' * level
        indent_s = '  ' * ( level + 1 )
        ccfg = __.dcls.replace(
            compositorcfg,
            line_prefix_initial = indent_i,
            line_prefix_subsequent = indent_s )
        compositor = _compositors.Compositor(
            configuration = ccfg, introducer = introducer )
        flavors[ level ] = __.FlavorConfiguration(
            compositor_factory = _produce_compositor_factory( compositor ) )
    return __.immut.Dictionary( flavors )


def _produce_compositor_factory(
    compositor: _compositors.Compositor
) -> __.CompositorFactory:
    return lambda address, flavor: compositor
