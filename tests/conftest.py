import textwrap

import pytest


@pytest.fixture
def untidy_contents():
    return """\
    a
    b
    !a/b

    # section 55
    x
    *.pdf"""


@pytest.fixture
def tidy_contents():
    return textwrap.dedent(
        """\
    a
    !a/b
    b

    # section 55
    *.pdf
    x
    """,
    )
