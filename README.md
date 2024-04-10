# Tidy up your `.gititnore` files

This little python package exposes one command line executable and [pre-commit hook](https://pre-commit.com) that can be used to tidy up a `.gitignore` file. It does

* remove leading or trailing white space (unless `--allow-leading-white-space` is set).
* remove duplicate entries.
* allow at most one blank line before comments.
* order entries while respecting that [negating entries](https://git-scm.com/docs/gitignore#_pattern_format) must always go *after* non-negating entries, e.g.


```
a/
!a/b
```

**Caution**

Sorting while preserving the pattern is complex in some cases. If you have
negating entries and wild-cards that are not at the end of the line within
the same section, running the current version may change your `.gitignore`
pattern and we advise against using this program in that case!
We might revisit the algoritm in the future to fix it for these cases:

```
# my first section
*csv
!*aut.csv

# another
*.pdf
```
Swapping the first two entries in the first section will change the exclusion pattern (just put `a.csv` and `aut.csv` into your repo to see why).

## CLI

```bash
gitignore-tidy # in repo root
```

## pre-commit hook

In your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/lorenzwalthert/gitignore-tidy
    rev: bb80136de68e7fe844cd0397f0088f469845d258.
    hooks:
    -   id: tidy-gitignore
        # args: [--allow-leading-whitespace]
```

And run `pre-commit autopudate` to get the latest hook version.
