import pytest


@pytest.fixture
def contents():
    return """\
    # secion1
    a
    b
    !a/b

    # section 55
    x
    *.pdf
    """
