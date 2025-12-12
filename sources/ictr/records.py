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


''' Records to inscribe. '''


from . import __
from . import flavors as _flavors


MessageDetail: __.typx.TypeAlias = str
MessageDetails: __.typx.TypeAlias = tuple[ MessageDetail, ... ]
MessageSummary: __.typx.TypeAlias = str | BaseException


class Content( __.immut.DataclassObject ):
    ''' Abstract base class for content. '''


class MessageContent( Content ):
    ''' Content for standard messages. '''

    summary: MessageSummary
    details: MessageDetails


class Record( __.immut.DataclassObject ):
    ''' Content with metadata. '''

    address: str
    content: Content
    flavor: _flavors.Flavor
    # TODO? 'ttl' for printing to other reporters
    ctime: __.Datetime = __.dcls.field(
        default_factory = lambda: __.Datetime.now( __.Timezone.utc ) )
    # TODO? 'excinfo' (exception info)
