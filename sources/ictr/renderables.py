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


''' Protocols for renderable objects. '''


from . import __


@__.typx.runtime_checkable
class Renderable(
    __.immut.Protocol, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Objects which can be rendered into a dictionary. '''

    def render_as_dictionary( self ) -> dict[ str, __.typx.Any ]:
        ''' Returns dictionary suitable for JSON/TOML serialization. '''
        return render_as_dictionary( self )


@__.typx.runtime_checkable
class RenderableDataclass(
    __.immut.DataclassProtocol, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Dataclass objects which can be rendered into a dictionary. '''

    def render_as_dictionary( self ) -> dict[ str, __.typx.Any ]:
        ''' Returns dictionary suitable for JSON/TOML serialization. '''
        return render_as_dictionary( self )


def render_as_dictionary( entity: object ) -> dict[ str, __.typx.Any ]:
    ''' Returns dictionary suitable for JSON/TOML serialization. '''
    if __.dcls.is_dataclass( entity ) and not isinstance( entity, type ):
        result: dict[ str, __.typx.Any ] = { }
        for field in __.dcls.fields( entity ):
            if field.name.startswith( '_' ): continue
            value = getattr( entity, field.name )
            result[ field.name ] = _serialize_value( value )
        return result
    if hasattr( entity, '__dict__' ):
        result = { }
        for name, value in entity.__dict__.items( ):
            if name.startswith( '_' ): continue
            result[ name ] = _serialize_value( value )
        return result
    raise NotImplementedError  # TODO: More specific error class.


def _serialize_value( value: __.typx.Any ) -> __.typx.Any:
    ''' Recursively serializes a value for dictionary representation. '''
    if isinstance( value, ( str, int, float, bool, __.types.NoneType ) ):
        return value
    if isinstance( value, __.cabc.Sequence ):
        return [ _serialize_value( e ) for e in value ]  # pyright: ignore
    if isinstance( value, __.cabc.Mapping ):
        return {
            str( k ): _serialize_value( v )  # pyright: ignore
            for k, v in value.items( ) }  # pyright: ignore
    if isinstance( value, ( Renderable, RenderableDataclass ) ):
        return value.render_as_dictionary( )
    if __.dcls.is_dataclass( value ) and not isinstance( value, type ):
        return render_as_dictionary( value )
    return repr( value )
