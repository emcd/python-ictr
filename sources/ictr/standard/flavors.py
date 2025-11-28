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
from . import core as _core
from . import introducers as _intros
from . import textualizers as _texts


def produce_flavors(
    introducercfg: _core.IntroducerConfiguration = (
        _core.INTRODUCER_CONFIGURATION_DEFAULT ),
    textualizercfg: _core.TextualizerConfiguration = (
        _core.TEXTUALIZER_CONFIGURATION_DEFAULT ),
) -> __.FlavorsRegistry:
    ''' Produces registry of all standard flavors.

        Customization of introducers and textualizers is possible.
    '''
    flavors: __.FlavorsRegistryLiberal = { }
    introducer = _intros.Introducer( configuration = introducercfg )
    textualizer = _texts.Textualizer(
        configuration = textualizercfg, introducer = introducer )
    for name, spec in __.flavor_specifications_standard.items( ):
        tcfg = textualizercfg
        if spec.stack:
            tcfg = __.dcls.replace( textualizercfg, include_exception = True )
        textualizer = _texts.Textualizer(
            configuration = tcfg, introducer = introducer )
        flavors[ name ] = __.FlavorConfiguration(
            textualizer_factory = _produce_textualizer_factory( textualizer ) )
    for alias, name in __.flavor_aliases_standard.items( ):
        flavors[ alias ] = flavors[ name ]
    for level in range( 10 ):
        indent_i = '  ' * level
        indent_s = '  ' * ( level + 1 )
        tcfg = __.dcls.replace(
            textualizercfg,
            line_prefix_initial = indent_i,
            line_prefix_subsequent = indent_s )
        textualizer = _texts.Textualizer(
            configuration = tcfg, introducer = introducer )
        flavors[ level ] = __.FlavorConfiguration(
            textualizer_factory = _produce_textualizer_factory( textualizer ) )
    return __.immut.Dictionary( flavors )


def _produce_textualizer_factory(
    textualizer: _texts.Textualizer
) -> __.TextualizerFactory:
    return lambda control, address, flavor: textualizer
