# Tidy up your `.gititnore` files

This little python package exposes one command line executable and [pre-commit hook](https://pre-commit.com) that can be used to tidy up a `.gitignore` file. It does

* remove leading or trailing white space (unless `--allow-leading-white-space` is set).
* remove duplicate entries.
* allow at most one blank line before comments.
* sort entries without ever changing what your `.gitignore` matches. The
  order of [negating entries](https://git-scm.com/docs/gitignore#_pattern_format)
  relative to other entries can change the meaning of the file, so every
  negating entry (leading `!`) is left exactly where it is; only the runs of
  non-negating entries between them are sorted:

```
b
a
!c/**/
z
```

becomes

```
a
b
!c/**/
z
```

This makes the following safe, whereas older versions would silently turn
`aut.csv` from tracked into ignored:

```
# my first section
*csv
!*aut.csv

# another
*.pdf
```

**`--negations-last`**

If you prefer all negating entries collected at the end, opt in with
`--negations-last`:

* `--negations-last=group` – within each section, sorted non-negating entries
  first, then that section's sorted negating entries.
* `--negations-last=eof` – all negating entries from the whole file, sorted,
  moved into a single block at the end.

**Caution:** unlike the default, both of these move negating entries relative
to other entries and *can* change which paths your `.gitignore` matches. Only
use them if you know your patterns don't rely on ordering.

## CLI

```bash
gitignore-tidy # in repo root
gitignore-tidy path/to/.gitignore another/.gitignore
gitignore-tidy --negations-last=group   # optional, see caution above
```

## pre-commit hook

In your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/lorenzwalthert/gitignore-tidy
    rev: bb80136de68e7fe844cd0397f0088f469845d258.
    hooks:
    -   id: tidy-gitignore
        # args: [--allow-leading-whitespace]
        # args: [--negations-last=group]
```

And run `pre-commit autopudate` to get the latest hook version.
