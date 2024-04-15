from __future__ import annotations

import collections.abc
import dataclasses
import itertools
import pathlib
import re
import sys
import typing
from functools import cached_property

from gitignore_tidy.logging import logger

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self  # noqa: F401


def tidy_file(path: pathlib.Path, *, allow_leading_whitespace: bool = False):
    lines = PlainLines.from_file(path)
    if len(lines) < 1:
        logger.info(f"File {path} is empty, not writing.")
        return

    tidy_plain_lines = tidy_lines(lines, allow_leading_whitespace=allow_leading_whitespace)
    if lines.lines == tidy_plain_lines.lines:
        logger.info(f"{path} already tidy.")  # TODO use logger module
    else:
        tidy_plain_lines.to_file(path)
        logger.info(f"Successfully written {path}.")


def tidy_lines(lines: PlainLines, allow_leading_whitespace: bool) -> PlainLines:
    normalised_contents = lines.normalize(allow_leading_whitespace=allow_leading_whitespace)
    sorted_sections = Sections(tuple(section.sort() for section in normalised_contents.split()))
    return sorted_sections.as_plain()


@dataclasses.dataclass(frozen=True)
class PlainLines:
    """
    Flat representation of a `.gitignore` file or parts of it
    """

    lines: collections.abc.Sequence[str]

    normalised: bool = False
    sorted: bool = False

    @classmethod
    def from_file(cls, path: pathlib.Path) -> PlainLines:

        with path.open("r") as f:
            lines = f.read().splitlines()

        return cls(lines, normalised=False, sorted=False)

    def to_file(self, path: pathlib.Path):
        with path.open("w") as f:
            f.writelines([line + "\n" for line in self.lines])

    def normalize(self, allow_leading_whitespace: bool = False) -> PlainLines:
        lines = self.lines
        if not allow_leading_whitespace:
            lines = [re.sub("^(!)? *\t*", "\\1", line) for line in lines]
        lines = [re.sub(" *\t*$", "", line) for line in lines]
        unique = []

        for line in lines:
            if line not in unique or line == "":
                unique.append(line)
        return PlainLines(unique, normalised=True, sorted=self.sorted)

    def __iter__(self) -> typing.Iterator[str]:
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
    def normalised(self):
        return self.lines.normalised

    @cached_property
    def sorted(self):
        return self.lines.sorted

    def sort(self) -> Section:
        return Section(
            self.header,
            PlainLines(self._sort(self.lines.lines), normalised=True, sorted=True),
            self.trailing_blanks,
        )

    def _materialized_trailing_blanks(self) -> list[typing.Literal[""]]:
        return [""] * self.trailing_blanks

    def __iter__(self):
        elements = list(filter(None, [self.header, *self.lines.lines]))
        if self.trailing_blanks > 0:
            [elements.insert(0, blank) for blank in self._materialized_trailing_blanks()]
        return iter(elements)

    @staticmethod
    def _sort(lines: collections.abc.Sequence[str]) -> list[str]:
        original = lines
        non_negated = [re.sub("^!", "", line) for line in lines]
        sorted_non_negated = sorted(non_negated)
        sorted_negated = []
        for line in sorted_non_negated:
            negated_cand = "!" + line
            if negated_cand in original:
                sorted_negated.append(negated_cand)
            else:
                sorted_negated.append(line)

        return sorted_negated


@dataclasses.dataclass(frozen=True)
class Sections:
    """
    The `.gitignore` file, represented as a collection of sections.
    """

    sections: tuple[Section, ...]

    @cached_property
    def sorted(self):
        return all(section.sorted for section in self)

    @cached_property
    def normalised(self):
        return all(section.normalised for section in self)

    def __iter__(self) -> typing.Iterator[Section]:
        return iter(self.sections)

    def as_plain(self) -> PlainLines:
        lines = list(itertools.chain(*(list(section) for section in self)))
        return PlainLines(lines, normalised=self.normalised, sorted=self.sorted)
