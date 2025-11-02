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
from . import configuration as _cfg
from . import printers as _printers


MessageSummary: __.typx.TypeAlias = str | Exception
MessageDetail: __.typx.TypeAlias = str


class Reporter( __.immut.DataclassObject ):
    ''' Formats and prints messages to targets. '''

    name: str
    active: bool  # TODO? Also accept predicate function to decide if active.
    flavor: _cfg.Flavor
    formatter: _cfg.Formatter
    printer: _printers.Printer

    def __call__(
        self, summary: MessageSummary, *details: MessageDetail
    ) -> None:
        # TODO? Return record.
        if not self.active: return
        # TODO: Produce record from arguments.
        # TODO: Invoke formatter on record.
        # TODO: Print formatted message.

    # TODO: inscribe (same as __call__)
    # TODO: inscribe_async
    # TODO? inspect
    # TODO? Ability to print stack traces either from current frame or from
    #       supplied traceback. Maybe various modes, such as compact or
    #       detailed (showing names and values of locals).
