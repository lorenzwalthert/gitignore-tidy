import os
import re
import tempfile

import pytest
from typer.testing import CliRunner

from gitignore_tidy.cli import app

runner = CliRunner()


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


def test_cli(contents):

    with tempfile.TemporaryDirectory() as temp_dir:
        g1 = os.path.join(temp_dir, ".gitignore")
        with open(g1, "w") as file:
            file.write(contents)

        dir2 = os.path.join(temp_dir, "docs")
        os.mkdir(dir2)
        g2 = os.path.join(dir2, ".gitignore")
        with open(g2, "w") as file:
            file.write(contents)

        result = runner.invoke(app, [g1, g2])
        assert result.exit_code == 0
        assert re.search(
            f"^Successfully written {g1}\\.\nSuccessfully written {g2}",
            result.stdout,
        )

        result = runner.invoke(app, [g1])
        assert result.exit_code == 0
        # assert re.search('already' in result.stdout
        assert re.search(f"^{g1} already tidy.\n$", result.stdout)
        # second file is processed when first file is ok
        with open(g2, "w") as file:
            file.write(contents)

        result = runner.invoke(app, [g1, g2])
        assert re.search(
            f"^{g1} already tidy\\.\nSuccessfully written {g2}.\n$",
            result.stdout,
        )
