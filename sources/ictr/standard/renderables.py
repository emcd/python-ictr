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


''' Protocols and default implementations for renderable objects. '''


import json as _json

from . import __
from . import linearizers as _linearizers


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
        self,
        auxdata: _linearizers.LinearizerState, /, *,
        compact: bool = False,
        indent: int = 2,
    ) -> str:
        ''' Returns JSON string representation. '''
        dictionary = self.render_as_dictionary( )
        return _render_as_json(
            dictionary, compact = compact, indent = indent )


@__.typx.runtime_checkable
class JsonRenderableDataclass(
    DictionaryRenderableDataclass, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Dataclass objects which can be rendered as JSON. '''

    def render_as_json(
        self,
        auxdata: _linearizers.LinearizerState, /, *,
        compact: bool = False,
        indent: int = 2,
    ) -> str:
        ''' Returns JSON string representation. '''
        dictionary = self.render_as_dictionary( )
        return _render_as_json(
            dictionary, compact = compact, indent = indent )


@__.typx.runtime_checkable
class MarkdownRenderable(
    DictionaryRenderable, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Objects which can be rendered as Markdown. '''

    def render_as_markdown(
        self, auxdata: _linearizers.LinearizerState, /
    ) -> str:
        ''' Returns Markdown string representation. '''
        dictionary = self.render_as_dictionary( )
        return _render_as_markdown( dictionary, auxdata )


@__.typx.runtime_checkable
class MarkdownRenderableDataclass(
    DictionaryRenderableDataclass, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Dataclass objects which can be rendered as Markdown. '''

    def render_as_markdown(
        self, auxdata: _linearizers.LinearizerState, /
    ) -> str:
        ''' Returns Markdown string representation. '''
        dictionary = self.render_as_dictionary( )
        return _render_as_markdown( dictionary, auxdata )


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


def _dictionary_to_markdown_lines(
    dictionary: __.cabc.Mapping[ __.typx.Any, __.typx.Any ],
    auxdata: _linearizers.LinearizerState,
    level: int = 0,
) -> tuple[ str, ... ]:
    lines: list[ str ] = [ ]
    prefix = ( '  ' * level + '- ' ) if level else ''
    level += 1
    for name, value in dictionary.items( ):
        name_ = f"**{name}**"
        if value is None:
            lines.append( f"{prefix}{name_}: (none)" )
        elif isinstance( value, ( bool, int, float, str ) ):
            lines.append( f"{prefix}{name_}: {value}" )
        elif isinstance( value, __.cabc.Container ) and not value:
            lines.append( f"{prefix}{name_}: (empty)" )
        elif isinstance( value, __.cabc.Sequence ):
            lines.append( f"{prefix}{name_}:" )
            lines.extend( _sequence_to_markdown_lines(
                __.typx.cast( __.cabc.Sequence[ __.typx.Any ], value ),
                auxdata, level = level ) )
        elif isinstance( value, __.cabc.Mapping ):
            lines.append( f"{prefix}{name_}:" )
            lines.extend( _dictionary_to_markdown_lines(
                __.typx.cast(
                    __.cabc.Mapping[ __.typx.Any, __.typx.Any ], value ),
                auxdata, level ) )
        else: lines.append( f"{prefix}{name_}: {value}" )
    return tuple( lines )


def _render_as_json(
    dictionary: dict[ str, __.typx.Any ],
    compact: bool = False, indent: int = 2,
) -> str:
    ''' Returns JSON string representation. '''
    if compact:
        return _json.dumps(
            dictionary, ensure_ascii = False, separators = ( ',', ':' ) )
    return _json.dumps( dictionary, ensure_ascii = False, indent = indent )


def _render_as_markdown(
    dictionary: dict[ str, __.typx.Any ],
    auxdata: _linearizers.LinearizerState,
    level: int = 0,
) -> str:
    ''' Returns Markdown string representation. '''
    lines = _dictionary_to_markdown_lines( dictionary, auxdata, level = level )
    markdown = '\n'.join( lines )
    if auxdata.colorize:
        # TODO? Parse colors from result.
        #       markdown_c = __.rich_text.Text.from_ansi( markdown )
        capture = __.io.StringIO( )
        console = __.produce_rich_console(
            auxdata.control, capture, auxdata.columns_max )
        console.print( __.rich_markdown.Markdown( markdown ) )
        return capture.getvalue( ).rstrip( '\n' )
    return markdown


def _sequence_to_markdown_lines(
    sequence: __.cabc.Sequence[ __.typx.Any ],
    auxdata: _linearizers.LinearizerState,
    level: int = 0,
) -> tuple[ str, ... ]:
    lines: list[ str ] = [ ]
    prefix = '  ' * level + '- '
    level += 1
    for element in sequence:
        if element is None:
            lines.append( f"{prefix}(none)" )
        elif isinstance( element, __.cabc.Container ) and not element:
            lines.append( f"{prefix}(empty)" )
        elif isinstance( element, __.cabc.Sequence ):
            lines.append( prefix )
            lines.extend( _sequence_to_markdown_lines(
                __.typx.cast( __.cabc.Sequence[ __.typx.Any ], element ),
                auxdata, level = level ) )
        elif isinstance( element, __.cabc.Mapping ):
            lines.append( prefix )
            lines.extend( _dictionary_to_markdown_lines(
                __.typx.cast(
                    __.cabc.Mapping[ __.typx.Any, __.typx.Any ], element ),
                auxdata, level = level ) )
        else: lines.append( f"{prefix}{element}" )
    return tuple( lines )


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
