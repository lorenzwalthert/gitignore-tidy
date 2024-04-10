import dataclasses
import itertools
import pathlib
import re
import typing

from gitignore_tidy.logging import logger


def tidy_file(path: pathlib.Path, *, allow_leading_whitespace: bool = False):
    lines = GitIgnoreContents.from_file(path)
    if len(lines) < 1:
        logger.fatal(f"File {path} is empty, not writing.")
        return

    sorted_contents = tidy_lines(lines, allow_leading_whitespace=allow_leading_whitespace)
    if lines.lines == sorted_contents.lines:
        logger.fatal(f"{path} already tidy.")  # TODO use logger module
    else:
        sorted_contents.to_file(path)
        logger.fatal(f"Successfully written {path}.")


def tidy_lines(lines: "GitIgnoreContents", allow_leading_whitespace: bool) -> "NormalisedGitIgnoreContents":
    normalised_contents = lines.normalize(allow_leading_whitespace=allow_leading_whitespace)
    sorted_sections = SortedSections(tuple(section.sort() for section in normalised_contents.split()))
    return sorted_sections.as_contents()


@dataclasses.dataclass(frozen=True)
class GitIgnoreContents:
    normalised: typing.ClassVar[bool] = False
    sorted: typing.ClassVar[bool] = False

    lines: list[str]
    """
    Represents all contents of a `.gitignore` file.
    """

    @classmethod
    def from_file(cls, path: pathlib.Path) -> typing.Self:
        if not path.exists():
            raise FileNotFoundError(f"{path} not found.")

        with path.open("r") as f:
            lines = f.read().splitlines()

        return cls(lines)

    def to_file(self, path: pathlib.Path):
        with path.open("w") as f:
            f.writelines([line + "\n" for line in self.lines])

    def normalize(self, allow_leading_whitespace: bool = False) -> "NormalisedGitIgnoreContents":
        lines = self.lines
        if not allow_leading_whitespace:
            lines = [re.sub("^(!)? *\t*", "\\1", line) for line in lines]
        lines = [re.sub(" *\t*$", "", line) for line in lines]
        unique = []

        for line in lines:
            if line not in unique or line == "":
                unique.append(line)
        return NormalisedGitIgnoreContents(unique)

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self.lines)

    def __len__(self) -> int:
        return len(self.lines)


class NormalisedGitIgnoreContents(GitIgnoreContents):
    """
    Represents a polished `.gitignore` file, i.e. with only unique entries, trailing
    (and potentially leading) spaces removed.
    """

    normalised: typing.ClassVar[bool] = True

    def split(self) -> "Sections":
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
            Section(header, NormalisedGitIgnoreContents(content["values"]), content["trailing_blanks"])
            for header, content in sections.items()
        )
        return Sections(tuple(sections))


@dataclasses.dataclass(frozen=True)
class Section:
    """
    One part of a normalised content of a `.gitignore` file
    """

    header: str | None
    lines: NormalisedGitIgnoreContents
    trailing_blanks: int = 0

    def sort(self):
        return SortedSection(
            self.header,
            NormalisedGitIgnoreContents(self._sort(self.lines.lines)),
            self.trailing_blanks,
        )

    def _materialized_trailing_blanks(self) -> list[str]:
        return [""] * self.trailing_blanks

    def __iter__(self):
        elements = list(filter(None, [self.header, *self.lines.lines]))
        if self.trailing_blanks > 0:
            [elements.insert(0, blank) for blank in self._materialized_trailing_blanks()]
        return iter(elements)

    @staticmethod
    def _sort(lines: list[str]) -> list[str]:
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

    def __iter__(self) -> typing.Iterator[Section]:
        return iter(self.sections)

    def as_contents(self) -> NormalisedGitIgnoreContents:
        lines = list(itertools.chain(*(list(section) for section in self)))
        return NormalisedGitIgnoreContents(lines)


@dataclasses.dataclass(frozen=True)
class SortedSections(Sections):
    sorted: typing.ClassVar[bool] = True


@dataclasses.dataclass(frozen=True)
class SortedSection(Section):
    sorted: typing.ClassVar[bool] = True
