# How to contribute to this repo

Required software:
* git
* pre-commit
* poetry

## Initial setup


```bash
pre-commit install # for pre-commit hooks
poetry install
```

## How to commit

```bash
cz commit # on every commit
```


## How to create a new release
```bash
NEXTVERSION=$(yes | cz bump --dry-run | sed -n 's/tag to create: \(.*\).*/\1/p')
cz changelog --unreleased-version=$NEXTVERSION
cz bump
```
