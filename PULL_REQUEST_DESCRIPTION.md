Title: Preserve unsafe negations in-section when sorting (Fix #29)

This PR implements logic to avoid moving unsafe negated patterns when sorting entries within the same section of a `.gitignore` file.

Why
- Sorting entries while preserving `.gitignore` semantics can be tricky when negated patterns and wildcards interact. Examples such as:

```
*csv
!*aut.csv
```

mean that swapping the two lines changes which files are ignored. The README currently warns about this case.

What changed
- Section._sort now:
  - classifies negated lines as "unsafe" (anchors) if they contain `**`, `?`, more than one `*`, or a single `*` where the suffix after the `*` contains `/` or further wildcards.
  - keeps unsafe negated lines at their original indices within a section.
  - sorts all other lines (removing leading `!` for comparison) and ensures non-negated lines come before their negated counterpart with the same base.
  - fills the non-anchor slots with the sorted movable lines left-to-right.

Tests
- Adds tests for:
  - preserving an unsafe negation such as `!c/**/` at its original position while sorting other lines around it.
  - ensuring a safe negation like `!path/to/*.csv` is movable and sorted where appropriate.

Related
- Fixes/addresses: https://github.com/lorenzwalthert/gitignore-tidy/issues/29
