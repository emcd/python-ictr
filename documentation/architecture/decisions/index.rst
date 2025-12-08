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
Architectural Decision Records
*******************************************************************************

This directory contains architectural decision records (ADRs) documenting
significant design choices made during the project lifecycle. Each ADR
captures the context, decision, alternatives considered, and consequences.

Active Decisions
===============================================================================

001. :doc:`Layered Architecture with Protocol-Based Boundaries <001-layered-architecture>`

    Separates concerns across dispatcher, reporter, textualizer, and printer
    layers with protocol-based interfaces.

002. :doc:`Hierarchical Configuration Following Package Structure <002-hierarchical-configuration>`

    Configuration inheritance follows Python package hierarchy for
    library-friendly isolation and application control.

Superseded Decisions
===============================================================================

None yet.

.. toctree::
   :maxdepth: 1
   :hidden:

   001-layered-architecture
   002-hierarchical-configuration
