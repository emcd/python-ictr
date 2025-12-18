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


import json as _json

from . import __


@__.typx.runtime_checkable
class DictionaryRenderable(
    __.immut.Protocol, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Objects which can be rendered into a dictionary. '''

    def render_as_dictionary( self ) -> dict[ str, __.typx.Any ]:
        ''' Returns dictionary suitable for JSON/TOML serialization. '''
        return render_as_dictionary( self )


@__.typx.runtime_checkable
class DictionaryRenderableDataclass(
    __.immut.DataclassProtocol, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Dataclass objects which can be rendered into a dictionary. '''

    def render_as_dictionary( self ) -> dict[ str, __.typx.Any ]:
        ''' Returns dictionary suitable for JSON/TOML serialization. '''
        return render_as_dictionary( self )


@__.typx.runtime_checkable
class JsonRenderable(
    DictionaryRenderable, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Objects which can be rendered as JSON. '''

    def render_as_json(
        self, /, *, compact: bool = False, indent: int = 2
    ) -> str:
        ''' Returns JSON string representation. '''
        dictionary = self.render_as_dictionary( )
        return _dictionary_to_json(
            dictionary, compact = compact, indent = indent )


@__.typx.runtime_checkable
class JsonRenderableDataclass(
    DictionaryRenderableDataclass, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Dataclass objects which can be rendered as JSON. '''

    def render_as_json(
        self, /, *, compact: bool = False, indent: int = 2
    ) -> str:
        ''' Returns JSON string representation. '''
        dictionary = self.render_as_dictionary( )
        return _dictionary_to_json(
            dictionary, compact = compact, indent = indent )


@__.typx.runtime_checkable
class MarkdownRenderable(
    DictionaryRenderable, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Objects which can be rendered as Markdown. '''

    def render_as_markdown(
        self, /, *,
        colorize: bool = False,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> str:
        ''' Returns Markdown string representation. '''
        dictionary = self.render_as_dictionary( )
        return _dictionary_to_markdown(
            dictionary, colorize = colorize, columns_max = columns_max )


@__.typx.runtime_checkable
class MarkdownRenderableDataclass(
    DictionaryRenderableDataclass, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Dataclass objects which can be rendered as Markdown. '''

    def render_as_markdown(
        self, /, *,
        colorize: bool = False,
        columns_max: __.Absential[ int ] = __.absent,
    ) -> str:
        ''' Returns Markdown string representation. '''
        dictionary = self.render_as_dictionary( )
        return _dictionary_to_markdown(
            dictionary, colorize = colorize, columns_max = columns_max )


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


def _dictionary_to_json(
    dictionary: dict[ str, __.typx.Any ], /, *,
    compact: bool = False, indent: int = 2,
) -> str:
    ''' Returns JSON string representation. '''
    if compact:
        return _json.dumps(
            dictionary, ensure_ascii = False, separators = ( ',', ':' ) )
    return _json.dumps( dictionary, ensure_ascii = False, indent = indent )


def _dictionary_to_markdown(
    dictionary: dict[ str, __.typx.Any ], /, *,
    colorize: bool = False,
    columns_max: __.Absential[ int ] = __.absent,
) -> str:
    ''' Returns Markdown string representation. '''
    # TODO: Default implementation.
    raise NotImplementedError


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
    if isinstance(
        value, ( DictionaryRenderable, DictionaryRenderableDataclass )
    ): return value.render_as_dictionary( )
    if __.dcls.is_dataclass( value ) and not isinstance( value, type ):
        return render_as_dictionary( value )
    return repr( value )
