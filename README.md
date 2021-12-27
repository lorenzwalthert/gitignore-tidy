
This little python package exposes one command line executable and [pre-commit hook](https://pre-commit.com) that can be used to tidy up a `.gitignore` file. It does

* remove leading or trailing white space (unless `--allow-leading-white-space` is set).
* remove duplicate entries.
* allow at most one blank line before comments.
* order entries while respecting that [negating entries](https://git-scm.com/docs/gitignore#_pattern_format) must always go *after* non-negating entries, e.g.


```
a/
!a/b
```

## CLI

```bash
gitignore-tidy # in repo root
```

## pre-commit hook

In your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/lorenzwalthert/gitignore-tidy
    rev: 60fc25cef15cbc8f96e766d951cd594d5bf7555a
    hooks:
    -   id: tidy-gitignore
        # args: [--allow-leading-whitespace]
```
