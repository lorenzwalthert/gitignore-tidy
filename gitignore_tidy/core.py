from __future__ import annotations

import collections.abc
import dataclasses
import enum
import itertools
import pathlib
import re
import sys
import typing
from functools import cached_property

from gitignore_tidy.logging import logger

if sys.version_info >= (3, 11):
    from enum import StrEnum
    from typing import Self  # noqa: F401
else:
    from typing_extensions import Self

    class StrEnum(str, enum.Enum):
        """Minimal backport of :class:`enum.StrEnum` for Python < 3.11."""

        __str__ = str.__str__

        def _generate_next_value_(name, start, count, last_values):  # noqa: N805
            return name.lower()


class NegationsLast(StrEnum):
    """Where to place negating (``!``) entries when sorting."""

    GROUP = enum.auto()
    EOF = enum.auto()


def tidy_file(
    path: pathlib.Path,
    *,
    allow_leading_whitespace: bool = False,
    negations_last: NegationsLast | None = None,
) -> None:
    lines = PlainLines.from_file(path)
    if len(lines) < 1:
        logger.info("File %s is empty, not writing.", path)
        return

    tidy_plain_lines = tidy_lines(
        lines,
        allow_leading_whitespace=allow_leading_whitespace,
        negations_last=negations_last,
    )
    if lines.lines == tidy_plain_lines.lines:
        logger.info("%s already tidy.", path)  # TODO use logger module
    else:
        tidy_plain_lines.to_file(path)
        logger.info("Successfully written %s.", path)


def tidy_lines(
    lines: PlainLines,
    allow_leading_whitespace: bool,
    negations_last: NegationsLast | None = None,
) -> PlainLines:
    normalised_contents = lines.normalize(allow_leading_whitespace=allow_leading_whitespace)
    sections = normalised_contents.split()
    if negations_last is NegationsLast.EOF:
        return sections.with_negations_at_eof().as_plain()
    sorted_sections = Sections(
        tuple(section.sort(negations_last=negations_last) for section in sections),
    )
    return sorted_sections.as_plain()


def _is_negation(line: str) -> bool:
    return line.startswith("!")


@dataclasses.dataclass(frozen=True)
class PlainLines:
    """
    Flat representation of a `.gitignore` file or parts of it
    """

    _leading_pattern: typing.ClassVar[re.Pattern] = re.compile("^(!)? *\t*")
    _trailing_pattern: typing.ClassVar[re.Pattern] = re.compile(" *\t*$")

    lines: collections.abc.Sequence[str]

    normalised: bool = False
    sorted: bool = False

    @classmethod
    def from_file(cls, path: pathlib.Path) -> Self:

        with path.open("r") as f:
            lines = f.read().splitlines()

        return cls(lines, normalised=False, sorted=False)

    def to_file(self, path: pathlib.Path) -> None:
        with path.open("w") as f:
            f.writelines(line + "\n" for line in self.lines)

    def normalize(self, allow_leading_whitespace: bool = False) -> Self:
        if allow_leading_whitespace:
            lines = self.lines
        else:
            lines = (re.sub(self._leading_pattern, "\\1", line) for line in self.lines)
        lines = (re.sub(self._trailing_pattern, "", line) for line in lines)
        unique = []

        for line in lines:
            if line not in unique or line == "":
                unique.append(line)
        return dataclasses.replace(self, lines=unique, normalised=True, sorted=self.sorted)

    def __iter__(self) -> collections.abc.Iterator[str]:
        return iter(self.lines)

    def __len__(self) -> int:
        return len(self.lines)

    def split(self) -> Sections:
        if not self.normalised:
            raise AssertionError("`PlainLines` must be normalised before splitting is possible.")

        lines = self.lines
        sections = dict()
        current_section = None
        for idx, line in enumerate(lines):
            if line.startswith("#"):
                sections[line] = dict(values=[])
                current_section = line
                if idx > 0 and lines[idx - 1] == "":
                    sections[current_section]["trailing_blanks"] = 1
                else:
                    sections[current_section]["trailing_blanks"] = 0
            elif idx == 0:  # first line has no comment
                sections[current_section] = dict(
                    values=[line],
                    trailing_blanks=0,
                )

            else:
                sections[current_section]["values"].append(line)

        sections = (
            Section(
                header,
                PlainLines(content["values"], normalised=self.normalised, sorted=False),
                content["trailing_blanks"],
            )
            for header, content in sections.items()
        )
        return Sections(tuple(sections))


@dataclasses.dataclass(frozen=True)
class Section:
    """
    One part of a normalised content of a `.gitignore` file, with header and
    trailing blanks parsed.
    """

    header: str | None
    lines: PlainLines
    trailing_blanks: int = 0

    def __post_init__(self):
        assert self.normalised, "Sections can't be initiated without normalised `PlainLines`."

    @cached_property
    def normalised(self) -> bool:
        return self.lines.normalised

    @cached_property
    def sorted(self) -> bool:
        return self.lines.sorted

    def sort(self, *, negations_last: NegationsLast | None = None) -> Section:
        sorter = self._sort_grouped if negations_last is NegationsLast.GROUP else self._sort
        return Section(
            self.header,
            PlainLines(sorter(self.lines.lines), normalised=True, sorted=True),
            self.trailing_blanks,
        )

    def _materialized_trailing_blanks(self) -> tuple[str, ...]:
        return tuple([""] * self.trailing_blanks)

    def __iter__(self) -> collections.abc.Iterator[str]:
        elements = list(filter(None, [self.header, *self.lines.lines]))
        if self.trailing_blanks > 0:
            [elements.insert(0, blank) for blank in self._materialized_trailing_blanks()]
        return iter(elements)

    @staticmethod
    def _sort(lines: collections.abc.Sequence[str]) -> tuple[str, ...]:
        """
        Sort entries while never changing the meaning of the ``.gitignore``.

        Every negating entry (leading ``!``) stays exactly where it is; only the
        runs of non-negating entries between two negations are sorted. Reordering
        non-negating entries among themselves can never change which paths are
        ignored, so this is always safe.
        """
        result: list[str] = []
        run: list[str] = []
        for line in lines:
            if _is_negation(line):
                result.extend(sorted(run))
                result.append(line)
                run = []
            else:
                run.append(line)
        result.extend(sorted(run))
        return tuple(result)

    @staticmethod
    def _sort_grouped(lines: collections.abc.Sequence[str]) -> tuple[str, ...]:
        """
        Sort non-negating entries first, then all negating entries.

        This moves negations relative to other entries, which *can* change the
        meaning of the ``.gitignore``; it is only used when explicitly requested.
        """
        non_negated = sorted(line for line in lines if not _is_negation(line))
        negated = sorted(line for line in lines if _is_negation(line))
        return tuple(non_negated + negated)


@dataclasses.dataclass(frozen=True)
class Sections:
    """
    The `.gitignore` file, represented as a collection of sections.
    """

    sections: collections.abc.Sequence[Section]

    @cached_property
    def sorted(self) -> bool:
        return all(section.sorted for section in self)

    @cached_property
    def normalised(self) -> bool:
        return all(section.normalised for section in self)

    def __iter__(self) -> collections.abc.Iterator[Section]:
        return iter(self.sections)

    def as_plain(self) -> PlainLines:
        lines = list(itertools.chain(*(list(section) for section in self)))
        return PlainLines(lines, normalised=self.normalised, sorted=self.sorted)

    def with_negations_at_eof(self) -> Sections:
        """
        Collect every negating entry (leading ``!``) into a single sorted block
        in a new section after the last one.

        This moves negations relative to other entries, which *can* change the
        meaning of the ``.gitignore``; it is only used when explicitly requested.
        """
        stripped: list[Section] = []
        collected_negations: list[str] = []
        for section in self:
            kept = [line for line in section.lines.lines if not _is_negation(line)]
            collected_negations.extend(line for line in section.lines.lines if _is_negation(line))
            stripped.append(
                Section(
                    section.header,
                    PlainLines(tuple(sorted(kept)), normalised=True, sorted=True),
                    section.trailing_blanks,
                ),
            )
        if collected_negations:
            stripped.append(
                Section(
                    None,
                    PlainLines(tuple(sorted(collected_negations)), normalised=True, sorted=True),
                    trailing_blanks=1,
                ),
            )
        return Sections(tuple(stripped))
