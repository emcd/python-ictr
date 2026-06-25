# Change: Hoist Renderable Protocol to Package Level

## Why

The `DictionaryRenderable` protocol in `standard/renderables.py` defines the
cross-package contract for objects that can render themselves as dictionaries.
Appcore will import this protocol from ictr as a shared primitive. Protocols
that define the public API belong at the package level, not buried in a
subpackage of defaults.

## What Changes

- Create `sources/ictr/renderables.py` with `Renderable` protocol (renamed
  from `DictionaryRenderable`)
- Update `standard/renderables.py` to import `Renderable` from the new
  location and alias it as `DictionaryRenderable` for backward compatibility
- Update `sources/ictr/__init__.py` to export `Renderable`

## Impact

- Affected specs: new `renderables` capability
- Affected code: `sources/ictr/renderables.py` (new),
  `sources/ictr/standard/renderables.py`, `sources/ictr/__init__.py`
