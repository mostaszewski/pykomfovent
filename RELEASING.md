# Release Checklist

## Before releasing

1. Ensure all tests pass: `uv run pytest`
2. Ensure linting passes: `uv run ruff check src/ tests/`
3. Ensure type checking passes: `uv run pyright src/`
4. Ensure formatting is correct: `uv run ruff format --check src/ tests/`

## Release steps

1. Update version in `pyproject.toml`
2. Update version in `src/pykomfovent/__init__.py`
3. Update `CHANGELOG.md` with release notes
4. Commit changes: `git commit -am "Release vX.Y.Z"`
5. Push to main: `git push origin main`
6. Wait for CI to pass
7. Create GitHub release:
   - Go to https://github.com/mostaszewski/pykomfovent/releases/new
   - Tag: `vX.Y.Z` (e.g., `v1.0.0`)
   - Title: `vX.Y.Z`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"
8. CI will automatically publish to PyPI
