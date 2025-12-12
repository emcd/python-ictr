.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Release Notes
*******************************************************************************

.. towncrier release notes start

ictr 1.0a0 (2025-12-11)
=======================

Enhancements
------------

- Add comprehensive examples documentation covering basic usage, trace levels, exception handling, and library integration.
- Add errorx and abortx flavors for automatic exception capture and formatting with full stack traces.
- Add standard message flavors with semantic labels and optional emoji/color styling: note, monition, error, abort, future, success, and advice.
- Clarify library integration workflow with clear separation of concerns between libraries and applications.
- Implement ten hierarchical trace levels (0-9) with automatic indentation for visualizing call depth and execution flow.
- Provide global dispatcher available in Python builtins after initial setup for zero-import access throughout applications.
