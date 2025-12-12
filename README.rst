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
                                      ictr
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/ictr
   :alt: Package Version
   :target: https://pypi.org/project/ictr/

.. image:: https://img.shields.io/pypi/status/ictr
   :alt: PyPI - Status
   :target: https://pypi.org/project/ictr/

.. image:: https://github.com/emcd/python-ictr/actions/workflows/tester.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-ictr/actions/workflows/tester.yaml

.. image:: https://emcd.github.io/python-ictr/coverage.svg
   :alt: Code Coverage Percentage
   :target: https://github.com/emcd/python-ictr/actions/workflows/tester.yaml

.. image:: https://img.shields.io/github/license/emcd/python-ictr
   :alt: Project License
   :target: https://github.com/emcd/python-ictr/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/ictr
   :alt: Python Versions
   :target: https://pypi.org/project/ictr/


🖋️ **Ictr** is a system for logging and debug printing in Python applications.
It provides a clean, type-safe API for emitting diagnostic messages with
minimal boilerplate, featuring standard message flavors, hierarchical trace
levels for debugging depth, automatic exception tracebacks, and optional rich
rendering with colors and styling.

Designed as an alternative to traditional print debugging and verbose logging
setup, ``ictr`` can install a global dispatcher into the Python builtins,
similar to the well-known `icecream <https://github.com/gruns/icecream>`_
package, for effortless access throughout your application — no import
statements needed in every module. Perfect for both quick debugging sessions
and production logging with per-module configuration.

Key Features ⭐
===============================================================================

🎨 **Standard Message Flavors**: Pre-configured ``note``, ``monition``,
``error``, ``abort``, ``future``, ``success``, and ``advice`` flavors with
semantic labels and optional emoji/color styling.

🔢 **Hierarchical Trace Levels**: Ten trace levels (0-9) with automatic
indentation for visualizing call depth and execution flow.

💥 **Automatic Exception Tracebacks**: ``errorx`` and ``abortx`` flavors
capture and format active exceptions with full stack traces.

🌳 **Module Hierarchy**: Global and per-module configs with inheritance for
precise control over active flavors, trace levels, output formatting, etc....

🚀 **Zero-Import Access**: Global dispatcher available in builtins after
initial setup — no import statements needed in every module.

🖨️ **Printer Factory**: Dynamically associate output functions with reporters
based on module name, flavor, etc.... Swap in customized ``print``,
``logging``, or other sinks as desired.

📚 **Library-Friendly**: Non-intrusive registration for libraries without
stepping on application debugger/logging configuration.

Installation 📦
===============================================================================

Method: Install Python Package
-------------------------------------------------------------------------------

Install via `uv <https://github.com/astral-sh/uv/blob/main/README.md>`_ ``pip``
command:

::

    uv pip install ictr

Or, install via ``pip``:

::

    pip install ictr


Examples 💡
===============================================================================

For more detailed examples, please see the `examples documentation
<https://emcd.github.io/python-ictr/stable/sphinx-html/examples/index.html>`_.

Basic Usage
-------------------------------------------------------------------------------

Install an ``ictr`` dispatcher as a Python builtin (default alias, ``ictr``)
and then use it anywhere in your codebase:

.. code-block:: python

    import ictr

    ictr.install( )

    # Emit messages with different flavors
    ictr( 'note' )( 'Application started.' )       # NOTE|  Application started.
    ictr( 'error' )( 'Connection failed.' )        # ERROR|  Connection failed.
    ictr( 'success' )( 'Task completed.' )         # SUCCESS|  Task completed.

Trace Levels
-------------------------------------------------------------------------------

Use numeric trace levels (0-9) for hierarchical debugging output:

.. code-block:: python

    import ictr

    ictr.install( trace_levels = { None: 3 } )  # Enable levels 0-3 globally

    ictr( 0 )( 'Top-level operation' )          # TRACE0|  Top-level operation
    ictr( 1 )( 'Sub-operation details' )        #   TRACE1|  Sub-operation details
    ictr( 2 )( 'More detail' )                  #     TRACE2|  More detail
    ictr( 4 )( 'Too verbose' )                  # (suppressed - level > 3)

Exception Handling
-------------------------------------------------------------------------------

Use ``errorx`` or ``abortx`` flavors to capture active exceptions with
tracebacks:

.. code-block:: python

    import ictr

    ictr.install( )

    try:
        result = 1 / 0
    except ZeroDivisionError:
        ictr( 'errorx' )( 'Calculation failed.' )
        # ERROR|  Calculation failed.
        #
        # [ZeroDivisionError] division by zero
        #   File 'example.py', line 8, in <module>
        #       result = 1 / 0

Library Integration
-------------------------------------------------------------------------------

Libraries can register their own configurations without overriding those of the
application:

.. code-block:: python

    # mylibrary/__init__.py
    import ictr

    ictr.register_address( 'mylibrary' )

When ``install`` is called by the application, any addresses that were
previously registered via ``register_address`` are incorporated into the
installed dispatcher. This allows applications to setup output after libraries
have registered their configurations.


Motivation 🚚
===============================================================================

Why ``ictr``?

There is nothing wrong with the ``icecream`` or ``logging`` packages. However,
there are times that the author of ``ictr`` (and its predecessor,
``icecream-truck``) has wanted, for various reasons, more than these packages
inherently offer:

* **Coexistence**: Application and libraries can coexist without configuration
  clashes.

  - Library developers are `strongly advised not to create custom levels
    <https://docs.python.org/3/howto/logging.html#custom-levels>`_ in
    ``logging``.

  - Library developers are `advised on how to avoid polluting stderr
    <https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library>`_
    in ``logging``, when an application has not supplied a configuration.

  - Loggers `propagate upwards
    <https://docs.python.org/3/library/logging.html#logging.Logger.propagate>`_
    by default in ``logging``. This means that libraries must explicitly
    opt-out of propagation if their authors want to be good citizens and not
    contribute to noise pollution / signal obfuscation.

* **Granularity**: Control of debug output by depth threshold and subsystem.

  - Only one default debugging level (``DEBUG``) with ``logging``. Libraries
    cannot safely extend this. (See point about coexistence).

  - No concept of debugging level with ``ic`` builtin. Need to orchestrate
    multiple ``icecream.IceCreamDebugger`` instances to support this. (In
    fact, this is what ``icecream-truck`` does.)

  - While logger hierarchies in ``logging`` do support the notion of software
    subsystems, hierarchies are not always the most convenient or abbreviated
    way of representing subsystems which span parts or entireties of modules.

* **Signal**: Prevention of undesirable library chatter.

  - The ``logging`` root logger will log all messages, at its current log
    level or higher, which propagate up to it. Many Python libraries have
    opt-out rather than opt-in logging, so you see all of their ``DEBUG`` and
    ``INFO`` spam unless you surgically manipulate their loggers or squelch
    the overall log level.

  - Use of the ``ic`` builtin is only recommended for temporary debugging. It
    cannot be left in production code without spamming. While the ``enabled``
    flag on the ``ic`` builtin can be set to false, it is easy to forget and
    also applies to every place where ``ic`` is used in the code. (See point
    about granularity.)

* **Extensibility**: More natural integration with packages like ``rich`` via
  robust recipes.

  - While it is not difficult to change the ``argToStringFunction`` on ``ic``
    to be ``rich.pretty.pretty_repr``, there is some repetitive code involved
    in each project which wants to do this. And, from a safety perspective,
    there should be a fallback if ``rich`` fails to import.

  - Similarly, one can add a ``rich.logging.RichHandler`` instance to a
    logger instance with minimal effort. However, depending on the the target
    output stream, one may also need to build a ``rich.console.Console`` first
    and pass that to the handler. This handler will also compete with whatever
    handler has been set on the root logger. So, some care must be taken to
    prevent propagation. Again, this is repetitive code across projects and
    there are import safety fallbacks to consider.


About the Name 📝
===============================================================================

The name ``ictr`` has multiple origins and interpretations:

* 🍦 **Shortened from icecream-truck**: The package from which ``ictr`` is
  derived and redesigned. The abbreviation maintains the connection to its
  predecessor while establishing its own identity.

* 🎯 **Short and memorable**: Four letters that are easy to type and remember.
  The Python package distribution name and import name are the same, reducing
  cognitive overhead.

* 📊 **Backronym interpretations**: While ``ictr`` works perfectly well as
  just a name, several backronyms capture different aspects of its purpose:

  - **Inspection-Capable Trace Reporting** (emphasizes diagnostic capabilities)
  - **Intelligent Configurable Trace Reporter** (emphasizes smart behavior)
  - **I See Textual Reports** (playful take on the phonetic sound)

Pronunciation? You can spell it out. But, if that is too many syllables, then
maybe "eyes-tra" but probably not "ick-ter", because it is not that revulsive.


Contribution 🤝
===============================================================================

Contribution to this project is welcome! However, it must follow the `code of
conduct
<https://emcd.github.io/python-project-common/stable/sphinx-html/common/conduct.html>`_
for the project.

Please file bug reports and feature requests in the `issue tracker
<https://github.com/emcd/python-ictr/issues>`_ or submit `pull
requests <https://github.com/emcd/python-ictr/pulls>`_ to
improve the source code or documentation.

For development guidance and standards, please see the `development guide
<https://emcd.github.io/python-ictr/stable/sphinx-html/contribution.html#development>`_.


Additional Indicia
===============================================================================

.. image:: https://img.shields.io/github/last-commit/emcd/python-ictr
   :alt: GitHub last commit
   :target: https://github.com/emcd/python-ictr

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json
   :alt: Copier
   :target: https://github.com/copier-org/copier

.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
   :alt: Hatch
   :target: https://github.com/pypa/hatch

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :alt: pre-commit
   :target: https://github.com/pre-commit/pre-commit

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :alt: Pyright
   :target: https://microsoft.github.io/pyright

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :alt: Ruff
   :target: https://github.com/astral-sh/ruff

.. image:: https://img.shields.io/pypi/implementation/ictr
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/ictr/

.. image:: https://img.shields.io/pypi/wheel/ictr
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/ictr/


Other Projects by This Author 🌟
===============================================================================


* `python-absence <https://github.com/emcd/python-absence>`_ (`absence <https://pypi.org/project/absence/>`_ on PyPI)

  🕳️ A Python library package which provides a **sentinel for absent values** - a falsey, immutable singleton that represents the absence of a value in contexts where ``None`` or ``False`` may be valid values.
* `python-accretive <https://github.com/emcd/python-accretive>`_ (`accretive <https://pypi.org/project/accretive/>`_ on PyPI)

  🌌 A Python library package which provides **accretive data structures** - collections which can grow but never shrink.
* `python-classcore <https://github.com/emcd/python-classcore>`_ (`classcore <https://pypi.org/project/classcore/>`_ on PyPI)

  🏭 A Python library package which provides **foundational class factories and decorators** for providing classes with attributes immutability and concealment and other custom behaviors.
* `python-detextive <https://github.com/emcd/python-detextive>`_ (`detextive <https://pypi.org/project/detextive/>`_ on PyPI)

  🕵️ A Python library which provides consolidated text detection capabilities for reliable content analysis. Offers MIME type detection, character set detection, and line separator processing.
* `python-dynadoc <https://github.com/emcd/python-dynadoc>`_ (`dynadoc <https://pypi.org/project/dynadoc/>`_ on PyPI)

  📝 A Python library package which bridges the gap between **rich annotations** and **automatic documentation generation** with configurable renderers and support for reusable fragments.
* `python-falsifier <https://github.com/emcd/python-falsifier>`_ (`falsifier <https://pypi.org/project/falsifier/>`_ on PyPI)

  🎭 A very simple Python library package which provides a **base class for falsey objects** - objects that evaluate to ``False`` in boolean contexts.
* `python-frigid <https://github.com/emcd/python-frigid>`_ (`frigid <https://pypi.org/project/frigid/>`_ on PyPI)

  🔒 A Python library package which provides **immutable data structures** - collections which cannot be modified after creation.
* `python-icecream-truck <https://github.com/emcd/python-icecream-truck>`_ (`icecream-truck <https://pypi.org/project/icecream-truck/>`_ on PyPI)

  🍦 **Flavorful Debugging** - A Python library which enhances the powerful and well-known ``icecream`` package with flavored traces, configuration hierarchies, customized outputs, ready-made recipes, and more.
* `python-librovore <https://github.com/emcd/python-librovore>`_ (`librovore <https://pypi.org/project/librovore/>`_ on PyPI)

  🐲 **Documentation Search Engine** - An intelligent documentation search and extraction tool that provides both a command-line interface for humans and an MCP (Model Context Protocol) server for AI agents. Search across Sphinx and MkDocs sites with fuzzy matching, extract clean markdown content, and integrate seamlessly with AI development workflows.
* `python-mimeogram <https://github.com/emcd/python-mimeogram>`_ (`mimeogram <https://pypi.org/project/mimeogram/>`_ on PyPI)

  📨 A command-line tool for **exchanging collections of files with Large Language Models** - bundle multiple files into a single clipboard-ready document while preserving directory structure and metadata... good for code reviews, project sharing, and LLM interactions.
