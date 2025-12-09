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


''' Message reporters. '''


from . import __
from . import flavors as _flavors
from . import printers as _printers
from . import records as _records
from . import textualizers as _texts


class Reporter( __.immut.DataclassObject ):
    ''' Formats and prints messages to targets. '''

    active: bool  # TODO? Also accept predicate function to decide if active.
    address: str
    flavor: _flavors.Flavor
    compositor: _texts.Compositor
    printers: _printers.Printers

    def __call__(
        self,
        summary: _records.MessageSummary, /,
        *details: _records.MessageDetail,
    ) -> None:
        # TODO? Return record.
        ''' Prepares record and prints it. '''
        if not self.active: return
        content = _records.MessageContent(
            summary = summary, details = details )
        record = _records.Record(
            address = self.address, content = content, flavor = self.flavor )
        for printer in self.printers:
            tcontrol = printer.provide_textualization_control( )
            if tcontrol is None: printer( record )
            else: printer( self.compositor( tcontrol, record ) )

    # TODO: inscribe (same as __call__)
    # TODO: inscribe_async
    # TODO? inspect
    # TODO? Ability to print stack traces either from current frame or from
    #       supplied traceback. Maybe various modes, such as compact or
    #       detailed (showing names and values of locals).
