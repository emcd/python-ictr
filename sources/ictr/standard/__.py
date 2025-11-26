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


# ruff: noqa: F401, F403


from ..__ import *
from ..exceptions import *
from ..flavors import Flavor
from ..printers import *
from ..records import *
from ..textualizers import *

ENRICH = False
try:
    import rich.console as      rich_console
    import rich.text as         rich_text
    import rich.traceback as    rich_traceback
    ENRICH = True  # pyright: ignore[reportConstantRedefinition]
except ImportError: pass
