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
Library Integration
*******************************************************************************

How to use ``ictr`` within a library without interfering with application-level
configuration.

Registering Addresses
===============================================================================

Libraries should use ``register_address`` instead of ``install``. This allows
the library to set defaults for its own modules, which can be overridden by
the application developer.

.. code-block:: python

    # mylibrary/__init__.py
    import ictr
    
    # Register library-specific configuration
    ictr.register_address(
        'mylibrary',
        flavors={
            # Custom library flavors or overrides
        }
    )

    # Use in code
    def do_something():
        # Will use registered configuration if installed, or default if not.
        # But 'ictr' needs to be available. 
        # Libraries typically don't import 'ictr' from builtins directly 
        # unless they document it as a dependency.
        # Better pattern: import package
        import ictr
        # Access dispatcher. 
        # If application installed it, it's configured.
        # If not, you might need a local fallback or check.
        pass

Actually, ``register_address`` is available on the module level for convenience.

.. testsetup:: library

    import ictr
    from io import StringIO
    from unittest.mock import patch
    capture = StringIO()
    
    class MockPrinter:
        def __init__(self, address, flavor): self.flavor = flavor
        def __call__(self, record):
            print(f"[{self.flavor}] {record.content.summary}", file=capture)
        def provide_textualization_control(self): return None

    def capture_factory(address, flavor): return MockPrinter(address, flavor)
    
    # Simulate application install
    ictr_app = ictr.install(printer_factories=[capture_factory])

.. doctest:: library

    >>> # Library code registers its preferences
    >>> ictr.register_address(
    ...     'mylib',
    ...     # Library wants 'debug' flavor to be active by default? 
    ...     # No, active flavors are global/per-address config.
    ...     # Configuration is for compositors/printers/etc.
    ... )
    AddressConfiguration(compositor_factory=None, flavors=frigid.dictionaries.Dictionary( {} ))
    
    >>> # Using the installed dispatcher
    >>> ictr_app('note', address='doctest')('Library message.')
    
    >>> print(capture.getvalue().strip())
    [note] Library message.

.. testcleanup:: library

    import builtins
    if hasattr(builtins, 'ictr'):
        delattr(builtins, 'ictr')