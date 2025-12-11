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


''' Tests for package exceptions. '''


from ictr import exceptions as _exceptions


class Test_000_Base_Hierarchy:
    ''' Base exception hierarchy. '''

    def test_000_base_classes( self ):
        ''' Base exceptions exist. '''
        assert issubclass( _exceptions.Omnierror, _exceptions.Omniexception )
        assert issubclass( _exceptions.Omnierror, Exception )

    def test_010_nomenclature( self ):
        ''' Exception names follow convention. '''
        # Simple check for some known exceptions
        name = _exceptions.ArgumentClassInvalidity.__name__
        assert name.endswith( 'Invalidity' )
        # Others might not end with Invalidity but should follow patterns



class Test_100_Exception_Instantiation:
    ''' Exception instantiation and messages. '''

    def test_100_argument_class_invalidity( self ):
        ''' ArgumentClassInvalidity message. '''
        exc = _exceptions.ArgumentClassInvalidity( 'arg', ( int, str ) )
        assert "Argument 'arg' must be an instance of" in str( exc )
        assert "int" in str( exc )
        assert "str" in str( exc )

    def test_110_attribute_nondisplacement( self ):
        ''' AttributeNondisplacement message. '''
        exc = _exceptions.AttributeNondisplacement( 'obj', 'attr' )
        assert "Cannot displace attribute 'attr' on: obj" in str( exc )

    def test_120_content_misclassification( self ):
        ''' ContentMisclassification message. '''
        exc = _exceptions.ContentMisclassification( int )
        assert "Unsupported record content type: int" in str( exc )

    def test_130_flavor_inavailability( self ):
        ''' FlavorInavailability message. '''
        exc = _exceptions.FlavorInavailability( 'missing' )
        assert "Flavor 'missing' is not available." in str( exc )

    def test_140_flavor_misclassification( self ):
        ''' FlavorMisclassification message. '''
        exc = _exceptions.FlavorMisclassification( 'flavor', 'expectation' )
        assert "Expected expectation flavor, got str: 'flavor'" in str( exc )

    def test_150_module_inference_failure( self ):
        ''' ModuleInferenceFailure message. '''
        exc = _exceptions.ModuleInferenceFailure()
        assert "Could not infer invoking module" in str( exc )

    def test_160_summary_linearization_failure( self ):
        ''' SummaryLinearizationFailure message. '''
        exc = _exceptions.SummaryLinearizationFailure()
        assert "Summary linearization produced no lines" in str( exc )


class Test_200_Exception_Behavior:
    ''' Exception behavior. '''

    def test_200_inheritance( self ):
        ''' Exceptions inherit from appropriate base classes. '''
        assert issubclass( _exceptions.ArgumentClassInvalidity, TypeError )
        assert issubclass(
            _exceptions.AttributeNondisplacement, AttributeError )
        assert issubclass( _exceptions.ContentMisclassification, TypeError )
        assert issubclass( _exceptions.FlavorInavailability, ValueError )
        assert issubclass( _exceptions.FlavorMisclassification, TypeError )
        assert issubclass( _exceptions.ModuleInferenceFailure, RuntimeError )
        assert issubclass(
            _exceptions.SummaryLinearizationFailure, RuntimeError )
