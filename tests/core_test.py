import pathlib
import tempfile

import pytest

from gitignore_tidy.core import GitIgnoreContents
from gitignore_tidy.core import NormalisedGitIgnoreContents
from gitignore_tidy.core import Section
from gitignore_tidy.core import Sections
from gitignore_tidy.core import SortedSection  # TODO how to import objects? Use * and __all__?
from gitignore_tidy.core import tidy_file
from gitignore_tidy.core import tidy_lines


def _create_section(header, input: list[str], trailing_blanks: int = 0, sorted: bool = False):
    constructor = SortedSection if sorted else Section
    return constructor(header, NormalisedGitIgnoreContents(input), trailing_blanks=trailing_blanks)


class TestGitIgnoreContents:

    def test_iter(self):
        it = ["a", "c", "1"]
        assert list(GitIgnoreContents(it)) == it

    @pytest.mark.parametrize(
        ("input", "expected_output", "allow_leading_whitespace"),
        (
            pytest.param(["x", "a"], ["x", "a"], False, id="standard"),
            pytest.param(["", "a"], ["", "a"], False, id="empty first"),
            pytest.param(["x", "a "], ["x", "a"], False, id="trailing blank"),
            pytest.param(["x", "a", "a"], ["x", "a"], False, id="duplicates"),
            pytest.param(["x", " a"], ["x", "a"], False, id="leading spaces"),
            pytest.param(["x", " a"], ["x", " a"], True, id="leading spaces allowed"),
        ),
    )
    def test_normalize(self, input, expected_output, allow_leading_whitespace):
        assert (
            GitIgnoreContents(input).normalize(allow_leading_whitespace=allow_leading_whitespace).lines
            == expected_output
        )

    def test_from_file(self, contents):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir, ".gitignore")
            with path.open("w") as file:
                file.write(contents)
            assert GitIgnoreContents.from_file(path) == GitIgnoreContents(contents.split("\n"))

    def test_to_file(self, contents):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir, ".gitignore")
            GitIgnoreContents(contents.split("\n")).to_file(path)
            with path.open("r") as f:
                lines = f.readlines()
        assert contents.split("\n") == [line.rstrip() for line in lines]


class TestNormalisedGitIgnoreContents:
    @pytest.mark.parametrize(
        ("input", "expected_output"),
        [
            (
                ["b", "a", "", "#", "q"],
                Sections(
                    (
                        Section(None, NormalisedGitIgnoreContents(["b", "a", ""])),
                        Section("#", NormalisedGitIgnoreContents(["q"]), trailing_blanks=1),
                    ),
                ),
            ),
            (
                ["# b", "a", "q"],  # if has spaces, it's not normalised
                Sections((Section("# b", NormalisedGitIgnoreContents(["a", "q"]), trailing_blanks=0),)),
            ),
        ],
    )
    def test_split(self, input, expected_output):
        assert NormalisedGitIgnoreContents(input).split() == expected_output


class TestSection:

    @pytest.mark.parametrize(
        ("input", "expected_output"),
        (
            pytest.param(
                ["a", "x", "b"],
                ["a", "b", "x"],
                id="no comment, no negation",
            ),
            pytest.param(
                ["a", "x", "!b/c", "b"],
                ["a", "b", "!b/c", "x"],
                id="no comment, negation",
            ),
        ),
    )
    def test_sort(self, input, expected_output):
        assert _create_section(None, input).sort() == _create_section(None, expected_output, sorted=True)

    @pytest.mark.parametrize(
        ("input", "expected_output"),
        (
            pytest.param(
                {"header": "# test", "lines": ["a", "x", "b"], "trailing_blanks": 0},
                ["# test", "a", "x", "b"],
                id="no trailing blanks",
            ),
            pytest.param(
                {"header": "# another", "lines": ["k", "b"], "trailing_blanks": 3},
                ["", "", "", "# another", "k", "b"],
                id="multiple trailing blanks",
            ),
        ),
    )
    def test_iter(self, input, expected_output):
        assert list(_create_section(input["header"], input["lines"], input["trailing_blanks"])) == expected_output


class TestSections:

    REPS: int = 2

    @classmethod
    def lines(cls):  # trade-off repetition and simple vs generic and harder to test / understand
        return ["# h1", "b", "c"]

    @classmethod
    def _sections_tuple(cls):  # TODO: underscore here and all other tests?
        return (_create_section(cls.lines()[0], cls.lines()[1:]),) * cls.REPS

    @classmethod
    def _sections(cls):
        return Sections(cls._sections_tuple())

    def test_iter(self):

        assert tuple(self._sections()) == self._sections_tuple()

    def test_as_contents(self):
        assert self._sections().as_contents() == NormalisedGitIgnoreContents(self.lines() * self.REPS)


class TestTidyLines:

    @pytest.mark.parametrize(
        ("input", "expected_output"),
        (
            pytest.param(
                [
                    "# section 1",
                    "a",
                    "x",
                    "b",
                    "# section 2",
                    "z",
                    "e",
                    "!e/f/*",
                    "*.pdf",
                ],
                [
                    "# section 1",
                    "a",
                    "b",
                    "x",
                    "# section 2",
                    "*.pdf",
                    "e",
                    "!e/f/*",
                    "z",
                ],
                id="comment, negation",
            ),
            pytest.param(
                [
                    "# section 1",
                    "a",
                    "x",
                    "b",
                    "",
                    "# section 2",
                    "z",
                    "e",
                    "!e/f/*",
                    "*.pdf",
                    "",
                    "",
                    "# more",
                ],
                [
                    "# section 1",
                    "a",
                    "b",
                    "x",
                    "",
                    "# section 2",
                    "*.pdf",
                    "e",
                    "!e/f/*",
                    "z",
                    "",
                    "# more",
                ],
                id="comment, blank line, negation",
            ),
            pytest.param(
                [
                    "a",
                    "x",
                    "b",
                    "",
                    "# section 2",
                    "z",
                    "e",
                    "!e/f/*",
                    "*.pdf",
                    "",
                    "",
                    "# more",
                ],
                [
                    "a",
                    "b",
                    "x",
                    "",
                    "# section 2",
                    "*.pdf",
                    "e",
                    "!e/f/*",
                    "z",
                    "",
                    "# more",
                ],
                id="comment, no root",
            ),
            pytest.param(
                [
                    "",
                    "",
                    "a",
                    "x",
                    "b",
                    "",
                    "# section 2",
                    "z",
                    "e",
                    "!e/f/*",
                    "*.pdf",
                    "",
                    "",
                    "# more",
                ],
                [
                    "a",
                    "b",
                    "x",
                    "",
                    "# section 2",
                    "*.pdf",
                    "e",
                    "!e/f/*",
                    "z",
                    "",
                    "# more",
                ],
                id="comments, blank lines",
            ),
            pytest.param(
                [
                    "a",
                    "b",
                    "",
                    "",
                    "",
                    "x",
                    "",
                    "# section 2",
                    "*.pdf",
                    "e",
                    "!e/f/*",
                    "",
                    "",
                    "z",
                    "",
                    "# more",
                    "",
                ],
                [
                    "a",
                    "b",
                    "x",
                    "",
                    "# section 2",
                    "*.pdf",
                    "e",
                    "!e/f/*",
                    "z",
                    "",
                    "# more",
                ],
                id="already ordered",
            ),
        ),
    )
    def test__sort_lines_with_comments(self, input, expected_output):
        assert list(tidy_lines(GitIgnoreContents(input), allow_leading_whitespace=False)) == expected_output


class TestTidyFile:

    def test_tidy_file(self, contents, tidy_contents):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir, ".gitignore")
            with path.open("w") as file:
                file.write(contents)

            tidy_file(path)

            with path.open("r") as file:
                output = file.read()

        assert output == tidy_contents
