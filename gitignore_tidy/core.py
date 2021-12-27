import os
import re
from pathlib import Path
from typing import List
from typing import Optional

import typer
app = typer.Typer()


def _normalize(lines, allow_leading_whitespace=False):
    if not allow_leading_whitespace:
        lines = [re.sub('^(!)? *\t*', '\\1', line) for line in lines]
    lines = [re.sub(' *\t*$', '', line) for line in lines]
    unique = []
    for line in lines:
        if line not in unique or line == '':
            unique.append(line)
    return unique


def _sort_lines(lines):
    original = lines
    non_negated = [re.sub('^!', '', line) for line in lines]
    sorted_non_negated = sorted(non_negated)
    sorted_negated = []
    for line in sorted_non_negated:
        negated_cand = ('!' + line)
        if negated_cand in original:
            sorted_negated.append(negated_cand)
        else:
            sorted_negated.append(line)

    return sorted_negated


def _sections_sort(sections):
    lines_out = []

    for section_title, section_content in sections.items():

        if section_content['trailing_blanks'] > 0:
            lines_out.append('')

        if section_title.startswith('#'):
            lines_out.append(section_title)

        for line in _sort_lines(section_content['values']):
            if line != '':
                lines_out.append(line)

    return lines_out


def _sections_split(lines):
    sections = dict()
    current_section = 'root'
    for idx, line in enumerate(lines):
        if line.startswith('#'):
            sections[line] = dict(values=[])
            current_section = line
            if idx > 0 and lines[idx - 1] == '':
                sections[current_section]['trailing_blanks'] = 1
            else:
                sections[current_section]['trailing_blanks'] = 0
        elif idx == 0:  # first line has no comment
            sections[current_section] = dict(
                values=[line], trailing_blanks=0,
            )

        else:
            sections[current_section]['values'].append(line)
    return sections


def _sort_lines_with_comments(lines):
    sections = _sections_split(lines)
    lines_out = _sections_sort(sections)
    return lines_out


def _tidy_file(path, *, allow_leading_whitespace=False):
    if not os.path.exists(path):
        raise FileNotFoundError(f'{path} not found.')

    with open(path) as f:
        lines = f.read().splitlines()

    if len(lines) < 1:
        typer.echo(f'{path} is empty.')
        return

    sorted_lines = _tidy_lines(
        lines,
        path=path,
        allow_leading_whitespace=allow_leading_whitespace,
    )
    with open(path, 'w') as f:
        f.writelines([line + '\n' for line in sorted_lines])
        typer.echo(f'Successfully written {path}.')


def _tidy_lines(lines, *, path, allow_leading_whitespace):
    lines = _normalize(
        lines,
        allow_leading_whitespace=allow_leading_whitespace,
    )

    sorted_lines = _sort_lines_with_comments(lines)
    if sorted_lines == lines:
        typer.echo(f'{path} already tidy.')
        typer.Exit()

    return sorted_lines


@app.command()
def tidy_files(
    files: Optional[List[Path]] = typer.Argument(
        None,
        help="""\
        Paths to one or more gitignore files.
        If not supplied, the .gitignore in the current
        working directory will be assumed.
        """,
    ),
    allow_leading_whitespace: bool = typer.Option(
        False,
        help='Whether or not to allow trailing whitespaces in file names',
    ),

):
    """
    Tidy .gitignore files
    """
    if files is None or len(files) < 1:
        files = [Path('.gitignore')]
    [
        _tidy_file(file, allow_leading_whitespace=allow_leading_whitespace)
        for file in files
    ]
