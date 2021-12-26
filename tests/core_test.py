import os
import tempfile

from gitignore_tidy.core import _normalize
from gitignore_tidy.core import _sort_lines
from gitignore_tidy.core import _sort_lines_with_comments
from gitignore_tidy.core import tidy


def test__normalize():
    # no sorting
    assert _normalize(['x', 'a']) == ['x', 'a']

    # remove trailing blank
    assert _normalize(['x', 'a ']) == ['x', 'a']

    # remove duplicates
    assert _normalize(['x', 'a', 'a']) == ['x', 'a']

    # remove leading whitespace
    assert _normalize(['x', ' a']) == ['x', 'a']

    assert _normalize(['x', ' a'], allow_trailing_whitespace=True) == [
        'x', ' a',
    ]


def test__sort_lines():
    assert _sort_lines(['a', 'x', 'b']) == ['a', 'b', 'x']
    assert _sort_lines(['a', 'x', '!b/c', 'b']) == ['a', 'b', '!b/c', 'x']


def test__sort_lines_with_comments_basic():
    input = [
        '# section 1', 'a', 'x', 'b',
        '# section 2', 'z', 'e', '!e/f/*', '*.pdf',
    ]
    output = [
        '# section 1', 'a', 'b', 'x',
        '# section 2', '*.pdf', 'e', '!e/f/*', 'z',
    ]
    assert _sort_lines_with_comments(input) == output


def test__sort_lines_with_comments_blank_lines():
    input = [
        '# section 1', 'a', 'x', 'b', '',  '# section 2',
        'z', 'e', '!e/f/*', '*.pdf', '', '', '# more',
    ]
    output = [
        '# section 1', 'a', 'b', 'x', '',  '# section 2',
        '*.pdf', 'e', '!e/f/*', 'z', '', '# more',
    ]
    assert _sort_lines_with_comments(input) == output


def test_tidy():

    contents = """\
    # secion1
    a
    b
    !a/b

    # section 55
    x
    *.pdf
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        g1 = os.path.join(temp_dir, '.gitignore')
        with open(g1, 'w') as file:
            file.write(contents)

        dir2 = os.path.join(temp_dir, 'docs')
        os.mkdir(dir2)
        g2 = os.path.join(dir2, '.gitignore')
        with open(g2, 'w') as file:
            file.write(contents)

        tidy([g1, g2])
