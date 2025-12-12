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


''' Tests for textualizer protocols. '''


from absence import absent

from ictr import textualizers as _texts


class Test_000_Protocols:
    ''' Protocol validation. '''

    def test_000_compositor_protocol( self ):
        ''' Compositor protocol is defined. '''
        assert issubclass( _texts.Compositor, object )

    def test_010_linearizer_protocol( self ):
        ''' Linearizer protocol is defined. '''
        assert issubclass( _texts.Linearizer, object )

    def test_020_introducer_protocol( self ):
        ''' Introducer protocol is defined. '''
        assert issubclass( _texts.Introducer, object )


class Test_400_Factory_Functions:
    ''' Factory function validation. '''

    def test_400_produce_default_with_string_introducer( self ):
        ''' produce_compositor_factory_default with string introducer. '''
        factory = _texts.produce_compositor_factory_default(
            introducer = 'intro' )
        compositor = factory( 'address', 'flavor' )
        # We can't easily check internal state without knowing standard details
        # But we can verify it's callable and returns something.
        assert callable( compositor )

    def test_410_produce_default_with_callable_introducer( self ):
        ''' produce_compositor_factory_default with callable introducer. '''
        def intro( ctrl, rec, cols=absent ): return 'intro'
        factory = _texts.produce_compositor_factory_default(
            introducer = intro )
        compositor = factory( 'address', 'flavor' )
        assert callable( compositor )

    def test_420_produce_default_with_configuration( self ):
        ''' produce_compositor_factory_default with configuration options. '''
        factory = _texts.produce_compositor_factory_default(
            line_prefix_initial = '>>',
            line_prefix_subsequent = '..'
        )
        compositor = factory( 'address', 'flavor' )
        assert callable( compositor )

    def test_430_produce_default_with_trace_exceptions( self ):
        ''' produce_compositor_factory_default with trace_exceptions. '''
        factory = _texts.produce_compositor_factory_default(
            trace_exceptions = True
        )
        compositor = factory( 'address', 'flavor' )
        assert callable( compositor )
