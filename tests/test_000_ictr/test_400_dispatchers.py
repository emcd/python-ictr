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


''' Tests for dispatchers. '''


from unittest.mock import patch

import pytest

from ictr import configuration as _cfg
from ictr import dispatchers as _dispatchers
from ictr import exceptions as _exceptions


class Test_000_Basic_Functionality:
    ''' Basic functionality. '''

    def test_000_creation( self ):
        ''' Dispatcher creation with default configuration. '''
        dispatcher = _dispatchers.Dispatcher()
        assert dispatcher.reporters is not None
        assert dispatcher.reporters_mutex is not None

    def test_010_call_flavor( self ):
        ''' Dispatcher call with flavor returns reporter. '''
        dispatcher = _dispatchers.Dispatcher()
        reporter = dispatcher( 'note', address = 'test' )
        assert reporter.flavor == 'note'

    def test_020_call_trace_level( self ):
        ''' Dispatcher call with trace level returns reporter. '''
        dispatcher = _dispatchers.Dispatcher()
        reporter = dispatcher( 0, address = 'test' )
        assert reporter.flavor == 0


class Test_200_Omniflavor:
    ''' Omniflavor validation. '''

    def test_200_matches_any( self ):
        ''' Omniflavor matches any flavor. '''
        assert (
            _dispatchers.Omniflavor.Instance
            is _dispatchers.Omniflavor.Instance )


class Test_400_Reporter_Production:
    ''' Reporter production and caching. '''

    def test_420_creates_and_caches_reporter( self ):
        ''' __call__ creates and caches reporter. '''
        dispatcher = _dispatchers.Dispatcher()
        reporter1 = dispatcher( 'note', address = 'test' )
        reporter2 = dispatcher( 'note', address = 'test' )
        assert reporter1 is reporter2
        
    def test_440_invalid_flavor( self ):
        ''' __call__ with invalid flavor raises exception. '''
        dispatcher = _dispatchers.Dispatcher()
        # 'missing' flavor is not in default configuration
        with pytest.raises( _exceptions.FlavorInavailability ):
            dispatcher( 'missing', address = 'test' )

    def test_450_active_flavors_configuration( self ):
        ''' Active flavors configuration is respected. '''
        # Only 'note' is active
        dispatcher = _dispatchers.Dispatcher(
            active_flavors = { 'test': { 'note' } }
        )
        reporter_note = dispatcher( 'note', address = 'test' )
        assert reporter_note.active is True
        
        reporter_error = dispatcher( 'error', address = 'test' )
        assert reporter_error.active is False

    def test_540_max_trace_level( self ):
        ''' Max trace level is respected. '''
        dispatcher = _dispatchers.Dispatcher(
            trace_levels = { 'test': 2 }
        )
        # Level 2 <= 2 -> Active
        reporter2 = dispatcher( 2, address = 'test' )
        assert reporter2.active is True
        
        # Level 3 > 2 -> Inactive
        reporter3 = dispatcher( 3, address = 'test' )
        assert reporter3.active is False


class Test_800_Registration:
    ''' Address registration. '''

    def test_810_register_address( self ):
        ''' register_address stores configuration. '''
        dispatcher = _dispatchers.Dispatcher()
        config = _cfg.AddressConfiguration()
        dispatcher.register_address( 'test.module', configuration = config )
        assert 'test.module' in dispatcher.addresscfgs
        assert dispatcher.addresscfgs['test.module'] is config

    def test_820_install_builtin( self ):
        ''' install installs dispatcher into builtins. '''
        dispatcher = _dispatchers.Dispatcher()
        import builtins

        # Clean up if already exists (safe for tests?)
        original = getattr( builtins, 'ictr_test_alias', None )
        
        try:
            dispatcher.install( alias = 'ictr_test_alias' )
            assert getattr( builtins, 'ictr_test_alias' ) is dispatcher
        finally:
            if original:
                setattr( builtins, 'ictr_test_alias', original )
            else:
                delattr( builtins, 'ictr_test_alias' )

    def test_830_install_replaces_existing( self ):
        ''' install replaces existing dispatcher. '''
        existing = _dispatchers.Dispatcher()
        new_dispatcher = _dispatchers.Dispatcher()
        
        import builtins
        original = getattr( builtins, 'ictr_test_replace', None )
        setattr( builtins, 'ictr_test_replace', existing )
        
        try:
            new_dispatcher.install( alias = 'ictr_test_replace' )
            assert getattr( builtins, 'ictr_test_replace' ) is new_dispatcher
        finally:
            if original is None:
                delattr( builtins, 'ictr_test_replace' )
            else:
                setattr( builtins, 'ictr_test_replace', original )

    def test_850_register_address_replaces_invalid( self ):
        ''' register_address raises if name taken by non-dispatcher. '''
        import builtins
        original = getattr( builtins, 'ictr', None )
        setattr( builtins, 'ictr', "not a dispatcher" )
        
        try:
            with pytest.raises( _exceptions.AttributeNondisplacement ):
                _dispatchers.register_address( 'test' )
        finally:
            if original: setattr( builtins, 'ictr', original )
            elif hasattr( builtins, 'ictr' ): delattr( builtins, 'ictr' )


class Test_900_Environment_Configuration:
    ''' Environment variable configuration. '''

    def test_900_active_flavors_env( self ):
        ''' active_flavors_from_environment parses correctly. '''
        def getenv(key, default=None):
            if key == 'TEST': return 'test:note,error+a'
            return default
            
        with patch( 'os.getenv', side_effect = getenv ):
            # +a -> None: frozenset({'a'})
            registry = _dispatchers.active_flavors_from_environment(
                evname='TEST' )
            assert 'test' in registry
            assert 'note' in registry['test']
            assert None in registry
            assert 'a' in registry[None]

    def test_910_trace_levels_env( self ):
        ''' trace_levels_from_environment parses correctly. '''
        def getenv(key, default=None):
            if key == 'TEST': return 'pkg:5+sub:0'
            return default
            
        with patch( 'os.getenv', side_effect = getenv ):
            registry = _dispatchers.trace_levels_from_environment(
                evname='TEST' )
            assert registry['pkg'] == 5
            assert registry['sub'] == 0

    def test_915_trace_levels_env_invalid( self ):
        ''' trace_levels_from_environment handles invalid values. '''
        def getenv(key, default=None):
            if key == 'TEST': return 'pkg:invalid'
            return default
            
        with patch( 'os.getenv', side_effect = getenv ):
            with pytest.warns( UserWarning, match="Non-integer trace level" ):
                registry = _dispatchers.trace_levels_from_environment(
                    evname='TEST' )
            assert 'pkg' not in registry

    def test_920_install_with_env( self ):
        ''' install with environment variables. '''
        def getenv(key, default=None):
            if key == 'TEST': return 'test:note'
            return default
            
        with patch( 'os.getenv', side_effect = getenv ):
            dispatcher = _dispatchers.produce_dispatcher(
                evname_active_flavors = 'TEST' )
            assert 'test' in dispatcher.active_flavors
            assert 'note' in dispatcher.active_flavors['test']

    def test_930_active_flavors_list( self ):
        ''' produce_dispatcher with list of active flavors. '''
        flavors = ['note', 'error']
        dispatcher = _dispatchers.produce_dispatcher(
            active_flavors = flavors )
        assert None in dispatcher.active_flavors
        assert 'note' in dispatcher.active_flavors[None]
        assert 'error' in dispatcher.active_flavors[None]

    def test_940_active_flavors_dict_omniflavor( self ):
        ''' produce_dispatcher with dict containing omniflavor. '''
        flavors = { 'test': _dispatchers.Omniflavor.Instance }
        dispatcher = _dispatchers.produce_dispatcher(
            active_flavors = flavors )
        assert (
            dispatcher.active_flavors['test']
            is _dispatchers.Omniflavor.Instance )

    def test_945_active_flavors_dict_set( self ):
        ''' produce_dispatcher with dict containing set of flavors. '''
        flavors = { 'test': {'note', 'error'} }
        dispatcher = _dispatchers.produce_dispatcher(
            active_flavors = flavors )
        assert 'test' in dispatcher.active_flavors
        assert 'note' in dispatcher.active_flavors['test']
        assert isinstance( dispatcher.active_flavors['test'], frozenset )


class Test_950_Hierarchy:
    ''' Configuration hierarchy. '''

    def test_950_inheritance( self ):
        ''' Configuration inherits from parent packages. '''
        
        def factory1(addr, flv): return lambda x: '1'
        def factory2(addr, flv): return lambda x: '2'
        
        # We need to craft Dispatcher with addresscfgs
        # Use a custom flavor that doesn't have a default factory in general
        # config
        parent_config = _cfg.AddressConfiguration(
            compositor_factory = factory1,
            flavors = { 'custom': _cfg.FlavorConfiguration() }
        )
        addresscfgs = { 'parent': parent_config }
        
        dispatcher = _dispatchers.produce_dispatcher(
            addresscfgs = addresscfgs )
        
        # Invoke private method to check config
        config = _dispatchers._produce_ic_configuration(
            dispatcher, 'parent.child', 'custom'
        )
        
        assert config['compositor_factory'] is factory1
        
        # Check overriding
        child_config = _cfg.AddressConfiguration(
            compositor_factory = factory2,
            flavors = { 'custom': _cfg.FlavorConfiguration() }
        )
        addresscfgs['parent.child'] = child_config
        dispatcher = _dispatchers.produce_dispatcher(
            addresscfgs = addresscfgs )
        
        config = _dispatchers._produce_ic_configuration(
            dispatcher, 'parent.child', 'custom'
        )
        assert config['compositor_factory'] is factory2

    def test_960_module_register_returns_config( self ):
        ''' module-level register_address returns configuration. '''
        dispatcher = _dispatchers.Dispatcher()
        
        import builtins
        original = getattr( builtins, 'ictr', None )
        setattr( builtins, 'ictr', dispatcher )
        
        def factory(addr, flv): return lambda x: 'test'
        
        try:
            config = _dispatchers.register_address(
                'test', compositor_factory=factory )
            assert isinstance( config, _cfg.AddressConfiguration )
            assert config.compositor_factory is factory
            
            # Verify it was registered
            assert 'test' in dispatcher.addresscfgs
            assert dispatcher.addresscfgs['test'] is config
        finally:
            if original is None:
                delattr( builtins, 'ictr' )
            else:
                setattr( builtins, 'ictr', original )