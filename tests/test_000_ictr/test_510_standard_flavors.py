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


''' Tests for standard flavors production. '''


from ictr.standard import flavors as _flavors


class Test_000_Produce_Flavors:
    ''' produce_flavors validation. '''

    def test_000_returns_dictionary( self ):
        ''' produce_flavors returns a dictionary-like object. '''
        flavors = _flavors.produce_flavors()
        
        import collections.abc as cabc
        assert isinstance( flavors, cabc.Mapping )

    def test_010_standard_flavors_included( self ):
        ''' Standard flavors are included. '''
        flavors = _flavors.produce_flavors()
        assert 'note' in flavors
        assert 'error' in flavors
        assert 'future' in flavors

    def test_300_aliases_included( self ):
        ''' Aliases are included and map to same config as target. '''
        flavors = _flavors.produce_flavors()
        assert 'n' in flavors
        assert flavors['n'] is flavors['note']

    def test_340_trace_levels_included( self ):
        ''' Trace levels are included. '''
        flavors = _flavors.produce_flavors()
        assert 0 in flavors
        assert 9 in flavors
