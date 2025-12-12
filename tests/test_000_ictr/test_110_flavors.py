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


''' Tests for flavors and specifications. '''


import pytest

from ictr import flavors as _flavors


class Test_000_FlavorSpecification:
    ''' FlavorSpecification functionality. '''

    def test_000_creation( self ):
        ''' FlavorSpecification creation works as expected. '''
        spec = _flavors.StandardFlavorSpecification(
            color = 'blue', emoji = 'X', label = 'TEST' )
        assert spec.color == 'blue'
        assert spec.emoji == 'X'
        assert spec.label == 'TEST'
        assert spec.stack is False

    def test_010_standard_flavors_keys( self ):
        ''' Standard flavors keys are present. '''
        specs = _flavors.flavor_specifications_standard
        assert 'note' in specs
        assert 'error' in specs
        assert 'future' in specs


class Test_100_FlavorSpecification_Components:
    ''' FlavorSpecification component validation. '''

    def test_100_all_optional_fields( self ):
        ''' FlavorSpecification with all optional fields. '''
        spec = _flavors.StandardFlavorSpecification(
            color = 'red', emoji = '!', label = 'TEST', stack = True )
        assert spec.stack is True

    def test_110_immutability( self ):
        ''' FlavorSpecification is immutable. '''
        spec = _flavors.StandardFlavorSpecification(
            color = 'blue', emoji = 'X', label = 'TEST' )
        with pytest.raises( AttributeError ):
            spec.label = 'NEW'

    def test_120_default_values( self ):
        ''' FlavorSpecification default values are correct. '''
        # Only stack has default value
        spec = _flavors.StandardFlavorSpecification(
            color = 'blue', emoji = 'X', label = 'TEST' )
        assert spec.stack is False


class Test_200_Standard_Flavors:
    ''' Standard flavors validation. '''

    def test_200_all_standard_flavors_present( self ):
        ''' All standard flavors are present. '''
        specs = _flavors.flavor_specifications_standard
        expected = {
            'note', 'monition', 'error', 'errorx', 'abort', 'abortx',
            'future', 'success', 'advice'
        }
        assert expected.issubset( specs.keys() )

    def test_210_single_letter_aliases( self ):
        ''' Single letter aliases are present. '''
        aliases = _flavors.flavor_aliases_standard
        expected = { 'n', 'm', 'e', 'a', 'f', 's', 'v' }
        assert expected.issubset( aliases.keys() )
        assert aliases['n'] == 'note'
        assert aliases['e'] == 'error'

    def test_220_exception_capturing_flavors( self ):
        ''' Exception capturing flavors have stack=True. '''
        specs = _flavors.flavor_specifications_standard
        assert specs['errorx'].stack is True
        assert specs['abortx'].stack is True
        assert specs['error'].stack is False
        assert specs['abort'].stack is False
