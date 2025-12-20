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


''' Standard textual presentations. '''


from . import __
from . import linearizers as _linearizers
from . import renderables as _renderables


@__.typx.runtime_checkable
class Presentation(
    __.immut.DataclassProtocol, __.typx.Protocol,
    class_mutables = __.PROTOCOL_RTC_MUTABLES,
):
    ''' Abstract base for presentations.

        Detects and invokes renderables with configuration.
    '''

    @__.abc.abstractmethod
    def is_renderable( self, entity: object ) -> bool:
        ''' Does object support this presentation mode? '''
        raise NotImplementedError

    def linearize(
        self, auxdata: _linearizers.LinearizerState, entity: object
    ) -> tuple[ str, ... ]:
        ''' Produces contiguous lines of text to render. '''
        return tuple( self.render( auxdata, entity ).split( '\n' ) )

    @__.abc.abstractmethod
    def render(
        self, auxdata: _linearizers.LinearizerState, entity: object
    ) -> str:
        ''' Renders object via its protocol implementation. '''
        raise NotImplementedError


class PlaintextPresentation( Presentation ):
    ''' Default presentation via standard linearization. '''

    def is_renderable( self, entity: object ) -> bool: return True

    def linearize(
        self, auxdata: _linearizers.LinearizerState, entity: object
    ) -> tuple[ str, ... ]:
        from .linearizers import linearize_omni
        # if isinstance( entity, PlaintextRenderable ):
        #     text = entity.render_as_plaintext( )
        #     return tuple( text.split( '\n' ) )
        return linearize_omni( auxdata, entity, auxdata.columns_max )

    def render(
        self, auxdata: _linearizers.LinearizerState, entity: object
    ) -> str:
        return '\n'.join( self.linearize( auxdata, entity ) )


_JSON_RENDERABLES = (
    _renderables.JsonRenderable,
    _renderables.JsonRenderableDataclass )
class JsonPresentation( Presentation ):
    ''' JSON presentation with configuration. '''

    compact: bool = False
    indent: int = 2

    def is_renderable( self, entity: object ) -> bool:
        return isinstance( entity, _JSON_RENDERABLES )

    def render(
        self, auxdata: _linearizers.LinearizerState, entity: object
    ) -> str:
        if isinstance( entity, _JSON_RENDERABLES ):
            return entity.render_as_json(
                auxdata, compact = self.compact, indent = self.indent )
        raise NotImplementedError  # TODO: Better error.


_MARKDOWN_RENDERABLES = (
    _renderables.MarkdownRenderable,
    _renderables.MarkdownRenderableDataclass )
class MarkdownPresentation( Presentation ):

    def is_renderable( self, entity: object ) -> bool:
        return isinstance( entity, _MARKDOWN_RENDERABLES )

    def render(
        self, auxdata: _linearizers.LinearizerState, entity: object
    ) -> str:
        if isinstance( entity, _MARKDOWN_RENDERABLES ):
            return entity.render_as_markdown( auxdata )
        raise NotImplementedError  # TODO: Better error.
