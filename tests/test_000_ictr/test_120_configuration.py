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


''' Tests for configuration types. '''


import pytest

from ictr import configuration as _cfg


class Test_000_Basic_Functionality:
    ''' Basic functionality tests. '''

    def test_000_address_configuration_minimal( self ):
        ''' AddressConfiguration with minimal settings. '''
        import collections.abc as cabc
        config = _cfg.AddressConfiguration()
        assert config.compositor_factory is None
        assert isinstance( config.flavors, cabc.Mapping )

    def test_010_flavor_configuration_defaults( self ):
        ''' FlavorConfiguration with defaults. '''
        config = _cfg.FlavorConfiguration()
        assert config.compositor_factory is None

    def test_020_produce_flavors_default( self ):
        ''' produce_flavors_default returns registry with standard flavors. '''
        flavors = _cfg.produce_flavors_default()
        assert 'note' in flavors
        assert 'error' in flavors
        assert 0 in flavors  # Trace levels
        assert flavors['note'].compositor_factory is not None


class Test_100_AddressConfiguration:
    ''' AddressConfiguration validation. '''

    def test_100_all_fields( self ):
        ''' AddressConfiguration with all fields specified. '''
        flavors = _cfg.FlavorsRegistry( {
            'note': _cfg.FlavorConfiguration() } )
        # Mock factory
        def factory( addr, flv ): return lambda x: 'test'
        
        config = _cfg.AddressConfiguration(
            compositor_factory = factory,
            flavors = flavors
        )
        assert config.compositor_factory is factory
        assert config.flavors is flavors

    def test_110_immutability( self ):
        ''' AddressConfiguration is immutable. '''
        config = _cfg.AddressConfiguration()
        with pytest.raises( AttributeError ):
            config.compositor_factory = None


class Test_200_FlavorConfiguration:
    ''' FlavorConfiguration validation. '''

    def test_200_custom_fields( self ):
        ''' FlavorConfiguration with custom fields. '''
        def factory( addr, flv ): return lambda x: 'test'
        config = _cfg.FlavorConfiguration(
            compositor_factory = factory
        )
        assert config.compositor_factory is factory

    def test_210_immutability( self ):
        ''' FlavorConfiguration is immutable. '''
        config = _cfg.FlavorConfiguration()
        with pytest.raises( AttributeError ):
            config.compositor_factory = None


class Test_300_DispatcherConfiguration:
    ''' DispatcherConfiguration validation. '''

    def test_300_defaults( self ):
        ''' DispatcherConfiguration defaults. '''
        config = _cfg.DispatcherConfiguration()
        assert config.compositor_factory is not None
        assert 'note' in config.flavors
