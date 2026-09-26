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

ictr 1.0a1 (2026-09-26)
=======================

Enhancements
------------

- API: Add Presentation protocol and PlaintextPresentation, JsonPresentation,
  MarkdownPresentation classes in ictr.standard for rendering objects in
  different formats. Presentations are exported from ictr.standard.
- API: Add Renderable and RenderableDataclass protocols at package level for
  objects that can render themselves as dictionaries. RenderableDataclass
  inherits from Renderable, following the classcore protocol hierarchy pattern.
- API: Export configuration and flavors module members from ictr package for
  direct import access.
- API: Support optional requests for colorization or decolorization in printers.
  Use consistent typing.TextIO interface for printer output streams.


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
