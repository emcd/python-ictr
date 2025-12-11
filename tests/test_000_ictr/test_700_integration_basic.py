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


''' Integration tests. '''


import io

from ictr import configuration as _cfg
from ictr import dispatchers as _dispatchers
from ictr import printers as _printers


class Test_700_EndToEnd:
    ''' End-to-end integration. '''

    def test_000_simple_flow( self ):
        ''' Simple flow from install to output. '''
        capture = io.StringIO()
        printer_factory = _printers.produce_printer_factory_default( capture )
        
        _dispatchers.install(
            alias = 'ictr_test_700',
            printer_factories = [printer_factory]
        )
        
        # Use installed dispatcher
        import builtins
        dispatcher = getattr( builtins, 'ictr_test_700' )
        
        dispatcher( 'note' )( 'Hello World' )
        
        output = capture.getvalue()
        assert 'Hello World' in output
        assert 'note' in output or 'NOTE' in output

        # Cleanup
        delattr( builtins, 'ictr_test_700' )
    def test_100_hierarchy_flavors( self ):
        ''' Hierarchy inheritance for active flavors. '''
        # Root: note
        # Pkg: +error
        # Mod: +monition

        ictr = _dispatchers.Dispatcher(
            active_flavors = {
                None: {'note'},
                'pkg': {'error'},
                'pkg.mod': {'monition'}
            }
        )

        # Pkg level should have note (from root) + error
        # But _calculate_effective_flavors implementation:
        # result = flavors.get(None)
        # loop ancestors: result |= flavors.get(ancestor)

        # Test root
        assert ictr( 'note', address='root' ).active
        assert not ictr( 'error', address='root' ).active

        # Test pkg
        assert ictr( 'note', address='pkg' ).active
        assert ictr( 'error', address='pkg' ).active
        assert not ictr( 'monition', address='pkg' ).active

        # Test mod
        assert ictr( 'note', address='pkg.mod' ).active
        assert ictr( 'error', address='pkg.mod' ).active
        assert ictr( 'monition', address='pkg.mod' ).active

    def test_200_hierarchy_trace_levels( self ):
        ''' Hierarchy inheritance for trace levels. '''
        # Root: 0
        # Pkg: 2
        # Mod: 5

        ictr = _dispatchers.Dispatcher(
            trace_levels = {
                None: 0,
                'pkg': 2,
                'pkg.mod': 5
            }
        )

        # Root
        assert ictr( 0, address='root' ).active
        assert not ictr( 1, address='root' ).active

        # Pkg (overrides root?)
        # _calculate_effective_trace_level:
        # result = levels.get(None)
        # loop ancestors: if addr in levels: result = levels[addr]
        # So yes, it overrides.

        assert ictr( 2, address='pkg' ).active
        assert not ictr( 3, address='pkg' ).active

        # Mod
        assert ictr( 5, address='pkg.mod' ).active
        assert not ictr( 6, address='pkg.mod' ).active

    def test_300_hierarchy_configuration( self ):
        ''' Configuration merging hierarchy. '''
        # Root: factory1
        # Pkg: factory2
        
        def factory1(addr, flv): return lambda x: '1'
        def factory2(addr, flv): return lambda x: '2'
        
        # We define a custom flavor in root config to ensure it exists
        # but has no factory
        root_cfg = _cfg.DispatcherConfiguration(
            compositor_factory = factory1,
            flavors = { 'custom': _cfg.FlavorConfiguration() }
        )
        pkg_cfg = _cfg.AddressConfiguration(
            compositor_factory = factory2
        )
        
        ictr = _dispatchers.produce_dispatcher(
            generalcfg = root_cfg,
            addresscfgs = { 'pkg': pkg_cfg }
        )
        
        # Check behavior via private method (or by observing side effect
        # if possible)
        config = _dispatchers._produce_ic_configuration(
            ictr, 'pkg.mod', 'custom' )
        assert config['compositor_factory'] is factory2
        
        config_root = _dispatchers._produce_ic_configuration(
            ictr, 'other', 'custom' )
        assert config_root['compositor_factory'] is factory1
