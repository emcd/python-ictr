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


''' Internal imports for textualizers and their attendants. '''


# ruff: noqa: F401, F403, F405


from ..__ import *
from ..configuration import *
from ..exceptions import *
from ..flavors import *
from ..printers import *
from ..records import *
from ..textualizers import *

ENRICH = False
try:

    import rich.console as      rich_console
    import rich.style as        rich_style
    import rich.text as         rich_text
    import rich.traceback as    rich_traceback

    ENRICH = True  # pyright: ignore[reportConstantRedefinition]

    def produce_rich_console(
        control: TextualizationControl,
        capture: typx.IO[ str ],
        columns_max: Absential[ int ] = absent,
    ) -> rich_console.Console:
        charset = control.charset or ''
        colorize = control.colorize
        columns_max_nullable = (
            None if is_absent( columns_max ) else columns_max )
        safe = charset.startswith( 'utf-' )
        return rich_console.Console(
            file = capture,
            force_terminal = colorize,
            no_color = not colorize,
            safe_box = safe,
            width = columns_max_nullable )

except ImportError: pass
