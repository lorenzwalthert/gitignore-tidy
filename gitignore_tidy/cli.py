import pathlib
import typing

import typer

from gitignore_tidy.core import tidy_file


app = typer.Typer()


@app.command()
def tidy_files(
    files: typing.Optional[list[pathlib.Path]] = typer.Argument(
        None,
        help="""\
        Paths to one or more gitignore files.
        If not supplied, the .gitignore in the current
        working directory will be assumed.
        """,
    ),
    allow_leading_whitespace: bool = typer.Option(
        False,
        help="Whether or not to allow trailing whitespaces in file names",
    ),
):
    """
    Tidy .gitignore files
    """
    if files is None or len(files) < 1:
        files = [pathlib.Path(".gitignore")]
    [tidy_file(file, allow_leading_whitespace=allow_leading_whitespace) for file in files]
