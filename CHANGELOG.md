## 0.1.1 (2024-03-20)

This is the first git tag pushed to the repo (previous version 0.1.0 was only set in `pyproject.toml`). This means that `$ pre-commit autoupdate` will now set `rev:` to the tag instead of the commit hash and subsequent new commits pushed to the default branch (withouth pushing a new tag) of this repo will only be updated with `$ pre-commit autoupdate --bleeding-edge` in downstream contexts.

### Fix

- Drop requirement for python version
- Don't require a specific Python version
