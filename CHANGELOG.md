## 0.1.3 (2025-09-28)

### Refactor

- simplify conditional
- iterable is fine, no need for list
- more type annotation, type fixes
- be generic about input, specific about output
- import annotations from __future__ to avoid quoting undeclared classes
- no need to check for path existance if the goal is to raise the same exception that attempting to read the file would
- use typing.Self or typing_extensions.Self depending on version with the goal to keep reminder in code
- more renaming
- simplify classes
- use INFO level only
- convert from functional to object oriented

### Perf

- pre-compile patterns
- avoid performance implication for fstring formatting in logging

## 0.1.2 (2024-03-21)

### Refactor

- Move cli to separate file
- add type hints to source code

## 0.1.1 (2024-03-20)

This is the first git tag pushed to the repo (previous version 0.1.0 was only set in `pyproject.toml`). This means that `$ pre-commit autoupdate` will now set `rev:` to the tag instead of the commit hash and subsequent new commits pushed to the default branch (withouth pushing a new tag) of this repo will only be updated with `$ pre-commit autoupdate --bleeding-edge` in downstream contexts.

### Fix

- Drop requirement for python version
- Don't require a specific Python version
