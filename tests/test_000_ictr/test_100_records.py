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


''' Tests for records and content types. '''


import pytest

from ictr import records as _records


class Test_000_Records:
    ''' Basic record functionality. '''

    def test_000_creation( self ):
        ''' Record creation with all fields works as expected. '''
        content = _records.MessageContent(
            summary = 'test summary', details = ( ) )
        record = _records.Record(
            address = 'test.address',
            content = content,
            flavor = 'note' )
        assert record.address == 'test.address'
        assert record.content is content
        assert record.flavor == 'note'
        assert record.ctime is not None

    def test_010_message_content_summary_only( self ):
        ''' MessageContent with summary only works as expected. '''
        content = _records.MessageContent(
            summary = 'test summary', details = ( ) )
        assert content.summary == 'test summary'
        assert content.details == ( )

    def test_020_message_content_summary_and_details( self ):
        ''' MessageContent with summary and details works as expected. '''
        content = _records.MessageContent(
            summary = 'test summary', details = ( 'detail 1', 'detail 2' ) )
        assert content.summary == 'test summary'
        assert content.details == ( 'detail 1', 'detail 2' )


class Test_100_Record_Components:
    ''' Record component validation. '''

    def test_100_empty_content( self ):
        ''' Record with empty content works as expected. '''
        content = _records.MessageContent( summary = '', details = ( ) )
        record = _records.Record(
            address = 'test.address',
            content = content,
            flavor = 'note' )
        assert record.content.summary == ''

    def test_120_timestamp_generation( self ):
        ''' Record generates timestamp automatically. '''
        content = _records.MessageContent( summary = 'test', details = ( ) )
        record1 = _records.Record(
            address = 'test', content = content, flavor = 'note' )
        import time
        time.sleep( 0.001 )
        record2 = _records.Record(
            address = 'test', content = content, flavor = 'note' )
        assert record1.ctime != record2.ctime
        assert record1.ctime < record2.ctime

    def test_130_immutability( self ):
        ''' Record is immutable. '''
        content = _records.MessageContent( summary = 'test', details = ( ) )
        record = _records.Record(
            address = 'test', content = content, flavor = 'note' )
        with pytest.raises( AttributeError ):
            record.address = 'new address'


class Test_200_MessageContent_Components:
    ''' MessageContent component validation. '''

    def test_200_various_detail_types( self ):
        ''' MessageContent accepts various detail types. '''
        details = ( 'str', 123, { 'a': 1 }, object() )
        content = _records.MessageContent(
            summary = 'test', details = details )
        assert content.details == details

    def test_210_exception_summary( self ):
        ''' MessageContent accepts BaseException as summary. '''
        exc = ValueError( 'test error' )
        content = _records.MessageContent( summary = exc, details = ( ) )
        assert content.summary is exc

    def test_220_empty_details( self ):
        ''' MessageContent with empty details works as expected. '''
        content = _records.MessageContent( summary = 'test', details = ( ) )
        assert content.details == ( )
        assert len( content.details ) == 0

    def test_230_immutability( self ):
        ''' MessageContent is immutable. '''
        content = _records.MessageContent( summary = 'test', details = ( ) )
        with pytest.raises( AttributeError ):
            content.summary = 'new summary'
