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


''' Common imports used throughout the package. '''

# ruff: noqa: F401


import                      abc
import collections.abc as   cabc
import                      codecs
import dataclasses as       dcls
import                      enum
import functools as         funct
import                      inspect
import                      io
import itertools as         itert
import                      locale
import                      os
import                      pprint
import                      re
import                      shutil
import                      sys
import traceback as         tb
import                      textwrap
import threading as         threads
import                      time
import                      types
import                      warnings

from datetime import datetime as Datetime, timezone as Timezone

import accretive as         accret
import exceptiongroup as    excg
import typing_extensions as typx
import                      wcwidth
# --- BEGIN: Injected by Copier ---
import dynadoc as           ddoc
import frigid as            immut
# --- END: Injected by Copier ---

# --- BEGIN: Injected by Copier ---
from absence import Absential, absent, is_absent
# --- END: Injected by Copier ---
