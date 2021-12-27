from gitignore_tidy.core import _normalize
from gitignore_tidy.core import _sort_lines
from gitignore_tidy.core import _sort_lines_with_comments
from gitignore_tidy.core import _tidy_lines


def test__normalize():
    # no sorting
    assert _normalize(['x', 'a']) == ['x', 'a']

    # remove trailing blank
    assert _normalize(['x', 'a ']) == ['x', 'a']

    # remove duplicates
    assert _normalize(['x', 'a', 'a']) == ['x', 'a']

    # remove leading whitespace
    assert _normalize(['x', ' a']) == ['x', 'a']

    assert _normalize(['x', ' a'], allow_leading_whitespace=True) == [
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


def test__sort_lines_with_comments_without_root():
    input = [
        'a', 'x', 'b', '',  '# section 2',
        'z', 'e', '!e/f/*', '*.pdf', '', '', '# more',
    ]
    output = [
        'a', 'b', 'x', '',  '# section 2',
        '*.pdf', 'e', '!e/f/*', 'z', '', '# more',
    ]
    assert _sort_lines_with_comments(input) == output


def test__sort_lines_with_comments_with_leading_blank_lines():
    input = [
        '', '',  'a', 'x', 'b', '',  '# section 2',
        'z', 'e', '!e/f/*', '*.pdf', '', '', '# more',
    ]
    output = [
        'a', 'b', 'x', '',  '# section 2',
        '*.pdf', 'e', '!e/f/*', 'z', '', '# more',
    ]
    assert _sort_lines_with_comments(input) == output


def test__tidy_one_with_already_correctly_ordered():
    input = [
        'a', 'b', '', '', '', 'x', '',  '# section 2',
        '*.pdf', 'e', '!e/f/*', '', '', 'z', '', '# more', '',
    ]
    output = [
        'a', 'b', 'x', '',  '# section 2',
        '*.pdf', 'e', '!e/f/*', 'z', '', '# more',
    ]
    assert _tidy_lines(
        input, path='/path/to/file',
        allow_leading_whitespace=False,
    ) == output
