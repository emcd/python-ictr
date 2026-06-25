## 1. Package-Level Protocol

- [ ] 1.1 Create `sources/ictr/renderables.py` with `Renderable` and `RenderableDataclass` protocols
- [ ] 1.2 Update `sources/ictr/standard/renderables.py` to import from package level and alias for backward compatibility
- [ ] 1.3 Update `sources/ictr/__init__.py` to export `Renderable`

## 2. Validation

- [ ] 2.1 Run linters and type checkers
- [ ] 2.2 Run tests to verify no regressions
- [ ] 2.3 Verify `from ictr import Renderable` works
