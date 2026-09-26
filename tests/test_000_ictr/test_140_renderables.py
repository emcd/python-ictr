# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.         #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,        #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#  See the License for the specific language governing permissions and      #
#  limitations under the License.                                           #
#                                                                            #
#============================================================================#


''' Tests for renderable protocols. '''


from unittest.mock import MagicMock

from ictr import printers as _printers
from ictr import renderables as _renderables
from ictr.standard import linearizers as _linearizers
from ictr.standard import presentations as _presentations
from ictr.standard import renderables as _std_renderables


class _DuckTypedRenderable:
    ''' Duck-typed object with render_as_dictionary. '''

    def __init__( self, name: str, count: int ):
        self.name = name
        self.count = count

    def render_as_dictionary( self ) -> dict:
        return { 'name': self.name, 'count': self.count }


class _JsonExample( _std_renderables.JsonRenderableDataclass ):
    ''' Concrete JsonRenderableDataclass subclass. '''

    def render_as_dictionary( self ) -> dict:
        return { 'name': 'test', 'count': 42 }


class _MarkdownExample( _std_renderables.MarkdownRenderableDataclass ):
    ''' Concrete MarkdownRenderableDataclass subclass. '''

    def render_as_dictionary( self ) -> dict:
        return { 'name': 'test', 'count': 42 }


class _RenderableDataclassExample( _renderables.RenderableDataclass ):
    ''' Concrete RenderableDataclass subclass. '''

    def __init__( self ):
        self._name = 'test'
        self._count = 42

    def render_as_dictionary( self ) -> dict:
        return { 'name': self._name, 'count': self._count }


class _InheritedExample( _renderables.RenderableDataclass ):
    ''' Concrete RenderableDataclass subclass using inherited default. '''

    name: str = 'test'
    count: int = 42


def _make_auxdata( colorize: bool = False ):
    config = _linearizers.LinearizerConfiguration( )
    control = MagicMock( spec = _printers.TextualizationControl )
    control.colorize = colorize
    control.columns_max = None
    return _linearizers.LinearizerState(
        configuration = config,
        control = control,
        colorize = colorize,
        columns_max = None )


class Test_000_Renderable_Detection:
    ''' Renderable protocol detection. '''

    def test_000_nominal_subclass_isinstance( self ):
        ''' Nominal subclass passes isinstance check. '''
        obj = _JsonExample( )
        assert isinstance( obj, _renderables.Renderable )

    def test_010_duck_typed_is_not_instance( self ):
        ''' Duck-typed object fails isinstance check. '''
        obj = _DuckTypedRenderable( name = 'test', count = 42 )
        assert not isinstance( obj, _renderables.Renderable )

    def test_020_duck_typed_has_render_as_dictionary( self ):
        ''' Duck-typed object has render_as_dictionary. '''
        obj = _DuckTypedRenderable( name = 'test', count = 42 )
        assert callable( getattr( obj, 'render_as_dictionary', None ) )

    def test_030_noncallable_attribute_not_detected( self ):
        ''' Noncallable render_as_dictionary is not detected. '''

        class Noncallable:
            render_as_dictionary = 'not a method'

        obj = Noncallable( )
        assert not callable( getattr( obj, 'render_as_dictionary', None ) )


class Test_100_Protocol_Inheritance:
    ''' Protocol inheritance hierarchy. '''

    def test_000_dataclass_inherits_renderable( self ):
        ''' RenderableDataclass inherits from Renderable. '''
        assert _renderables.Renderable in \
            _renderables.RenderableDataclass.__mro__

    def test_010_json_dataclass_inherits_json( self ):
        ''' JsonRenderableDataclass inherits from JsonRenderable. '''
        assert _std_renderables.JsonRenderable in \
            _std_renderables.JsonRenderableDataclass.__mro__

    def test_020_markdown_dataclass_inherits_markdown( self ):
        ''' MarkdownRenderableDataclass inherits MarkdownRenderable. '''
        assert _std_renderables.MarkdownRenderable in \
            _std_renderables.MarkdownRenderableDataclass.__mro__

    def test_030_json_dataclass_inherits_dataclass( self ):
        ''' JsonRenderableDataclass inherits RenderableDataclass. '''
        assert _renderables.RenderableDataclass in \
            _std_renderables.JsonRenderableDataclass.__mro__

    def test_040_markdown_dataclass_inherits_dataclass( self ):
        ''' MarkdownRenderableDataclass inherits RenderableDataclass. '''
        assert _renderables.RenderableDataclass in \
            _std_renderables.MarkdownRenderableDataclass.__mro__


class Test_200_Inherited_Renderers:
    ''' Concrete subclasses inherit default renderers. '''

    def test_000_renderable_dataclass_render_as_dictionary( self ):
        ''' RenderableDataclass subclass inherits render_as_dictionary. '''
        obj = _RenderableDataclassExample( )
        result = obj.render_as_dictionary( )
        assert result == { 'name': 'test', 'count': 42 }

    def test_010_json_dataclass_render_as_json( self ):
        ''' JsonRenderableDataclass subclass inherits render_as_json. '''
        obj = _JsonExample( )
        auxdata = _make_auxdata( )
        result = obj.render_as_json( auxdata )
        assert '"name": "test"' in result
        assert '"count": 42' in result

    def test_020_json_dataclass_render_as_json_compact( self ):
        ''' JsonRenderableDataclass subclass supports compact mode. '''
        obj = _JsonExample( )
        auxdata = _make_auxdata( )
        result = obj.render_as_json( auxdata, compact = True )
        assert '"name":"test"' in result

    def test_030_markdown_dataclass_render_as_markdown( self ):
        ''' MarkdownRenderableDataclass inherits render_as_markdown. '''
        obj = _MarkdownExample( )
        auxdata = _make_auxdata( )
        result = obj.render_as_markdown( auxdata )
        assert '**name**' in result
        assert 'test' in result

    def test_040_nested_renderable_serialization( self ):
        ''' Nested renderable values serialize via inherited method. '''
        inner = _RenderableDataclassExample( )
        result = _renderables._serialize_value( inner )
        assert result == { 'name': 'test', 'count': 42 }

    def test_045_inherited_default_render_as_dictionary( self ):
        ''' Inherited default render_as_dictionary serializes fields. '''
        obj = _InheritedExample( )
        result = obj.render_as_dictionary( )
        assert result == { 'name': 'test', 'count': 42 }

    def test_047_nested_inherited_default_serialization( self ):
        ''' Nested inherited default serializes via public function. '''

        class Outer:
            def __init__( self ):
                self.nested = _InheritedExample( )

        outer = Outer( )
        result = _renderables.render_as_dictionary( outer )
        assert result == { 'nested': { 'name': 'test', 'count': 42 } }

    def test_050_nested_duck_typed_serialization( self ):
        ''' Duck-typed values serialize via callable check. '''
        inner = _DuckTypedRenderable( name = 'inner', count = 1 )
        result = _renderables._serialize_value( inner )
        assert result == { 'name': 'inner', 'count': 1 }

    def test_060_nested_noncallable_not_serialized( self ):
        ''' Noncallable render_as_dictionary falls through to repr. '''

        class Noncallable:
            render_as_dictionary = 'not a method'

        result = _renderables._serialize_value( Noncallable( ) )
        assert isinstance( result, str )


class Test_300_Presentation_Routes:
    ''' Presentation classes detect and render renderables. '''

    def test_000_json_presentation_is_renderable( self ):
        ''' JsonPresentation detects renderable objects. '''
        presentation = _presentations.JsonPresentation( )
        obj = _JsonExample( )
        assert presentation.is_renderable( obj )

    def test_010_json_presentation_render( self ):
        ''' JsonPresentation renders renderable objects. '''
        presentation = _presentations.JsonPresentation( )
        obj = _JsonExample( )
        auxdata = _make_auxdata( )
        result = presentation.render( auxdata, obj )
        assert '"name": "test"' in result

    def test_020_markdown_presentation_is_renderable( self ):
        ''' MarkdownPresentation detects renderable objects. '''
        presentation = _presentations.MarkdownPresentation( )
        obj = _MarkdownExample( )
        assert presentation.is_renderable( obj )

    def test_030_markdown_presentation_render( self ):
        ''' MarkdownPresentation renders renderable objects. '''
        presentation = _presentations.MarkdownPresentation( )
        obj = _MarkdownExample( )
        auxdata = _make_auxdata( )
        result = presentation.render( auxdata, obj )
        assert '**name**' in result
