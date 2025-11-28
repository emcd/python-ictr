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


''' Family of exceptions for package API. '''


from . import __


class Omniexception( __.immut.exceptions.Omniexception ):
    ''' Base for all exceptions raised by package API. '''


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


class ArgumentClassInvalidity( Omnierror, TypeError ):
    ''' Argument class is invalid. '''

    def __init__( self, name: str, classes: type | tuple[ type, ... ] ):
        if isinstance( classes, type ): classes = ( classes, )
        cnames = ' | '.join( map(
            lambda cls: f"{cls.__module__}.{cls.__qualname__}", classes ) )
        super( ).__init__(
            f"Argument {name!r} must be an instance of {cnames}." )


class AttributeNondisplacement( Omnierror, AttributeError ):
    ''' Cannot displace existing attribute. '''

    def __init__( self, object_: __.typx.Any, name: str ):
        super( ).__init__(
            f"Cannot displace attribute {name!r} on: {object_}" )


class ContentMisclassification( Omnierror, TypeError ):
    ''' Record content type is invalid or unsupported. '''

    def __init__( self, class_: type ):
        super( ).__init__(
            f"Unsupported record content type: {class_.__name__}" )


class FlavorInavailability( Omnierror, ValueError ):
    ''' Requested flavor is not available. '''

    def __init__( self, flavor: int | str ):
        super( ).__init__( f"Flavor {flavor!r} is not available." )


class FlavorMisclassification( Omnierror, TypeError ):
    ''' Flavor type is invalid for the requested operation. '''

    def __init__( self, flavor: int | str, expectation: str ):
        super( ).__init__(
            f"Expected {expectation} flavor, got {type( flavor ).__name__}: "
            f"{flavor!r}" )


class ModuleInferenceFailure( Omnierror, RuntimeError ):
    ''' Failure to infer invoking module from call stack. '''

    def __init__( self ):
        super( ).__init__( "Could not infer invoking module from call stack." )


class SummaryLinearizationFailure( Omnierror, RuntimeError ):
    ''' Failure to linearize summary. '''

    def __init__( self ):
        super( ).__init__( "Summary linearization produced no lines." )
