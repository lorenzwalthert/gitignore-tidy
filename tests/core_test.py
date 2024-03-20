import pytest

from gitignore_tidy.core import _normalize
from gitignore_tidy.core import _sort_lines
from gitignore_tidy.core import _sort_lines_with_comments
from gitignore_tidy.core import _tidy_lines


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        pytest.param(["x", "a"], ["x", "a"], id="no sorting"),
        pytest.param(["x", "a "], ["x", "a"], id="trailing blank"),
        pytest.param(["x", "a", "a"], ["x", "a"], id="duplicates"),
        pytest.param(["x", " a"], ["x", "a"], id="leading spaces"),
    ),
)
def test__normalize_without_leading_whitespace(input, expected_output):
    assert _normalize(input) == expected_output


def test__normalize_with_leading_whitespace():
    assert _normalize(["x", " a"], allow_leading_whitespace=True) == [
        "x",
        " a",
    ]


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
def test__sort_lines(input, expected_output):
    assert _sort_lines(input) == expected_output


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
    ),
)
def test__sort_lines_with_comments(input, expected_output):
    assert _sort_lines_with_comments(input) == expected_output


def test__tidy_one_with_already_correctly_ordered():
    input = [
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
    ]
    output = [
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
    ]
    assert (
        _tidy_lines(
            input,
            allow_leading_whitespace=False,
        )
        == output
    )
