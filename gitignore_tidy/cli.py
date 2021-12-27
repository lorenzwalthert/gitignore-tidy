from pathlib import Path
from typing import Optional

import typer


def main(
    name: Optional[Path] = typer.Argument(None),
    allow_leading_whitespace: bool = typer.Option(
        False,
        help='Whether or not to allow trailing whitespaces in file names',
    ),
):
    if name is None:
        print(f'Hello {name}')
    else:
        typer.echo('Hello World!')


if __name__ == '__main__':
    typer.run(main)
